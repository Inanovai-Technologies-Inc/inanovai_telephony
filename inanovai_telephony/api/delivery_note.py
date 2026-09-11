import frappe
from frappe import _


def send_delivery_sms(doc, method=None):
    """Best-effort customer notification on Delivery Note submit.
    Any failure here is logged and swallowed — it must never block submit."""
    try:
        phone = doc.contact_mobile

        if not phone:
            frappe.log_error(
                title="Delivery Note submission SMS skipped",
                message=f"No contact mobile number on file for customer {doc.customer} (Delivery Note {doc.name}).",
            )
            return

        message = _(
            "Your order has been shipped. Delivery Note {0} has been created."
        ).format(doc.name)

        from telephony.twilio.sms import send_sms

        send_sms(to=phone, message=message)
    except Exception:
        frappe.log_error(
            title="Delivery Note submission SMS failed",
            message=frappe.get_traceback(),
        )
