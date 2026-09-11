import frappe
from frappe import _


@frappe.whitelist()
def get_supplier_phone(supplier):
    if not supplier:
        return {"phone": None}

    # First check direct Supplier phone fields if available.
    if frappe.db.has_column("Supplier", "mobile_no"):
        phone = frappe.db.get_value("Supplier", supplier, "mobile_no")
        if phone:
            return {"phone": phone}

    if frappe.db.has_column("Supplier", "phone"):
        phone = frappe.db.get_value("Supplier", supplier, "phone")
        if phone:
            return {"phone": phone}

    # Otherwise find a Contact linked to this Supplier.
    contacts = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Supplier",
            "link_name": supplier,
            "parenttype": "Contact",
        },
        pluck="parent",
    )

    for contact in contacts:
        phones = frappe.get_all(
            "Contact Phone",
            filters={"parent": contact},
            fields=["phone", "is_primary_mobile_no", "is_primary_phone"],
            order_by="idx asc",
        )

        for row in phones:
            if row.is_primary_mobile_no and row.phone:
                return {"phone": row.phone}

        for row in phones:
            if row.is_primary_phone and row.phone:
                return {"phone": row.phone}

        for row in phones:
            if row.phone:
                return {"phone": row.phone}

    return {"phone": None}


def send_submission_sms(doc, method=None):
    """Best-effort supplier notification on Purchase Order submit.
    Any failure here is logged and swallowed — it must never block submit."""
    try:
        phone = get_supplier_phone(doc.supplier).get("phone")

        if not phone:
            frappe.log_error(
                title="Purchase Order submission SMS skipped",
                message=f"No phone number on file for supplier {doc.supplier} (Purchase Order {doc.name}).",
            )
            return

        message = _(
            "Purchase Order {0} has been submitted. Please review and confirm."
        ).format(doc.name)

        from telephony.twilio.sms import send_sms

        send_sms(to=phone, message=message)
    except Exception:
        frappe.log_error(
            title="Purchase Order submission SMS failed",
            message=frappe.get_traceback(),
        )
