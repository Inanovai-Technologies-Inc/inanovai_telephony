let delivery_note_sms_ui = null

function getDeliveryNoteSMSUI() {
    if (delivery_note_sms_ui) return delivery_note_sms_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-sms-ui-delivery-note"
    document.body.appendChild(container)

    delivery_note_sms_ui = window.mountTelephonySMSUI(container, {
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
                        delivery_note_sms_ui.showSuccess()
                        setTimeout(() => {
                            delivery_note_sms_ui.close()
                        }, 1000)
                    } else {
                        delivery_note_sms_ui.setSending(false)
                    }
                },
                error: () => {
                    delivery_note_sms_ui.setSending(false)
                },
            })
        },
    })

    return delivery_note_sms_ui
}

frappe.ui.form.on("Delivery Note", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.docstatus !== 1 || !frm.doc.contact_mobile) return

        frm.add_custom_button(__("Send Delivery SMS"), () => {
            const message = __(
                "Your order has been delivered. Delivery Note {0} has been completed.",
                [frm.doc.name]
            )

            getDeliveryNoteSMSUI()?.open(frm.doc.contact_mobile, message)
        })
    },
})
