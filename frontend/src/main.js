import { createApp, h } from "vue"
import TelephonyCallUI from "./components/TelephonyCallUI.vue"
import TelephonySMSUI from "./components/TelephonySMSUI.vue"
import TelephonyOTPUI from "./components/TelephonyOTPUI.vue"

let app = null
let component = null

export function mountTelephonyCallUI(target) {
    if (!target) return null

    if (app) {
        app.unmount()
        app = null
        component = null
    }

    app = createApp({
        render() {
            return h(TelephonyCallUI, {
                ref: (instance) => {
                    component = instance
                },
            })
        },
    })

    app.mount(target)

    return component
}

window.mountTelephonyCallUI = mountTelephonyCallUI

let smsApp = null
let smsComponent = null

export function mountTelephonySMSUI(target, handlers = {}) {
    if (!target) return null

    if (smsApp) {
        smsApp.unmount()
        smsApp = null
        smsComponent = null
    }

    smsApp = createApp({
        render() {
            return h(TelephonySMSUI, {
                onSend: handlers.onSend,
                ref: (instance) => {
                    smsComponent = instance
                },
            })
        },
    })

    smsApp.mount(target)

    return smsComponent
}

window.mountTelephonySMSUI = mountTelephonySMSUI

let otpApp = null
let otpComponent = null

export function mountTelephonyOTPUI(target) {
    if (!target) return null

    if (otpApp) {
        otpApp.unmount()
        otpApp = null
        otpComponent = null
    }

    otpApp = createApp({
        render() {
            return h(TelephonyOTPUI, {
                ref: (instance) => {
                    otpComponent = instance
                },
            })
        },
    })

    otpApp.mount(target)

    return otpComponent
}

window.mountTelephonyOTPUI = mountTelephonyOTPUI
