import frappe
from frappe import _
from twilio.twiml.voice_response import Gather, VoiceResponse
from werkzeug.wrappers import Response

from telephony.twilio.api import create_call_log
from telephony.twilio.twilio_handler import IncomingCall, Twilio, TwilioCallDetails
from telephony.twilio.utils import get_public_url

GREETING = "Welcome to Inanovai. Press 1 for Sales. Press 2 for Support. Press 3 for Accounts."
INVALID_INPUT = "Sorry, that is not a valid option. Please press 1 for Sales, 2 for Support, or 3 for Accounts."
NO_INPUT = "Sorry, we did not receive your selection. Please press 1 for Sales, 2 for Support, or 3 for Accounts."
GOODBYE = "We're unable to connect your call right now. Goodbye."

# digit -> (Telephony IVR Settings fieldname, display label)
MENU = {
    "1": ("sales_number", "Sales"),
    "2": ("support_number", "Support"),
    "3": ("accounts_number", "Accounts"),
}

MENU_ACTION_PATH = "/api/method/inanovai_telephony.api.ivr.handle_menu_selection"


def get_ivr_settings():
    return frappe.get_cached_doc("Telephony IVR Settings")


def _gather_response(prompt, attempt):
    resp = VoiceResponse()
    gather = Gather(
        num_digits=1,
        timeout=8,
        action=f"{get_public_url(MENU_ACTION_PATH)}?attempt={attempt}",
        method="POST",
    )
    gather.say(_(prompt))
    resp.append(gather)
    return resp


def _fallback_response(settings, from_number):
    """Used once max_attempts is exhausted, or a selected department has no
    number configured. Reuses the same dial-with-recording helper as a normal
    selection, so a fallback transfer is logged/recorded identically."""
    if settings.fallback_number:
        twilio = Twilio.connect()
        return twilio.generate_twilio_dial_response(from_number, settings.fallback_number)

    resp = VoiceResponse()
    resp.say(_(GOODBYE))
    resp.hangup()
    return resp


@frappe.whitelist(allow_guest=True)
def incoming_call(**kwargs):
    """Voice webhook for the Twilio phone number's own 'A call comes in' setting.

    Logs the call exactly as the existing twilio_incoming_call_handler does,
    then either serves the IVR menu (if enabled) or falls back to the existing
    single-agent routing in IncomingCall.process() — unchanged behavior when
    IVR is turned off.
    """
    args = frappe._dict(kwargs)

    call_details = TwilioCallDetails(args)
    create_call_log(call_details)

    settings = get_ivr_settings()

    if not settings.enabled:
        resp = IncomingCall(args.From, args.To).process()
        return Response(resp.to_xml(), mimetype="text/xml")

    resp = _gather_response(GREETING, attempt=1)
    return Response(resp.to_xml(), mimetype="text/xml")


@frappe.whitelist(allow_guest=True)
def handle_menu_selection(**kwargs):
    """<Gather>'s action callback. Routes on 1/2/3, re-prompts on invalid or
    empty input (up to settings.max_attempts), then falls back."""
    args = frappe._dict(kwargs)
    digit = (args.get("Digits") or "").strip()
    attempt = frappe.utils.cint(args.get("attempt")) or 1
    call_sid = args.get("CallSid")
    from_number = args.get("From")

    settings = get_ivr_settings()

    if digit in MENU:
        field, label = MENU[digit]
        destination = (settings.get(field) or "").strip()

        if call_sid and frappe.db.exists("TP Call Log", call_sid):
            frappe.get_doc("TP Call Log", call_sid).add_comment(
                "Comment", _("IVR Selection: {0}").format(_(label))
            )

        if not destination:
            resp = _fallback_response(settings, from_number)
            return Response(resp.to_xml(), mimetype="text/xml")

        twilio = Twilio.connect()
        resp = twilio.generate_twilio_dial_response(from_number, destination)
        return Response(resp.to_xml(), mimetype="text/xml")

    max_attempts = settings.max_attempts or 3

    if attempt >= max_attempts:
        resp = _fallback_response(settings, from_number)
        return Response(resp.to_xml(), mimetype="text/xml")

    prompt = NO_INPUT if not digit else INVALID_INPUT
    resp = _gather_response(prompt, attempt=attempt + 1)
    return Response(resp.to_xml(), mimetype="text/xml")
