<template>
  <div v-if="visible">

    <!-- Minimized call bar -->
    <div v-if="minimized" class="call-mini-bar">
      <div class="mini-info">
        <div class="mini-dot" :class="{ connected }"></div>

        <div class="mini-text">
          <div class="mini-name">{{ title }}</div>
          <div class="mini-status">
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
        ↗
      </button>

      <button
        type="button"
        class="mini-hangup"
        title="End call"
        @click="endCall"
      >
        ☎
      </button>
    </div>

    <!-- Expanded call card -->
    <div v-else class="call-popup">

      <div class="call-header">
        <div class="contact-info">
          <div class="avatar">
            {{ initials }}
          </div>

          <div>
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
            ↘
          </button>
        </div>
      </div>

      <div class="call-content">

        <div class="call-indicator" :class="{ active: connected }">
          <span v-if="connected">〽</span>
          <span v-else>☎</span>
        </div>

        <div class="duration">
          {{ connected ? formattedDuration : "" }}
        </div>

        <div class="call-status">
          {{ statusText }}
        </div>
      </div>

      <div class="call-actions">

        <template v-if="connected">

          <button
            type="button"
            class="action"
            :class="{ active: muted }"
            @click="toggleMute"
          >
            <span class="action-icon">🎙</span>
            <span>{{ muted ? "Unmute" : "Mute" }}</span>
          </button>

          <button
            type="button"
            class="action"
            @click="showKeypad = !showKeypad"
          >
            <span class="action-icon">⠿</span>
            <span>Keypad</span>
          </button>

          <button
            type="button"
            class="action hangup"
            @click="hangUpCall"
          >
            <span class="action-icon">☎</span>
            <span>Hang Up</span>
          </button>

        </template>

        <template v-else>

          <button
            type="button"
            class="action cancel"
            @click="cancelCall"
          >
            <span class="action-icon">☎</span>
            <span>Cancel</span>
          </button>

        </template>

      </div>
      <div v-if="showKeypad && connected" class="keypad-display">
      {{ keypadInput || " " }}
      </div>
      <div v-if="showKeypad && connected" class="keypad">
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
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 360px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.16);
  overflow: hidden;
  z-index: 9999;
}

.call-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid #eeeeee;
}

.contact-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  color: #475569;
}

.contact-name {
  font-size: 17px;
  font-weight: 600;
  color: #111827;
}

.phone-number {
  margin-top: 3px;
  font-size: 13px;
  color: #6b7280;
}

.header-actions {
  display: flex;
}

.icon-button {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  font-size: 19px;
  color: #6b7280;
}

.icon-button:hover {
  background: #f3f4f6;
}

.call-content {
  padding: 30px 20px 24px;
  text-align: center;
}

.call-indicator {
  width: 64px;
  height: 64px;
  margin: 0 auto 14px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 27px;
  color: #64748b;
}

.call-indicator.active {
  background: #ecfdf5;
  color: #16a34a;
}

.duration {
  min-height: 25px;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.call-status {
  margin-top: 4px;
  font-size: 14px;
  color: #6b7280;
}

.call-actions {
  display: flex;
  justify-content: center;
  gap: 18px;
  padding: 8px 20px 24px;
}

.action {
  min-width: 76px;
  border: 0;
  background: transparent;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 7px;
  color: #374151;
  font-size: 12px;
}

.action-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.action:hover .action-icon {
  background: #e5e7eb;
}

.action.active .action-icon {
  background: #fee2e2;
}

.action.hangup .action-icon,
.action.cancel .action-icon {
  background: #ef4444;
  color: white;
}

.action.hangup,
.action.cancel {
  color: #dc2626;
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 0 28px 24px;
}

.keypad button {
  height: 42px;
  border: 0;
  border-radius: 8px;
  background: #f3f4f6;
  cursor: pointer;
  font-size: 16px;
}

.keypad button:hover {
  background: #e5e7eb;
}

/* Minimized call bar */

.call-mini-bar {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 300px;
  min-height: 64px;
  padding: 8px 10px 8px 14px;
  background: #171717;
  border-radius: 12px;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  z-index: 9999;
}

.mini-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mini-dot {
  width: 9px;
  height: 9px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: #60a5fa;
}

.mini-dot.connected {
  background: #22c55e;
}

.mini-name {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.mini-status {
  margin-top: 2px;
  color: #d1d5db;
  font-size: 12px;
}

.mini-expand {
  width: 34px;
  height: 34px;
  margin-right: 5px;
  border: 0;
  background: transparent;
  color: #d1d5db;
  cursor: pointer;
  font-size: 18px;
}

.mini-hangup {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  cursor: pointer;
  font-size: 18px;
}

.mini-hangup:hover {
  background: #dc2626;
}

.keypad-display {
  margin: 0 28px 12px;
  min-height: 42px;
  padding: 10px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fafafa;
  color: #111827;
  text-align: center;
  font-size: 20px;
  font-weight: 500;
  letter-spacing: 3px;
  font-variant-numeric: tabular-nums;
}
</style>
