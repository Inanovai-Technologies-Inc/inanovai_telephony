let opportunity_device = null

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
                    },
                })

                frappe.msgprint(
                    __("Calling {0}...", [frm.doc.contact_mobile])
                )

                call.on("disconnect", () => {
                    frappe.show_alert({
                        message: __("Call ended"),
                        indicator: "green",
                    })
                })

                call.on("error", (error) => {
                    frappe.msgprint(
                        __("Call failed: {0}", [error.message])
                    )
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
