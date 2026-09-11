import frappe
from frappe import _

from inanovai_telephony.api.purchase_order import get_supplier_phone


def send_receipt_sms(doc, method=None):
    """Best-effort supplier notification on Purchase Receipt submit.
    Any failure here is logged and swallowed — it must never block submit."""
    try:
        phone = get_supplier_phone(doc.supplier).get("phone")

        if not phone:
            frappe.log_error(
                title="Purchase Receipt submission SMS skipped",
                message=f"No phone number on file for supplier {doc.supplier} (Purchase Receipt {doc.name}).",
            )
            return

        purchase_orders = list(
            dict.fromkeys(row.purchase_order for row in doc.items if row.purchase_order)
        )

        if len(purchase_orders) == 1:
            message = _(
                "Goods for Purchase Order {0} have been received (Receipt {1})."
            ).format(purchase_orders[0], doc.name)
        elif purchase_orders:
            message = _(
                "Goods for Purchase Orders {0} have been received (Receipt {1})."
            ).format(", ".join(purchase_orders), doc.name)
        else:
            message = _("Goods have been received (Receipt {0}).").format(doc.name)

        from telephony.twilio.sms import send_sms

        send_sms(to=phone, message=message)
    except Exception:
        frappe.log_error(
            title="Purchase Receipt submission SMS failed",
            message=frappe.get_traceback(),
        )
