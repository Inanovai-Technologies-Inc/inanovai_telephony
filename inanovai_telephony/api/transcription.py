import json

import frappe
import requests
from twilio.rest import Client


@frappe.whitelist(allow_guest=True, methods=["POST"])
def transcription_callback():
    """Receive a completed Twilio transcription result."""
    payload = frappe.request.get_json(silent=True) or {}

    frappe.log_error(
        frappe.as_json(payload),
        "TWILIO TRANSCRIPTION CALLBACK RECEIVED",
    )

    status = payload.get("status")
    recording_sid = payload.get("sourceId")
    transcription_id = payload.get("id")

    if str(status).lower() != "completed":
        return {"ok": True}

    sentences = payload.get("sentences") or []

    transcript = "\n".join(
        sentence.get("text", "").strip()
        for sentence in sentences
        if sentence.get("text")
    )

    if not recording_sid or not transcript:
        frappe.log_error(
            json.dumps(payload, indent=2),
            "Twilio Transcription Callback - Missing Data",
        )
        return {"ok": True}

    settings = frappe.get_single("TP Twilio Settings")

    twilio_client = Client(
        settings.account_sid,
        settings.get_password("auth_token"),
    )

    try:
        recording = twilio_client.recordings(recording_sid).fetch()
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Twilio Recording Lookup Failed ({recording_sid})",
        )
        return {"ok": True}

    call_sid = recording.call_sid

    if not call_sid:
        return {"ok": True}

    comment = (
        "<b>Twilio Transcription</b><br>"
        f"Transcription ID: "
        f"{frappe.utils.escape_html(transcription_id or '')}"
        "<br><br>"
        f"{frappe.utils.escape_html(transcript).replace(chr(10), '<br>')}"
    )

    # ---------------------------------------------------------
    # Regular ERPNext Telephony
    # ---------------------------------------------------------
    if frappe.db.exists("TP Call Log", call_sid):
        call_log = frappe.get_doc("TP Call Log", call_sid)
        call_log.add_comment("Comment", comment)

        try:
            for link in call_log.get("links") or []:
                link_doctype = link.get("link_doctype")
                link_name = link.get("link_name")

                if (
                    link_doctype
                    and link_name
                    and frappe.db.exists(link_doctype, link_name)
                ):
                    linked_doc = frappe.get_doc(
                        link_doctype,
                        link_name,
                    )
                    linked_doc.add_comment(
                        "Comment",
                        comment,
                    )

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to add transcription to linked ERPNext document ({call_sid})",
            )

        frappe.db.commit()
        return {"ok": True}

    # ---------------------------------------------------------
    # Existing Frappe CRM
    # ---------------------------------------------------------
    if frappe.db.exists("CRM Call Log", call_sid):
        call_log = frappe.get_doc("CRM Call Log", call_sid)
        call_log.add_comment("Comment", comment)
        frappe.db.commit()
        return {"ok": True}

    frappe.log_error(
        f"Call Log not found for CallSid {call_sid}",
        f"Twilio Transcription - Call Log Not Found ({recording_sid})",
    )

    return {"ok": True}


@frappe.whitelist()
def submit_recording_for_transcription(recording_sid):
    """Submit a Twilio recording to the configured transcription service."""
    settings = frappe.get_single("TP Twilio Settings")

    account_sid = settings.account_sid
    auth_token = settings.get_password("auth_token")
    configuration_id = frappe.conf.get(
        "twilio_transcription_configuration"
    )

    if not configuration_id:
        frappe.log_error(
            "Twilio transcription configuration is not set.",
            "Automatic Twilio Transcription",
        )
        return

    response = requests.post(
        "https://voice.twilio.com/v3/Transcriptions",
        auth=(account_sid, auth_token),
        json={
            "transcriptionConfigurationId": configuration_id,
            "sourceId": recording_sid,
        },
        timeout=30,
    )

    if not response.ok:
        frappe.log_error(
            response.text,
            "Automatic Twilio Transcription Failed",
        )
        response.raise_for_status()

    return response.json()
