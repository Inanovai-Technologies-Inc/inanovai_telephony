let device = null
let call_ui = null

function getCallUI() {
    if (call_ui) return call_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-call-ui"
    document.body.appendChild(container)

    call_ui = window.mountTelephonyCallUI(container)
    return call_ui
}

frappe.ui.form.on("Lead", {
    refresh(frm) {
        if (frm.is_new() || !frm.doc.mobile_no) return

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

                if (!device) {
                    device = new Twilio.Device(token, {
                        codecPreferences: ["opus", "pcmu"],
                        fakeLocalDTMF: true,
                        enableRingingState: true,
                    })

                    await device.register()
                }

                const call = await device.connect({
                    params: {
                        To: frm.doc.mobile_no,
                        link_doctype: "Lead",
                        link_docname: frm.doc.name,
                    },
                })

                const ui = getCallUI()

                if (ui) {
                    ui.startCall(call, frm.doc.mobile_no)
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
