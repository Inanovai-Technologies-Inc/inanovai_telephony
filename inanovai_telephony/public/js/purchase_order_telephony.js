let purchase_order_device = null

frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        if (frm.is_new() || !frm.doc.supplier) return

        frm.add_custom_button(__("Make a Call"), async () => {
            try {
                const phone_response = await frappe.call({
                    method: "inanovai_telephony.api.purchase_order.get_supplier_phone",
                    args: {
                        supplier: frm.doc.supplier,
                    },
                })

                const phone = phone_response.message?.phone

                if (!phone) {
                    frappe.msgprint(
                        __("No phone number is configured for supplier {0}.", [
                            frm.doc.supplier,
                        ])
                    )
                    return
                }

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

                if (!purchase_order_device) {
                    purchase_order_device = new Twilio.Device(token, {
                        codecPreferences: ["opus", "pcmu"],
                        fakeLocalDTMF: true,
                        enableRingingState: true,
                    })

                    await purchase_order_device.register()
                }

                const call = await purchase_order_device.connect({
                    params: {
                        To: phone,
                        link_doctype: "Purchase Order",
                        link_docname: frm.doc.name,
                    },
                })

                frappe.msgprint(
                    __("Calling {0}...", [phone])
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
