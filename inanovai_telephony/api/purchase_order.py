import frappe


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
