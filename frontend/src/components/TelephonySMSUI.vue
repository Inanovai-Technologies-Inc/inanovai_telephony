<template>
  <Transition name="sms-fade">
    <div
      v-if="visible"
      class="sms-overlay"
      @mousedown.self="handleClose"
    >
      <div
        class="sms-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="sms-ui-title"
      >
        <div class="sms-glow" aria-hidden="true"></div>

        <div class="sms-surface">

          <!-- Header -->
          <div class="sms-header">
            <div class="sms-header-info">
              <div class="brand-mark">
                <img
                  src="https://inanovai.com/files/Inanovai%20Logo%20without%20background.png"
                  alt="Inanovai"
                />
              </div>

              <div class="sms-header-text">
                <div id="sms-ui-title" class="sms-title">Send SMS</div>
                <div class="sms-subtitle">Send a message to this contact</div>
              </div>
            </div>

            <button
              type="button"
              class="icon-button"
              title="Close"
              aria-label="Close"
              :disabled="sending"
              @click="handleClose"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>

          <template v-if="!success">

            <!-- Body -->
            <div class="sms-body">
              <div class="sms-field">
                <label class="sms-label">To</label>

                <div class="sms-recipient">
                  <svg class="sms-recipient-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M6.6 10.8c2.9 2.3 5.1 2.3 8 0l1.7 1.7c.5.5 1.3.5 1.8 0l1.4-1.4c.5-.5.5-1.3 0-1.8C15.2 4.7 8.8 4.7 4.5 9.3c-.5.5-.5 1.3 0 1.8l1.4 1.4c.5.5 1.3.5 1.8 0l1.7-1.7z"
                    />
                  </svg>
                  <span>{{ phoneNumber || "—" }}</span>
                </div>
              </div>

              <div class="sms-field">
                <div class="sms-field-header">
                  <label class="sms-label" for="sms-message-input">Message</label>
                  <span class="sms-char-count">{{ message.length }}</span>
                </div>

                <textarea
                  id="sms-message-input"
                  ref="messageInput"
                  v-model="message"
                  class="sms-textarea"
                  placeholder="Type your message..."
                  rows="5"
                  :disabled="sending"
                ></textarea>
              </div>
            </div>

            <!-- Actions -->
            <div class="sms-actions">
              <button
                type="button"
                class="sms-btn sms-btn-secondary"
                :disabled="sending"
                @click="handleClose"
              >
                Cancel
              </button>

              <button
                type="button"
                class="sms-btn sms-btn-primary"
                :disabled="!canSend"
                @click="handleSend"
              >
                <span v-if="sending" class="sms-spinner" aria-hidden="true"></span>
                <span>{{ sending ? "Sending..." : "Send SMS" }}</span>
              </button>
            </div>

          </template>

          <!-- Success -->
          <div v-else class="sms-success">
            <div class="sms-success-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div class="sms-success-text">SMS sent successfully.</div>
          </div>

        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue"

const emit = defineEmits(["send"])

const visible = ref(false)
const phoneNumber = ref("")
const message = ref("")
const sending = ref(false)
const success = ref(false)
const messageInput = ref(null)

const canSend = computed(() => !sending.value && message.value.trim().length > 0)

function open(number, initialMessage = "") {
  phoneNumber.value = number || ""
  message.value = initialMessage || ""
  sending.value = false
  success.value = false
  visible.value = true

  nextTick(() => {
    messageInput.value?.focus()
  })
}

function close() {
  if (sending.value) return

  visible.value = false
  message.value = ""
  success.value = false
}

function handleClose() {
  close()
}

function setSending(value) {
  sending.value = value
}

function showSuccess() {
  sending.value = false
  success.value = true
}

function handleSend() {
  if (!canSend.value) return

  sending.value = true

  emit("send", {
    to: phoneNumber.value,
    message: message.value.trim(),
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
})

defineExpose({
  open,
  close,
  setSending,
  showSuccess,
})
</script>

<style scoped>
.sms-overlay {
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

.sms-modal {
  position: relative;
  width: 100%;
  max-width: 400px;
  --coral: #ef6a52;
  --coral-dark: #dc4c3f;
  --ink: #1f2430;
  --muted: #6b7280;
  color: var(--ink);
}

.sms-glow {
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

.sms-surface {
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

.sms-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 16px 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.04));
  border-bottom: 1px solid rgba(255, 255, 255, 0.45);
}

.sms-header-info {
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

.sms-header-text {
  min-width: 0;
}

.sms-title {
  font-size: 15.5px;
  font-weight: 650;
  letter-spacing: -0.01em;
  color: var(--ink);
  line-height: 1.3;
}

.sms-subtitle {
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

.sms-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px 20px;
}

.sms-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 34px 20px 38px;
  text-align: center;
}

.sms-success-icon {
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
}

.sms-success-icon svg {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sms-success-text {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink);
}

.sms-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sms-field-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.sms-label {
  font-size: 11.5px;
  font-weight: 650;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted);
}

.sms-char-count {
  font-size: 11px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.sms-recipient {
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
  color: var(--ink);
  font-size: 14.5px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.sms-recipient-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  fill: none;
  stroke: var(--coral);
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sms-textarea {
  width: 100%;
  min-height: 118px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.4);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  color: var(--ink);
  font: inherit;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.sms-textarea::placeholder {
  color: rgba(107, 114, 128, 0.75);
}

.sms-textarea:focus {
  outline: none;
  border-color: rgba(239, 106, 82, 0.45);
  background: rgba(255, 255, 255, 0.55);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 0 0 3px rgba(239, 106, 82, 0.14);
}

.sms-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sms-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 20px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.5);
}

.sms-btn {
  height: 38px;
  padding: 0 18px;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition:
    background 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease,
    transform 0.12s ease,
    box-shadow 0.15s ease;
}

.sms-btn:disabled {
  opacity: 0.55;
  cursor: default;
}

.sms-btn-secondary {
  border: 1px solid rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.35);
  color: var(--ink);
}

.sms-btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.65);
}

.sms-btn-secondary:active:not(:disabled) {
  transform: scale(0.96);
}

.sms-btn-primary {
  border: 1px solid transparent;
  background: linear-gradient(180deg, #f0705a, var(--coral-dark));
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(220, 76, 63, 0.32);
}

.sms-btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #ea5c44, #c9433a);
  box-shadow: 0 8px 20px rgba(220, 76, 63, 0.4);
}

.sms-btn-primary:active:not(:disabled) {
  transform: scale(0.96);
}

.sms-btn-secondary:focus-visible,
.sms-btn-primary:focus-visible,
.icon-button:focus-visible,
.sms-textarea:focus-visible {
  outline: 2px solid rgba(239, 106, 82, 0.45);
  outline-offset: 2px;
}

.sms-spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #ffffff;
  animation: sms-spin 0.7s linear infinite;
}

@keyframes sms-spin {
  to {
    transform: rotate(360deg);
  }
}

.sms-fade-enter-active,
.sms-fade-leave-active {
  transition: opacity 0.18s ease;
}

.sms-fade-enter-from,
.sms-fade-leave-to {
  opacity: 0;
}

.sms-fade-enter-active .sms-modal,
.sms-fade-leave-active .sms-modal {
  transition: transform 0.18s ease, opacity 0.18s ease;
}

.sms-fade-enter-from .sms-modal,
.sms-fade-leave-to .sms-modal {
  transform: translateY(8px) scale(0.98);
  opacity: 0;
}

@media (max-width: 480px) {
  .sms-overlay {
    padding: 16px;
  }

  .sms-modal {
    max-width: none;
  }

  .sms-actions {
    flex-direction: column-reverse;
  }

  .sms-btn {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sms-fade-enter-active,
  .sms-fade-leave-active,
  .sms-fade-enter-active .sms-modal,
  .sms-fade-leave-active .sms-modal {
    transition: none;
  }

  .sms-spinner {
    animation: none;
  }
}
</style>
