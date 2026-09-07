import frappe
from frappe import _


@frappe.whitelist(allow_guest=True, methods=["POST"])
def incoming_sms():
    """Receive an incoming SMS from Twilio and log it."""
    from_number = frappe.form_dict.get("From")
    to_number = frappe.form_dict.get("To")
    message = frappe.form_dict.get("Body")
    sid = frappe.form_dict.get("MessageSid")

    if not from_number or not to_number:
        frappe.throw(_("Invalid incoming SMS request."))

    from telephony.twilio.sms import create_sms_log

    create_sms_log(
        from_number,
        to_number,
        message or "",
        "General",
        "Delivered",
        sid=sid,
    )

    return "<Response></Response>"
