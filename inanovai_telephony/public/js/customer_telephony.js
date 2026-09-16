let customer_otp_ui = null

function getCustomerOTPUI() {
    if (customer_otp_ui) return customer_otp_ui

    const container = document.createElement("div")
    container.id = "inanovai-telephony-otp-ui-customer"
    document.body.appendChild(container)

    customer_otp_ui = window.mountTelephonyOTPUI(container)
    return customer_otp_ui
}

frappe.ui.form.on("Customer", {
    refresh(frm) {
        if (frm.is_new() || !frm.doc.mobile_no) return

        frm.add_custom_button(__("Send OTP"), () => {
            getCustomerOTPUI()?.open(frm.doc.mobile_no)
        })
    },
})
