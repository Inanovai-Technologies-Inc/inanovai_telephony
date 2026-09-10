let opportunity_device = null
let opportunity_call_ui = null

function getOpportunityCallUI() {
    if (opportunity_call_ui) return opportunity_call_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-call-ui-opportunity"
    document.body.appendChild(container)

    opportunity_call_ui = window.mountTelephonyCallUI(container)
    return opportunity_call_ui
}

frappe.ui.form.on("Opportunity", {
    refresh(frm) {
        if (frm.is_new() || !frm.doc.contact_mobile) return

        frm.add_custom_button(__("Make a Call"), async () => {
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

                if (!opportunity_device) {
                    opportunity_device = new Twilio.Device(token, {
                        codecPreferences: ["opus", "pcmu"],
                        fakeLocalDTMF: true,
                        enableRingingState: true,
                    })

                    await opportunity_device.register()
                }

                const call = await opportunity_device.connect({
                    params: {
                        To: frm.doc.contact_mobile,
                        link_doctype: "Opportunity",
                        link_docname: frm.doc.name,
                        contact_person: frm.doc.contact_person,
                    },
                })

                const ui = getOpportunityCallUI()

                if (ui) {
                    ui.startCall(call, frm.doc.contact_mobile)
                }

                call.on("error", (error) => {
                    console.error("Twilio call error:", error)
                })
            } catch (error) {
                console.error(error)

                frappe.msgprint(
                    __("Unable to start the call: {0}", [
                        error.message || error,
                    ])
                )
            }
        })
    },
})
