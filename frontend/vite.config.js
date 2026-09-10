import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
    plugins: [vue()],
    root: "frontend",
    define: {
        "process.env.NODE_ENV": JSON.stringify("production"),
    },
    build: {
        outDir: "../inanovai_telephony/public/js",
        emptyOutDir: false,
        lib: {
            entry: "src/main.js",
            name: "InanovaiTelephony",
            formats: ["iife"],
            fileName: () => "telephony_call_ui.js",
        },
    },
})
