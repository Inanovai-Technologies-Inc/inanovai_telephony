import { createApp, h } from "vue"
import TelephonyCallUI from "./components/TelephonyCallUI.vue"

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
