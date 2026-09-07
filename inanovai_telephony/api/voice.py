import frappe
from frappe import _
from werkzeug.wrappers import Response
from twilio.twiml.voice_response import Dial, VoiceResponse

from crm.integrations.twilio.api import (
    create_call_log,
    validate_twilio_request,
)
from crm.integrations.twilio.twilio_handler import TwilioCallDetails, Twilio
from crm.integrations.twilio.utils import get_public_url


@frappe.whitelist(allow_guest=True)
def voice(**kwargs):
    """Generate CRM outbound TwiML using the automatic recording configuration."""

    args = frappe._dict(kwargs)
    twilio = validate_twilio_request(args, require_application_sid=True)

    def get_caller_number(caller):
        identity = caller.replace("client:", "").strip()
        user = Twilio.emailid_from_identity(identity)
        return frappe.db.get_value(
            "CRM Telephony Agent",
            user,
            "twilio_number",
        )

    from_number = get_caller_number(args.Caller)

    if not from_number:
        resp = VoiceResponse()
        resp.say(
            _("Your account is not configured with a phone number. Please contact your administrator.")
        )
        return Response(resp.to_xml(), mimetype="text/xml")

    try:
        call_details = TwilioCallDetails(args, call_from=from_number)
        create_call_log(call_details)
    except Exception:
        frappe.db.rollback()
        frappe.log_error(title="Error while creating Twilio call log")
        frappe.db.commit()

        resp = VoiceResponse()
        resp.say(_("We're unable to connect your call right now. Please try again later."))
        return Response(resp.to_xml(), mimetype="text/xml")

    recording_configuration_id = frappe.conf.get(
        "twilio_recording_configuration"
    )

    if not recording_configuration_id:
        frappe.throw(
            _("Twilio recording configuration is not configured.")
        )

    resp = VoiceResponse()

    dial = Dial(
        caller_id=from_number,
        record="record-from-answer",
        recording_configuration_id=recording_configuration_id,
    )

    dial.number(
        args.To,
        status_callback_event="initiated ringing answered completed",
        status_callback=get_public_url(
            "/api/method/crm.integrations.twilio.api.update_call_status_info"
        ),
        status_callback_method="POST",
    )

    resp.append(dial)

    return Response(resp.to_xml(), mimetype="text/xml")
