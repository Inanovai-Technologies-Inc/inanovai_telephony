import frappe

from telephony.twilio.twilio_handler import Twilio, TwilioCallDetails

from inanovai_telephony.api.transcription import (
    submit_recording_for_transcription,
)


def _format_datetime(value):
    """Convert Twilio datetime to Frappe-compatible datetime."""
    if not value:
        return None

    return value.strftime("%Y-%m-%d %H:%M:%S")


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_call_status_info(**kwargs):
    """Update TP Call Log from Twilio status callbacks."""
    try:
        args = frappe._dict(kwargs)

        call_sid = args.get("ParentCallSid") or args.get("CallSid")
        callback_status = args.get("CallStatus")
        callback_duration = args.get("CallDuration")

        if not call_sid:
            return {"ok": True}

        if not frappe.db.exists("TP Call Log", call_sid):
            frappe.log_error(
                f"TP Call Log not found for CallSid: {call_sid}",
                "Twilio Call Status Callback",
            )
            return {"ok": True}

        twilio = Twilio.connect()
        call_details = twilio.get_call_info(call_sid)

        values = {
            "status": TwilioCallDetails.get_call_status(
                callback_status or call_details.status
            ),
        }

        if callback_duration not in (None, ""):
            try:
                values["duration"] = float(callback_duration)
            except (TypeError, ValueError):
                pass

        if "duration" not in values and call_details.duration is not None:
            values["duration"] = call_details.duration

        start_time = _format_datetime(call_details.start_time)
        end_time = _format_datetime(call_details.end_time)

        if start_time:
            values["start_time"] = start_time

        if end_time:
            values["end_time"] = end_time

        # Use direct database update instead of get_doc().save()
        # to avoid TimestampMismatchError when multiple Twilio
        # callbacks arrive at the same time.
        frappe.db.set_value(
            "TP Call Log",
            call_sid,
            values,
            update_modified=False,
        )

        frappe.db.commit()

        return {
            "ok": True,
            "call_sid": call_sid,
            "values": values,
        }

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Twilio Call Status Callback Failed",
        )
        return {"ok": True}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_recording_info(**kwargs):
    """Save Twilio recording and submit it for transcription."""
    try:
        args = frappe._dict(kwargs)

        frappe.log_error(
            frappe.as_json(dict(args)),
            "TWILIO RECORDING CALLBACK RECEIVED",
        )

        call_sid = args.get("CallSid")
        recording_url = args.get("RecordingUrl")
        recording_sid = args.get("RecordingSid")
        recording_status = str(
            args.get("RecordingStatus") or ""
        ).lower()

        if not call_sid:
            return {"ok": True}

        if frappe.db.exists("TP Call Log", call_sid):
            if recording_url:
                frappe.db.set_value(
                    "TP Call Log",
                    call_sid,
                    "recording_url",
                    recording_url,
                    update_modified=False,
                )
                frappe.db.commit()

        if recording_status == "completed" and recording_sid:
            try:
                result = submit_recording_for_transcription(recording_sid)

                frappe.log_error(
                    frappe.as_json(result),
                    "TWILIO TRANSCRIPTION SUBMISSION SUCCESS",
                )

            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "Automatic Twilio Transcription Submission Failed",
                )

        return {"ok": True}

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Failed to capture regular ERPNext recording",
        )
        return {"ok": True}
