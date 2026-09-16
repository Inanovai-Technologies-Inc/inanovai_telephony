/*
 * Generic, config-driven telephony buttons — loaded globally (via hooks.py
 * app_include_js), not per-DocType (no hooks.py / doctype_js entry needed to
 * enable a new DocType).
 *
 * This file contains no DocType-specific branching in its ACTION logic at
 * all. Which buttons appear, and for which DocTypes, is entirely decided by
 * the "Telephony Settings" DocType via
 * inanovai_telephony.api.telephony_settings.get_telephony_actions. To
 * telephony-enable a new DocType (e.g. Quotation), add a row to Telephony
 * Settings — nothing here or in hooks.py needs to change.
 *
 * WHY THIS ISN'T frappe.ui.form.on("Doctype", {refresh(frm){...}}) PER
 * DOCTYPE, AND ISN'T frappe.ui.form.on("*", ...) EITHER:
 * Frappe's own client dispatch code (frappe/public/js/frappe/form/
 * script_manager.js, ScriptManager.get_handlers) looks up
 * frappe.ui.form.handlers[frm.doctype][event_name] using the form's literal
 * doctype string — there is no "*" fallback bucket anywhere in that lookup,
 * so frappe.ui.form.on("*", ...) silently never fires (verified by reading
 * that file, not assumed). Instead this hooks frappe.router.on("change", ...)
 * — the same first-party, core-Frappe event Frappe's own framework code uses
 * for cross-cutting, DocType-agnostic behavior (see e.g.
 * frappe/public/js/frappe/router_history.js and
 * frappe/public/js/onboarding_tours/onboarding_tours.js, both of which use
 * this exact pattern) — filtered to actual Form routes, and deferred past
 * any in-flight document load via frappe.after_ajax (frappe/public/js/
 * frappe/request.js), so frm.doc is guaranteed populated before we read a
 * phone number off it.
 *
 * KNOWN TRADE-OFF: this fires once per navigation to a Form route, not on
 * every subsequent frm.refresh() (e.g. after Save). In practice this means
 * a Telephony Settings change is picked up the next time the DocType is
 * opened, not instantly if you already have it open — acceptable for a
 * settings screen that isn't expected to change mid-edit.
 *
 * PHONE NUMBER RESOLUTION: button visibility never depends on whether a
 * phone number exists. Buttons are added purely from get_telephony_actions()
 * above. Only when a button is actually clicked does this call
 * inanovai_telephony.api.telephony_settings.resolve_phone_number(doctype,
 * docname) — a generic, metadata-driven backend resolver (direct fields,
 * then Dynamic Link fields, then contact_person, then any Link field whose
 * target doctype is Contact/Customer/Supplier — see that file for the exact
 * order). If it finds nothing, the click shows "No phone number found for
 * this document." instead of silently failing or hiding the button.
 *
 * LEGACY SCRIPT COMPATIBILITY (Purchase Order / Delivery Note):
 * Both were previously excluded from the generic flow (see git history for
 * the old, longer version of this comment). Now:
 *
 *  - Purchase Order (public/js/purchase_order_telephony.js) is fully
 *    RETIRED from hooks.py's doctype_js — it no longer loads at all. Its
 *    "Make a Call"/"Send SMS" buttons and its supplier-phone lookup are now
 *    entirely reproduced by this generic file: button visibility comes from
 *    Telephony Settings, and phone resolution falls through to Purchase
 *    Order's `supplier` Link field -> get_supplier_phone() (see
 *    api/telephony_settings.py's resolver). The file is left on disk,
 *    untouched, as an inert rollback safety net — it just isn't loaded.
 *    It HAD to be retired (not merely left in place) rather than run
 *    alongside this file, because its buttons use the exact same labels
 *    ("Make a Call", "Send SMS") this file also produces — leaving both
 *    active would duplicate them.
 *
 *  - Delivery Note (public/js/delivery_note_telephony.js) is DELIBERATELY
 *    KEPT ACTIVE in hooks.py's doctype_js, running alongside this file. Its
 *    one button is labeled "Send Delivery SMS" (not "Send SMS") and does
 *    something this generic file has no equivalent for: a pre-filled
 *    templated message, only once docstatus === 1. Because the label
 *    differs from anything this file adds, the two coexist without
 *    collision — a Delivery Note with Send SMS enabled in Telephony
 *    Settings will show BOTH "Send Delivery SMS" (submitted-only, templated)
 *    and a generic "Send SMS" (blank composer, any status) as two distinct,
 *    intentional actions, not a duplicate.
 *
 * LEGACY_SCRIPT_DOCTYPES is now empty — nothing currently needs the
 * "don't run the generic flow at all on this DocType" escape hatch — but the
 * mechanism is kept as a named extension point in case a future DocType's
 * dedicated script needs it (e.g. if it reused the generic labels itself).
 */

const LEGACY_SCRIPT_DOCTYPES = []

let telephony_settings_device = null
let telephony_settings_call_ui = null
let telephony_settings_sms_ui = null
let telephony_settings_otp_ui = null

function getTelephonySettingsCallUI() {
    if (telephony_settings_call_ui) return telephony_settings_call_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-call-ui-settings"
    document.body.appendChild(container)

    telephony_settings_call_ui = window.mountTelephonyCallUI(container)
    return telephony_settings_call_ui
}

function getTelephonySettingsSMSUI() {
    if (telephony_settings_sms_ui) return telephony_settings_sms_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-sms-ui-settings"
    document.body.appendChild(container)

    telephony_settings_sms_ui = window.mountTelephonySMSUI(container, {
        onSend: ({ to, message }) => {
            frappe.call({
                method: "telephony.twilio.sms.send_sms",
                args: {
                    to,
                    message,
                },
                freeze: true,
                freeze_message: __("Sending SMS..."),
                callback: (r) => {
                    if (r && !r.exc) {
                        telephony_settings_sms_ui.showSuccess()
                        setTimeout(() => {
                            telephony_settings_sms_ui.close()
                        }, 1000)
                    } else {
                        telephony_settings_sms_ui.setSending(false)
                    }
                },
                error: () => {
                    telephony_settings_sms_ui.setSending(false)
                },
            })
        },
    })

    return telephony_settings_sms_ui
}

function getTelephonySettingsOTPUI() {
    if (telephony_settings_otp_ui) return telephony_settings_otp_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-otp-ui-settings"
    document.body.appendChild(container)

    telephony_settings_otp_ui = window.mountTelephonyOTPUI(container)
    return telephony_settings_otp_ui
}

async function resolveTelephonyPhoneNumber(frm) {
    // Generic, click-time only — never used to decide button visibility.
    // See api/telephony_settings.py:resolve_phone_number for the resolution
    // order (direct fields, Supplier, Dynamic Link fields, contact_person,
    // then any Link field pointing at Contact/Customer/Supplier).
    const response = await frappe.call({
        method: "inanovai_telephony.api.telephony_settings.resolve_phone_number",
        args: {
            doctype: frm.doctype,
            docname: frm.doc.name,
        },
    })

    return response.message || { phone: "", source: "" }
}

function notifyNoTelephonyPhoneNumber() {
    frappe.msgprint(__("No phone number found for this document."))
}

async function startTelephonySettingsCall(frm, phone) {
    try {
        const response = await frappe.call({
            method: "telephony.twilio.api.generate_access_token",
        })

        const token = response.message?.token

        if (!token) {
            frappe.msgprint(
                __("Unable to initialize Telephony. Please check your Telephony Agent settings.")
            )
            return
        }

        if (!telephony_settings_device) {
            telephony_settings_device = new Twilio.Device(token, {
                codecPreferences: ["opus", "pcmu"],
                fakeLocalDTMF: true,
                enableRingingState: true,
            })

            await telephony_settings_device.register()
        }

        const call = await telephony_settings_device.connect({
            params: {
                To: phone,
                link_doctype: frm.doctype,
                link_docname: frm.doc.name,
                // Generic, field-presence based (not a doctype check): when the
                // current document has a contact_person field set, pass it along
                // so the call log links to that exact Contact instead of falling
                // back to phone-number matching. Mirrors Opportunity's existing
                // behavior; a no-op for doctypes with no such field (e.g. Lead).
                ...(frm.doc.contact_person ? { contact_person: frm.doc.contact_person } : {}),
            },
        })

        const ui = getTelephonySettingsCallUI()

        if (ui) {
            ui.startCall(call, phone)
        }

        call.on("error", (error) => {
            console.error("Twilio call error:", error)
        })
    } catch (error) {
        console.error(error)

        frappe.msgprint(
            __("Unable to start the call: {0}", [error.message || error])
        )
    }
}

function setupTelephonyActions(frm) {
    if (frm.is_new()) return
    if (LEGACY_SCRIPT_DOCTYPES.includes(frm.doctype)) return

    frappe.call({
        method: "inanovai_telephony.api.telephony_settings.get_telephony_actions",
        args: {
            doctype: frm.doctype,
        },
        callback: (r) => {
            const actions = r.message

            // Telephony Settings missing / disabled / no row for this
            // DocType / row exists but every action is off -> nothing to add.
            // Deliberately NOT checking for a phone number here — button
            // visibility is config-only; phone resolution happens per-click.
            if (!actions || !actions.enabled) return

            if (actions.make_a_call) {
                frm.add_custom_button(__("Make a Call"), async () => {
                    const { phone } = await resolveTelephonyPhoneNumber(frm)
                    if (!phone) return notifyNoTelephonyPhoneNumber()
                    startTelephonySettingsCall(frm, phone)
                })
            }

            if (actions.send_sms) {
                frm.add_custom_button(__("Send SMS"), async () => {
                    const { phone } = await resolveTelephonyPhoneNumber(frm)
                    if (!phone) return notifyNoTelephonyPhoneNumber()
                    getTelephonySettingsSMSUI()?.open(phone)
                })
            }

            if (actions.send_otp) {
                frm.add_custom_button(__("Send OTP"), async () => {
                    const { phone } = await resolveTelephonyPhoneNumber(frm)
                    if (!phone) return notifyNoTelephonyPhoneNumber()
                    getTelephonySettingsOTPUI()?.open(phone)
                })
            }
        },
    })
}

frappe.router.on("change", () => {
    frappe.after_ajax(() => {
        const route = frappe.get_route()

        // Only real document forms ["Form", "<DocType>", "<docname>"] — not
        // list views, reports, workspaces, etc.
        if (!route || route[0] !== "Form") return

        // cur_frm is Frappe's own global reference to the currently active
        // form (set synchronously at the top of Form.prototype.refresh,
        // before this document's data is used) — the same reference every
        // other custom script on the page relies on.
        if (!cur_frm || cur_frm.doctype !== route[1]) return

        setupTelephonyActions(cur_frm)
    })
})
