k<template>
  <div v-if="visible">

    <Transition name="mode-swap" mode="out-in">

    <!-- Minimized call bar -->
    <div v-if="minimized" key="mini" class="call-mini-bar">
      <div class="mini-info">
        <div class="mini-brand">
          <img
            src="https://inanovai.com/files/Inanovai%20Logo%20without%20background.png"
            alt="Inanovai"
          />
        </div>

        <div class="mini-dot" :class="{ connected, pulsing: !connected }"></div>

        <div class="mini-text">
          <div class="mini-name">{{ title }}</div>
          <div class="mini-status">
            {{ phoneNumber }}
            <span class="mini-status-sep">&middot;</span>
            {{ connected ? formattedDuration : statusText }}
          </div>
        </div>
      </div>

      <button
        type="button"
        class="mini-expand"
        title="Open call"
        @click="minimized = false"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M14 5h5v5M19 5l-7 7" />
        </svg>
      </button>

      <button
        type="button"
        class="mini-hangup"
        title="End call"
        @click="endCall"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M6.6 10.8c2.9 2.3 5.1 2.3 8 0l1.7 1.7c.5.5 1.3.5 1.8 0l1.4-1.4c.5-.5.5-1.3 0-1.8C15.2 4.7 8.8 4.7 4.5 9.3c-.5.5-.5 1.3 0 1.8l1.4 1.4c.5.5 1.3.5 1.8 0l1.7-1.7z"
          />
        </svg>
      </button>
    </div>

    <!-- Expanded call card -->
    <div v-else key="full" class="call-popup">
      <div class="call-glow" aria-hidden="true"></div>

      <div class="call-surface">

      <!-- Header -->
      <div class="call-header">
        <div class="contact-info">

          <div class="brand-mark">
            <img
              src="https://inanovai.com/files/Inanovai%20Logo%20without%20background.png"
              alt="Inanovai"
            />
          </div>

          <div class="contact-details">
            <div class="contact-name">{{ title }}</div>
            <div class="phone-number">{{ phoneNumber }}</div>
          </div>

        </div>

        <div class="header-actions">
          <button
            type="button"
            class="icon-button"
            title="Minimize"
            @click="minimized = true"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 15h4v4h2v-6H5v2zm10-10v6h6V9h-4V5h-2z" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Call information -->
      <div class="call-content">

        <div
          class="call-indicator"
          :class="{ active: connected, pulsing: !connected }"
        >
          <svg
            v-if="connected"
            class="waveform"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <rect class="eq-bar eq-bar-1" x="3.6" y="10" width="2.3" height="4" rx="1.15" />
            <rect class="eq-bar eq-bar-2" x="8" y="6.5" width="2.3" height="11" rx="1.15" />
            <rect class="eq-bar eq-bar-3" x="12.4" y="4" width="2.3" height="16" rx="1.15" />
            <rect class="eq-bar eq-bar-4" x="16.8" y="7.5" width="2.3" height="9" rx="1.15" />
          </svg>

          <svg
            v-else
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M6.6 10.8c2.9 2.3 5.1 2.3 8 0l1.7 1.7c.5.5 1.3.5 1.8 0l1.4-1.4c.5-.5.5-1.3 0-1.8C15.2 4.7 8.8 4.7 4.5 9.3c-.5.5-.5 1.3 0 1.8l1.4 1.4c.5.5 1.3.5 1.8 0l1.7-1.7z"
            />
          </svg>
        </div>

        <div class="duration">
          {{ connected ? formattedDuration : "" }}
        </div>

        <div class="call-status" :class="{ live: !connected }">
          {{ statusText }}
        </div>
      </div>

      <!-- Call actions -->
      <div class="call-actions">

        <template v-if="connected">

          <!-- Mute -->
          <button
            type="button"
            class="action"
            :class="{ active: muted }"
            @click="toggleMute"
          >
            <span class="action-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3z"
                />
                <path d="M19 11a7 7 0 0 1-14 0M12 18v4M8 22h8" />
              </svg>
            </span>

            <span>{{ muted ? "Unmute" : "Mute" }}</span>
          </button>

          <!-- Keypad -->
          <button
            type="button"
            class="action"
            :class="{ active: showKeypad }"
            @click="showKeypad = !showKeypad"
          >
            <span class="action-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="7" cy="6" r="1.5" />
                <circle cx="12" cy="6" r="1.5" />
                <circle cx="17" cy="6" r="1.5" />
                <circle cx="7" cy="12" r="1.5" />
                <circle cx="12" cy="12" r="1.5" />
                <circle cx="17" cy="12" r="1.5" />
                <circle cx="7" cy="18" r="1.5" />
                <circle cx="12" cy="18" r="1.5" />
                <circle cx="17" cy="18" r="1.5" />
              </svg>
            </span>

            <span>Keypad</span>
          </button>

          <!-- Hang Up -->
          <button
            type="button"
            class="action hangup"
            @click="hangUpCall"
          >
            <span class="action-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M6.6 10.8c2.9 2.3 5.1 2.3 8 0l1.7 1.7c.5.5 1.3.5 1.8 0l1.4-1.4c.5-.5.5-1.3 0-1.8C15.2 4.7 8.8 4.7 4.5 9.3c-.5.5-.5 1.3 0 1.8l1.4 1.4c.5.5.5 1.3 0 1.8l1.7-1.7z"
                />
              </svg>
            </span>

            <span>Hang Up</span>
          </button>

        </template>

        <template v-else>

          <!-- Cancel -->
          <button
            type="button"
            class="action cancel"
            @click="cancelCall"
          >
            <span class="action-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M6.6 10.8c2.9 2.3 5.1 2.3 8 0l1.7 1.7c.5.5 1.3.5 1.8 0l1.4-1.4c.5-.5.5-1.3 0-1.8C15.2 4.7 8.8 4.7 4.5 9.3c-.5.5-.5 1.3 0 1.8l1.4 1.4c.5.5 1.3.5 1.8 0l1.7-1.7z"
                />
              </svg>
            </span>

            <span>Cancel</span>
          </button>

        </template>

      </div>

      <!-- Keypad -->
      <Transition name="keypad-fade">
        <div
          v-if="showKeypad && connected"
          class="keypad-panel"
        >
          <div class="keypad-display-row">
            <div class="keypad-display">
              {{ keypadInput || " " }}
            </div>

            <button
              type="button"
              class="keypad-backspace"
              title="Delete last digit"
              aria-label="Delete last digit"
              :disabled="!keypadInput"
              @click="deleteLastDigit"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M9 6h10a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9l-5-6 5-6z" />
                <path d="M13 10.5l4 3M17 10.5l-4 3" />
              </svg>
            </button>
          </div>

          <div class="keypad">
            <button
              v-for="key in keypadKeys"
              :key="key"
              type="button"
              @click="sendDigit(key)"
            >
              {{ key }}
            </button>
          </div>
        </div>
      </Transition>

      </div>

    </div>

    </Transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue"

const visible = ref(false)
const calling = ref(false)
const connected = ref(false)
const phoneNumber = ref("")
const status = ref("")
const activeCall = ref(null)
const minimized = ref(false)
const muted = ref(false)
const showKeypad = ref(false)
const keypadInput = ref("")
const elapsedSeconds = ref(0)

const title = ref("Make Call")

const keypadKeys = [
  "1", "2", "3",
  "4", "5", "6",
  "7", "8", "9",
  "*", "0", "#",
]

let timer = null

const statusText = computed(() => {
  if (connected.value) return "Connected"
  if (status.value === "ringing") return "Ringing..."
  if (status.value === "initiating") return "Initiating call..."
  if (calling.value) return "Calling..."
  return "Ready"
})

const formattedDuration = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60)
  const seconds = elapsedSeconds.value % 60

  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
})

const initials = computed(() => {
  const value = title.value || "Call"

  return value
    .split(" ")
    .map((word) => word.charAt(0))
    .join("")
    .slice(0, 2)
    .toUpperCase()
})

function startTimer() {
  stopTimer()

  elapsedSeconds.value = 0

  timer = setInterval(() => {
    elapsedSeconds.value += 1
  }, 1000)
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function startCall(call, number, contactName = "Make Call") {
  activeCall.value = call
  phoneNumber.value = number
  title.value = contactName || "Make Call"

  visible.value = true
  minimized.value = false
  calling.value = true
  connected.value = false
  muted.value = false
  showKeypad.value = false
  keypadInput.value = ""
  elapsedSeconds.value = 0
  status.value = "initiating"

  call.on("accept", () => {
    calling.value = true
    connected.value = false
    status.value = "ringing"
  })

  call.on("messageReceived", (message) => {
    const info = message.content

    if (info?.CallStatus === "in-progress") {
      calling.value = false
      connected.value = true
      status.value = "in-progress"
      startTimer()
    }
  })

  call.on("disconnect", () => {
    reset()
  })

  call.on("cancel", () => {
    reset()
  })

  call.on("error", (error) => {
    console.error("Twilio call error:", error)
    reset()
  })
}

function cancelCall() {
  if (activeCall.value) {
    activeCall.value.disconnect()
  }

  reset()
}

function hangUpCall() {
  if (activeCall.value) {
    activeCall.value.disconnect()
  }

  reset()
}

function endCall() {
  if (activeCall.value) {
    activeCall.value.disconnect()
  }

  reset()
}

function toggleMute() {
  if (!activeCall.value) return

  muted.value = !muted.value

  activeCall.value.mute(muted.value)
}

function sendDigit(digit) {
  if (!activeCall.value || !connected.value) return

  keypadInput.value += digit

  if (typeof activeCall.value.sendDigits === "function") {
    activeCall.value.sendDigits(digit)
  }
}

function deleteLastDigit() {
  if (!keypadInput.value) return

  keypadInput.value = keypadInput.value.slice(0, -1)
}

function reset() {
  stopTimer()

  visible.value = false
  calling.value = false
  connected.value = false
  phoneNumber.value = ""
  status.value = ""
  activeCall.value = null
  minimized.value = false
  muted.value = false
  showKeypad.value = false
  keypadInput.value = ""
  elapsedSeconds.value = 0
}

onBeforeUnmount(() => {
  stopTimer()
})

defineExpose({
  startCall,
  cancelCall,
  hangUpCall,
})
</script>

<style scoped>
.call-popup {
  --glass-bg: rgba(255, 255, 255, 0.72);
  --glass-bg-strong: rgba(255, 255, 255, 0.88);
  --glass-border: rgba(255, 255, 255, 0.6);
  --coral: #ef6a52;
  --coral-dark: #dc4c3f;
  --coral-tint: rgba(239, 106, 82, 0.12);
  --ink: #1f2430;
  --muted: #6b7280;

  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 344px;
  z-index: 9999;
  color: var(--ink);
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}

/* Ambient coral glow bleeding past the card edges — this is what
   sells the glass even when the page behind it is plain white,
   since it doesn't depend on backdrop-filter picking up detail. */
.call-glow {
  position: absolute;
  inset: -34px;
  z-index: -1;
  border-radius: 40px;
  background:
    radial-gradient(40% 36% at 22% 4%, rgba(255, 255, 255, 0.5), transparent 70%),
    radial-gradient(48% 42% at 16% 10%, rgba(239, 106, 82, 0.26), transparent 70%),
    radial-gradient(46% 46% at 88% 92%, rgba(239, 106, 82, 0.14), transparent 70%);
  filter: blur(36px);
  opacity: 0.8;
  pointer-events: none;
}

.call-surface {
  position: relative;
  isolation: isolate;
  background-color: rgba(255, 255, 255, 0.5);
  background-image:
    linear-gradient(165deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.16) 45%, rgba(255, 255, 255, 0.4) 100%),
    radial-gradient(120% 60% at 12% -10%, rgba(239, 106, 82, 0.1), transparent 55%);
  -webkit-backdrop-filter: blur(30px) saturate(190%);
  backdrop-filter: blur(30px) saturate(190%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow:
    0 4px 12px rgba(17, 24, 39, 0.05),
    0 16px 40px rgba(17, 24, 39, 0.12),
    0 32px 70px rgba(17, 24, 39, 0.14),
    0 0 0 1px rgba(239, 106, 82, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    inset 0 -20px 36px -28px rgba(239, 106, 82, 0.1);
  overflow: hidden;
  transition: box-shadow 0.25s ease;
}

.call-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.04));
  border-bottom: 1px solid rgba(255, 255, 255, 0.45);
}

.contact-info {
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

.contact-details {
  min-width: 0;
}

.contact-name {
  font-size: 14.5px;
  font-weight: 650;
  letter-spacing: -0.01em;
  color: var(--ink);
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.phone-number {
  margin-top: 2px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.3;
  font-variant-numeric: tabular-nums;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
  flex-shrink: 0;
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
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease, transform 0.12s ease;
}

.icon-button:hover {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(17, 24, 39, 0.05);
  color: var(--ink);
}

.icon-button:active {
  transform: scale(0.94);
}

.icon-button:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.icon-button svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.call-content {
  padding: 18px 20px 14px;
  text-align: center;
}

.call-indicator {
  position: relative;
  width: 56px;
  height: 56px;
  margin: 0 auto 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.35);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow:
    0 4px 14px rgba(17, 24, 39, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  color: #8a8f99;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.call-indicator svg {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  position: relative;
  z-index: 1;
}

.call-indicator svg.waveform {
  fill: currentColor;
  stroke: none;
}

.eq-bar {
  transform-box: fill-box;
  transform-origin: center;
  animation: eq-bounce 1.1s ease-in-out infinite;
}

.eq-bar-1 { animation-delay: 0s; }
.eq-bar-2 { animation-delay: 0.12s; }
.eq-bar-3 { animation-delay: 0.24s; }
.eq-bar-4 { animation-delay: 0.36s; }

@keyframes eq-bounce {
  0%, 100% {
    transform: scaleY(0.55);
  }
  50% {
    transform: scaleY(1);
  }
}

.call-indicator.active {
  background: rgba(239, 106, 82, 0.14);
  border-color: rgba(239, 106, 82, 0.26);
  color: var(--coral);
  box-shadow:
    0 4px 14px rgba(239, 106, 82, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  animation: glow-breathe 2.6s ease-in-out infinite;
}

@keyframes glow-breathe {
  0%, 100% {
    box-shadow:
      0 4px 14px rgba(239, 106, 82, 0.14),
      inset 0 1px 0 rgba(255, 255, 255, 0.7);
  }
  50% {
    box-shadow:
      0 4px 20px rgba(239, 106, 82, 0.24),
      inset 0 1px 0 rgba(255, 255, 255, 0.7);
  }
}

.call-indicator.pulsing {
  background: rgba(239, 106, 82, 0.14);
  border-color: rgba(239, 106, 82, 0.24);
  color: var(--coral);
  box-shadow:
    0 4px 14px rgba(239, 106, 82, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.call-indicator.pulsing::before,
.call-indicator.pulsing::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(239, 106, 82, 0.4);
  animation: call-ripple 2.1s ease-out infinite;
}

.call-indicator.pulsing::after {
  animation-delay: 0.9s;
}

@keyframes call-ripple {
  0% {
    transform: scale(1);
    opacity: 0.4;
  }
  100% {
    transform: scale(1.35);
    opacity: 0;
  }
}

.duration {
  min-height: 26px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
  transition: color 0.2s ease;
}

.call-status {
  margin-top: 2px;
  font-size: 12.5px;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: var(--muted);
  transition: color 0.2s ease;
}

.call-status.live::before {
  content: "";
  display: inline-block;
  width: 5px;
  height: 5px;
  margin-right: 6px;
  border-radius: 50%;
  background: var(--coral);
  vertical-align: middle;
  animation: status-dot-pulse 1.4s ease-in-out infinite;
}

@keyframes status-dot-pulse {
  0%, 100% {
    opacity: 0.35;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

.call-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  padding: 4px 20px 18px;
}

.action {
  min-width: 72px;
  border: 0;
  background: transparent;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: #4b5160;
  font-size: 11.5px;
  font-weight: 500;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.45);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.75);
  box-shadow: 0 2px 8px rgba(17, 24, 39, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b5563;
  transition:
    background 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease,
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.action-icon svg {
  width: 19px;
  height: 19px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.action:hover .action-icon {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(17, 24, 39, 0.08);
}

.action:active .action-icon {
  transform: scale(0.94);
}

.action:focus-visible .action-icon {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.action.active .action-icon {
  background: var(--coral-tint);
  border-color: rgba(239, 106, 82, 0.3);
  color: var(--coral);
}

.action.hangup .action-icon,
.action.cancel .action-icon {
  background: linear-gradient(180deg, #f0705a, var(--coral-dark));
  border-color: transparent;
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(220, 76, 63, 0.35);
}

.action.hangup:hover .action-icon,
.action.cancel:hover .action-icon {
  background: linear-gradient(180deg, #ea5c44, #c9433a);
  box-shadow: 0 8px 20px rgba(220, 76, 63, 0.42);
}

.action.hangup,
.action.cancel {
  color: var(--coral-dark);
  font-weight: 600;
}

.keypad-panel {
  position: relative;
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  padding-top: 12px;
  background:
    linear-gradient(180deg, rgba(239, 106, 82, 0.04), transparent 40%),
    rgba(255, 255, 255, 0.2);
}

.keypad-display-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 20px 10px;
}

.keypad-display {
  flex: 1;
  min-width: 0;
  min-height: 36px;
  padding: 8px 14px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  color: var(--ink);
  text-align: center;
  font-size: 18px;
  font-weight: 500;
  letter-spacing: 3px;
  font-variant-numeric: tabular-nums;
  display: flex;
  align-items: center;
  justify-content: center;
}

.keypad-backspace {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.28);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
  color: #8a8f99;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease,
    transform 0.12s ease,
    opacity 0.15s ease;
}

.keypad-backspace svg {
  width: 17px;
  height: 17px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.keypad-backspace:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(17, 24, 39, 0.08);
  color: var(--coral-dark);
}

.keypad-backspace:active:not(:disabled) {
  transform: scale(0.92);
  background: rgba(239, 106, 82, 0.14);
  border-color: rgba(239, 106, 82, 0.28);
}

.keypad-backspace:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.keypad-backspace:disabled {
  opacity: 0.4;
  cursor: default;
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 7px;
  padding: 0 20px 18px;
}

.keypad button {
  height: 38px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.38);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  box-shadow: 0 1px 3px rgba(17, 24, 39, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.7);
  color: var(--ink);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.12s ease, transform 0.12s ease, border-color 0.12s ease;
}

.keypad button:hover {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(17, 24, 39, 0.08);
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(17, 24, 39, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.keypad button:active {
  transform: scale(0.94);
  background: rgba(239, 106, 82, 0.18);
  border-color: rgba(239, 106, 82, 0.3);
  color: var(--coral-dark);
}

.keypad button:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.keypad-fade-enter-active,
.keypad-fade-leave-active {
  transition: opacity 0.18s ease, max-height 0.22s ease;
  max-height: 220px;
  overflow: hidden;
}

.keypad-fade-enter-from,
.keypad-fade-leave-to {
  opacity: 0;
  max-height: 0;
}

.mode-swap-enter-active,
.mode-swap-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.mode-swap-enter-from {
  opacity: 0;
  transform: translateY(6px) scale(0.98);
}

.mode-swap-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.99);
}

.call-mini-bar {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 288px;
  min-height: 56px;
  padding: 6px 8px 6px 12px;
  background-color: rgba(255, 255, 255, 0.54);
  background-image:
    linear-gradient(160deg, rgba(255, 255, 255, 0.58), rgba(255, 255, 255, 0.2)),
    radial-gradient(90% 90% at 10% 0%, rgba(239, 106, 82, 0.1), transparent 60%);
  -webkit-backdrop-filter: blur(26px) saturate(190%);
  backdrop-filter: blur(26px) saturate(190%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 999px;
  box-shadow:
    0 3px 10px rgba(17, 24, 39, 0.05),
    0 14px 34px rgba(17, 24, 39, 0.15),
    0 0 0 1px rgba(239, 106, 82, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.85);
  display: flex;
  align-items: center;
  z-index: 9999;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}

.call-mini-bar::before {
  content: "";
  position: absolute;
  inset: -20px;
  z-index: -1;
  border-radius: 999px;
  background:
    radial-gradient(35% 55% at 20% 15%, rgba(255, 255, 255, 0.45), transparent 70%),
    radial-gradient(60% 60% at 15% 20%, rgba(239, 106, 82, 0.22), transparent 70%);
  filter: blur(28px);
  opacity: 0.8;
  pointer-events: none;
}

.mini-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 9px;
}

.mini-brand {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mini-brand img {
  width: 17px;
  height: 17px;
  object-fit: contain;
}

.mini-dot {
  position: relative;
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--coral, #ef6a52);
}

.mini-dot.pulsing::after {
  content: "";
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1.5px solid rgba(239, 106, 82, 0.5);
  animation: call-ripple 1.8s ease-out infinite;
}

.mini-dot.connected {
  background: #22c55e;
}

.mini-dot.connected::after {
  display: none;
}

.mini-text {
  min-width: 0;
}

.mini-name {
  color: #1f2430;
  font-size: 13.5px;
  font-weight: 650;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-status {
  margin-top: 1px;
  color: #6b7280;
  font-size: 11.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-status-sep {
  margin: 0 3px;
  opacity: 0.6;
}

.mini-expand {
  width: 32px;
  height: 32px;
  margin-right: 4px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.4);
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s ease, color 0.15s ease, transform 0.12s ease;
}

.mini-expand svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.mini-expand:hover {
  background: rgba(255, 255, 255, 0.85);
  color: var(--ink, #1f2430);
}

.mini-expand:active {
  transform: scale(0.92);
}

.mini-expand:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.mini-hangup {
  width: 38px;
  height: 38px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: linear-gradient(180deg, #f0705a, #dc4c3f);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(220, 76, 63, 0.35);
  transition: background 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}

.mini-hangup svg {
  width: 17px;
  height: 17px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.mini-hangup:hover {
  background: linear-gradient(180deg, #ea5c44, #c9433a);
  box-shadow: 0 6px 16px rgba(220, 76, 63, 0.42);
  transform: translateY(-1px);
}

.mini-hangup:active {
  transform: scale(0.92);
}

.mini-hangup:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.55);
  outline-offset: 2px;
}

@media (max-width: 480px) {
  .call-popup {
    right: 12px;
    left: 12px;
    bottom: 12px;
    width: auto;
  }

  .call-mini-bar {
    right: 12px;
    left: 12px;
    bottom: 12px;
    width: auto;
  }

  .call-actions {
    gap: 8px;
  }

  .action {
    min-width: 0;
    flex: 1;
  }

  .keypad {
    padding: 0 16px 16px;
  }

  .keypad-display {
    margin: 0 16px 10px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .call-indicator.pulsing::before,
  .call-indicator.pulsing::after,
  .call-indicator.active,
  .mini-dot.pulsing::after,
  .eq-bar,
  .call-status.live::before {
    animation: none;
  }

  .mode-swap-enter-active,
  .mode-swap-leave-active,
  .keypad-fade-enter-active,
  .keypad-fade-leave-active {
    transition: none;
  }
}
</style>
