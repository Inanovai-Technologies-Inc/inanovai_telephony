<template>
  <Transition name="otp-fade">
    <div
      v-if="visible"
      class="otp-overlay"
      @mousedown.self="handleClose"
    >
      <div
        class="otp-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="otp-ui-title"
      >
        <div class="otp-glow" aria-hidden="true"></div>

        <div class="otp-surface">

          <!-- Header -->
          <div class="otp-header">
            <div class="otp-header-info">
              <div class="brand-mark">
                <img
                  src="https://inanovai.com/files/Inanovai%20Logo%20without%20background.png"
                  alt="Inanovai"
                />
              </div>

              <div class="otp-header-text">
                <div id="otp-ui-title" class="otp-title">OTP Verification</div>
                <div class="otp-subtitle">Verify your phone number securely</div>
              </div>
            </div>

            <button
              type="button"
              class="icon-button"
              title="Close"
              aria-label="Close"
              :disabled="loading"
              @click="handleClose"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>

          <Transition name="otp-state" mode="out-in">

            <!-- Step 1: phone number -->
            <div v-if="!otpSent && !verified" key="phone" class="otp-body">
              <div class="otp-field">
                <label class="otp-label" for="otp-phone-input">Mobile Number</label>

                <div class="otp-phone-wrap">
                  <svg class="otp-phone-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M6.6 10.8c2.9 2.3 5.1 2.3 8 0l1.7 1.7c.5.5 1.3.5 1.8 0l1.4-1.4c.5-.5.5-1.3 0-1.8C15.2 4.7 8.8 4.7 4.5 9.3c-.5.5-.5 1.3 0 1.8l1.4 1.4c.5.5 1.3.5 1.8 0l1.7-1.7z"
                    />
                  </svg>
                  <input
                    id="otp-phone-input"
                    ref="phoneInput"
                    v-model="phone"
                    class="otp-phone-input"
                    type="tel"
                    placeholder="+91XXXXXXXXXX"
                    :disabled="loading"
                  />
                </div>
              </div>

              <div v-if="message" :class="['otp-banner', messageType]">
                {{ message }}
              </div>

              <button
                type="button"
                class="otp-btn otp-btn-primary"
                :disabled="loading || !phone"
                @click="sendOTP"
              >
                <span v-if="loading" class="otp-spinner" aria-hidden="true"></span>
                <span>{{ loading ? "Sending..." : "Send OTP" }}</span>
              </button>
            </div>

            <!-- Step 2: enter code -->
            <div v-else-if="otpSent && !verified" key="otp" class="otp-body">
              <div class="otp-step-title">Enter the OTP</div>
              <div class="otp-step-subtitle">
                Enter the 6-digit verification code sent to
                <span class="otp-phone-chip">{{ phone }}</span>
              </div>

              <div class="otp-digits" @paste="handleDigitPaste">
                <input
                  v-for="(digit, i) in otpDigits"
                  :key="i"
                  :ref="(el) => setDigitRef(el, i)"
                  class="otp-digit"
                  type="text"
                  inputmode="numeric"
                  autocomplete="one-time-code"
                  maxlength="1"
                  :aria-label="`Digit ${i + 1} of 6`"
                  :value="digit"
                  :disabled="loading || verified"
                  @input="handleDigitInput(i, $event)"
                  @keydown="handleDigitKeydown(i, $event)"
                />
              </div>

              <div class="otp-expiry-row">
                <span v-if="expiresIn > 0" class="otp-expiry">
                  OTP expires in {{ formattedExpiry }}
                </span>
                <span v-else-if="hasExpired" class="otp-expired">
                  OTP expired — use another number to request a new code
                </span>
              </div>

              <div v-if="message" :class="['otp-banner', messageType]">
                {{ message }}
              </div>

              <button
                type="button"
                class="otp-btn otp-btn-primary"
                :disabled="loading || !isComplete"
                @click="verifyOTP"
              >
                <span v-if="loading" class="otp-spinner" aria-hidden="true"></span>
                <span>{{ loading ? "Verifying..." : "Verify OTP" }}</span>
              </button>

              <button
                type="button"
                class="otp-btn-ghost"
                :disabled="loading"
                @click="reset"
              >
                Use another number
              </button>
            </div>

            <!-- Step 3: verified -->
            <div v-else key="success" class="otp-success">
              <div class="otp-success-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div class="otp-success-title">OTP Verified</div>
              <div class="otp-success-text">Your phone number has been successfully verified.</div>
            </div>

          </Transition>

        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue"

const visible = ref(false)
const phone = ref("")
const otpDigits = ref(["", "", "", "", "", ""])
const loading = ref(false)
const otpSent = ref(false)
const verified = ref(false)
const expiresIn = ref(0)
const hasExpired = ref(false)
const message = ref("")
const messageType = ref("")
const phoneInput = ref(null)
const digitRefs = ref([])

let expiryTimer = null

const otp = computed(() => otpDigits.value.join(""))
const isComplete = computed(() => otp.value.length === 6)

const formattedExpiry = computed(() => {
  const minutes = Math.floor(expiresIn.value / 60)
  const seconds = expiresIn.value % 60
  return `${minutes}:${String(seconds).padStart(2, "0")}`
})

function setDigitRef(el, index) {
  if (el) digitRefs.value[index] = el
}

function focusDigit(index) {
  nextTick(() => digitRefs.value[index]?.focus())
}

function open(number = "") {
  phone.value = number || ""
  otpDigits.value = ["", "", "", "", "", ""]
  loading.value = false
  otpSent.value = false
  verified.value = false
  expiresIn.value = 0
  hasExpired.value = false
  message.value = ""
  messageType.value = ""
  visible.value = true

  nextTick(() => {
    phoneInput.value?.focus()
  })
}

function close() {
  if (loading.value) return
  visible.value = false
  clearExpiryTimer()
}

function handleClose() {
  close()
}

function clearExpiryTimer() {
  if (expiryTimer) {
    clearInterval(expiryTimer)
    expiryTimer = null
  }
}

function startExpiryTimer(seconds) {
  clearExpiryTimer()
  expiresIn.value = seconds
  hasExpired.value = false

  expiryTimer = setInterval(() => {
    if (expiresIn.value <= 1) {
      expiresIn.value = 0
      hasExpired.value = true
      clearExpiryTimer()
      return
    }
    expiresIn.value--
  }, 1000)
}

function handleDigitInput(index, event) {
  const digit = (event.target.value || "").replace(/\D/g, "").slice(-1)
  otpDigits.value[index] = digit
  event.target.value = digit

  if (digit && index < 5) {
    focusDigit(index + 1)
  }
}

function handleDigitKeydown(index, event) {
  if (event.key === "Backspace" && !otpDigits.value[index] && index > 0) {
    otpDigits.value[index - 1] = ""
    focusDigit(index - 1)
  }
}

function handleDigitPaste(event) {
  const text = (event.clipboardData || window.clipboardData)?.getData("text") || ""
  const digits = text.replace(/\D/g, "").slice(0, 6).split("")

  if (!digits.length) return

  event.preventDefault()
  digits.forEach((d, i) => {
    otpDigits.value[i] = d
  })
  focusDigit(Math.min(digits.length, 5))
}

async function sendOTP() {
  loading.value = true
  message.value = ""

  try {
    const response = await frappe.call({
      method: "telephony.twilio.sms.generate_otp",
      args: {
        phone_number: phone.value,
        purpose: "Verification",
      },
    })

    const result = response.message

    if (result?.sent) {
      otpSent.value = true
      message.value = "OTP sent successfully."
      messageType.value = "success"
      startExpiryTimer(result.expires_in || 300)
      focusDigit(0)
    } else {
      message.value = "Unable to send OTP."
      messageType.value = "error"
    }
  } catch (error) {
    console.error(error)
    message.value = "Unable to send OTP."
    messageType.value = "error"
  } finally {
    loading.value = false
  }
}

async function verifyOTP() {
  loading.value = true
  message.value = ""

  try {
    const response = await frappe.call({
      method: "telephony.twilio.sms.verify_otp",
      args: {
        phone_number: phone.value,
        otp: otp.value,
        purpose: "Verification",
      },
    })

    const result = response.message

    if (result?.verified || result?.success) {
      verified.value = true
      message.value = "OTP verified successfully."
      messageType.value = "success"
      clearExpiryTimer()
    } else {
      message.value = "Invalid or expired OTP."
      messageType.value = "error"
    }
  } catch (error) {
    console.error(error)
    message.value = "Invalid or expired OTP."
    messageType.value = "error"
  } finally {
    loading.value = false
  }
}

function reset() {
  clearExpiryTimer()
  otpDigits.value = ["", "", "", "", "", ""]
  otpSent.value = false
  verified.value = false
  expiresIn.value = 0
  hasExpired.value = false
  message.value = ""
  messageType.value = ""

  nextTick(() => {
    phoneInput.value?.focus()
  })
}

function handleKeydown(event) {
  if (event.key === "Escape" && visible.value) {
    handleClose()
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown)
  clearExpiryTimer()
})

defineExpose({
  open,
  close,
})
</script>

<style scoped>
.otp-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(17, 24, 39, 0.38);
  -webkit-backdrop-filter: blur(3px);
  backdrop-filter: blur(3px);
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}

.otp-modal {
  position: relative;
  width: 100%;
  max-width: 380px;
  --coral: #ef6a52;
  --coral-dark: #dc4c3f;
  --ink: #1f2430;
  --muted: #6b7280;
  color: var(--ink);
}

.otp-glow {
  position: absolute;
  inset: -32px;
  z-index: -1;
  border-radius: 44px;
  background:
    radial-gradient(48% 42% at 18% 8%, rgba(239, 106, 82, 0.3), transparent 70%),
    radial-gradient(46% 46% at 88% 92%, rgba(239, 106, 82, 0.16), transparent 70%);
  filter: blur(36px);
  opacity: 0.8;
  pointer-events: none;
}

.otp-surface {
  position: relative;
  isolation: isolate;
  background-color: rgba(255, 255, 255, 0.6);
  background-image:
    linear-gradient(165deg, rgba(255, 255, 255, 0.58) 0%, rgba(255, 255, 255, 0.18) 45%, rgba(255, 255, 255, 0.42) 100%),
    radial-gradient(120% 60% at 12% -10%, rgba(239, 106, 82, 0.1), transparent 55%);
  -webkit-backdrop-filter: blur(26px) saturate(170%);
  backdrop-filter: blur(26px) saturate(170%);
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: 22px;
  box-shadow:
    0 28px 70px rgba(17, 24, 39, 0.22),
    0 2px 10px rgba(17, 24, 39, 0.08),
    0 0 0 1px rgba(239, 106, 82, 0.045),
    inset 0 1px 0 rgba(255, 255, 255, 0.85);
  overflow: hidden;
}

.otp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 16px 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.04));
  border-bottom: 1px solid rgba(255, 255, 255, 0.45);
}

.otp-header-info {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}

.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-mark img {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.otp-header-text {
  min-width: 0;
}

.otp-title {
  font-size: 15.5px;
  font-weight: 650;
  letter-spacing: -0.01em;
  color: var(--ink);
  line-height: 1.3;
}

.otp-subtitle {
  margin-top: 2px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.3;
}

.icon-button {
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.4);
  color: #7a7f8a;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease, transform 0.12s ease;
}

.icon-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(17, 24, 39, 0.05);
  color: var(--ink);
}

.icon-button:active:not(:disabled) {
  transform: scale(0.94);
}

.icon-button:disabled {
  opacity: 0.5;
  cursor: default;
}

.icon-button svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.otp-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
}

.otp-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.otp-label {
  font-size: 11.5px;
  font-weight: 650;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted);
}

.otp-phone-wrap {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 14px;
  border-radius: 11px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.4);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.otp-phone-wrap:focus-within {
  border-color: rgba(239, 106, 82, 0.45);
  background: rgba(255, 255, 255, 0.55);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 0 0 3px rgba(239, 106, 82, 0.14);
}

.otp-phone-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  fill: none;
  stroke: var(--coral);
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.otp-phone-input {
  flex: 1;
  min-width: 0;
  border: 0;
  background: transparent;
  outline: none;
  font: inherit;
  font-size: 14.5px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
}

.otp-phone-input:disabled {
  opacity: 0.7;
}

.otp-phone-input::placeholder {
  color: rgba(107, 114, 128, 0.7);
  font-weight: 500;
}

.otp-step-title {
  font-size: 14.5px;
  font-weight: 650;
  color: var(--ink);
}

.otp-step-subtitle {
  margin-top: -8px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--muted);
}

.otp-phone-chip {
  display: inline-block;
  font-weight: 650;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}

.otp-digits {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}

.otp-digit {
  width: 100%;
  aspect-ratio: 1;
  min-width: 0;
  border-radius: 11px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.42);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  text-align: center;
  font-size: 19px;
  font-weight: 650;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, transform 0.12s ease;
}

.otp-digit:focus {
  outline: none;
  border-color: rgba(239, 106, 82, 0.5);
  background: rgba(255, 255, 255, 0.6);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 0 0 3px rgba(239, 106, 82, 0.16);
  transform: translateY(-1px);
}

.otp-digit:disabled {
  opacity: 0.6;
}

.otp-expiry-row {
  min-height: 16px;
  text-align: center;
}

.otp-expiry {
  font-size: 12px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.otp-expired {
  font-size: 12px;
  color: var(--coral-dark);
  font-weight: 600;
}

.otp-banner {
  padding: 9px 12px;
  border-radius: 9px;
  font-size: 12.5px;
  font-weight: 600;
  text-align: center;
}

.otp-banner.success {
  background: rgba(34, 197, 94, 0.12);
  color: #1a9350;
}

.otp-banner.error {
  background: rgba(239, 106, 82, 0.12);
  color: var(--coral-dark);
}

.otp-btn {
  height: 40px;
  padding: 0 18px;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid transparent;
  transition:
    background 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease,
    transform 0.12s ease,
    box-shadow 0.15s ease;
}

.otp-btn:disabled {
  opacity: 0.55;
  cursor: default;
}

.otp-btn-primary {
  background: linear-gradient(180deg, #f0705a, var(--coral-dark));
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(220, 76, 63, 0.32);
}

.otp-btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #ea5c44, #c9433a);
  box-shadow: 0 8px 20px rgba(220, 76, 63, 0.4);
}

.otp-btn-primary:active:not(:disabled) {
  transform: scale(0.97);
}

.otp-btn-ghost {
  border: 0;
  background: transparent;
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px;
  align-self: center;
  transition: color 0.15s ease;
}

.otp-btn-ghost:hover:not(:disabled) {
  color: var(--coral-dark);
}

.otp-btn-ghost:disabled {
  opacity: 0.5;
  cursor: default;
}

.otp-btn-primary:focus-visible,
.otp-btn-ghost:focus-visible,
.icon-button:focus-visible,
.otp-digit:focus-visible,
.otp-phone-input:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.otp-spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #ffffff;
  animation: otp-spin 0.7s linear infinite;
}

@keyframes otp-spin {
  to {
    transform: rotate(360deg);
  }
}

.otp-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 34px 20px 38px;
  text-align: center;
}

.otp-success-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(34, 197, 94, 0.14);
  border: 1px solid rgba(34, 197, 94, 0.3);
  box-shadow: 0 4px 14px rgba(34, 197, 94, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.7);
  color: #22c55e;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: otp-pop 0.4s ease;
}

.otp-success-icon svg {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

@keyframes otp-pop {
  0% {
    transform: scale(0.7);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.otp-success-title {
  font-size: 14.5px;
  font-weight: 650;
  color: var(--ink);
}

.otp-success-text {
  font-size: 13px;
  color: var(--muted);
  max-width: 30ch;
}

.otp-fade-enter-active,
.otp-fade-leave-active {
  transition: opacity 0.18s ease;
}

.otp-fade-enter-from,
.otp-fade-leave-to {
  opacity: 0;
}

.otp-fade-enter-active .otp-modal,
.otp-fade-leave-active .otp-modal {
  transition: transform 0.18s ease, opacity 0.18s ease;
}

.otp-fade-enter-from .otp-modal,
.otp-fade-leave-to .otp-modal {
  transform: translateY(8px) scale(0.98);
  opacity: 0;
}

.otp-state-enter-active,
.otp-state-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.otp-state-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.otp-state-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 480px) {
  .otp-overlay {
    padding: 16px;
  }

  .otp-modal {
    max-width: none;
  }

  .otp-digit {
    font-size: 17px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .otp-fade-enter-active,
  .otp-fade-leave-active,
  .otp-fade-enter-active .otp-modal,
  .otp-fade-leave-active .otp-modal,
  .otp-state-enter-active,
  .otp-state-leave-active {
    transition: none;
  }

  .otp-spinner {
    animation: none;
  }

  .otp-success-icon {
    animation: none;
  }
}
</style>
