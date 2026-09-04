#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "apps/orcsdr-tab5/ui/main.cpp"
s = p.read_text()

if "RTL_FM_DSP_TASK ready" in s:
    print("already patched: dedicated FM DSP task")
    raise SystemExit(0)

# Add async FM DSP storage next to modern-driver stream state.
old = '''static float g_stream_audio_scale = 5500.0f;
static RtlBand g_stream_band = RtlBand::fm;
'''
new = '''static float g_stream_audio_scale = 5500.0f;
static RtlBand g_stream_band = RtlBand::fm;
constexpr uint8_t kFmDspSlotCount = 2;
constexpr size_t kFmDspSlotBytes = 32768 + 512;
static uint8_t* fm_dsp_slots[kFmDspSlotCount]{};
static size_t fm_dsp_sizes[kFmDspSlotCount]{};
static QueueHandle_t fm_dsp_free = nullptr;
static QueueHandle_t fm_dsp_ready = nullptr;
static std::atomic<uint32_t> fm_dsp_queue_drops{0};
'''
if s.count(old) != 1:
    raise SystemExit("modern stream-state marker not found uniquely; source unchanged")
s = s.replace(old, new, 1)

# Offload only FM/WBFM first; other modes retain their proven inline paths.
old = '''        } else {
          demodulate_fm(iq->data, n, g_stream_audio_scale,
                        g_stream_band == RtlBand::fm);
        }
'''
new = '''        } else if (g_stream_band == RtlBand::fm && fm_dsp_free && fm_dsp_ready) {
          uint8_t slot = 0;
          if (xQueueReceive(fm_dsp_free, &slot, 0) == pdTRUE) {
            const size_t copy_n = n <= kFmDspSlotBytes ? n : kFmDspSlotBytes;
            std::memcpy(fm_dsp_slots[slot], iq->data, copy_n);
            fm_dsp_sizes[slot] = copy_n;
            if (xQueueSend(fm_dsp_ready, &slot, 0) != pdTRUE) {
              (void)xQueueSend(fm_dsp_free, &slot, 0);
              fm_dsp_queue_drops.fetch_add(1, std::memory_order_relaxed);
            }
          } else {
            fm_dsp_queue_drops.fetch_add(1, std::memory_order_relaxed);
          }
        } else {
          demodulate_fm(iq->data, n, g_stream_audio_scale,
                        g_stream_band == RtlBand::fm);
        }
'''
if s.count(old) != 1:
    raise SystemExit("modern inline FM marker not found uniquely; source unchanged")
s = s.replace(old, new, 1)

# Define the low-priority DSP worker immediately before the modern host initializer.
marker = '''void initialize_rtl_sdr_host() {
  adsb_iq_free = xQueueCreate(kAdsbIqBlockCount, sizeof(uint8_t));
'''
worker = '''static void fm_dsp_task(void*) {
  Serial.println("RTL_FM_DSP_TASK ready core=1 prio=3 slots=2 psram=1");
  while (true) {
    uint8_t slot = 0;
    if (xQueueReceive(fm_dsp_ready, &slot, portMAX_DELAY) != pdTRUE) continue;
    if (slot < kFmDspSlotCount && fm_dsp_slots[slot] != nullptr && fm_dsp_sizes[slot] != 0) {
      demodulate_fm(fm_dsp_slots[slot], fm_dsp_sizes[slot], g_stream_audio_scale, true);
    }
    (void)xQueueSend(fm_dsp_free, &slot, portMAX_DELAY);
    taskYIELD();
  }
}

void initialize_rtl_sdr_host() {
  fm_dsp_free = xQueueCreate(kFmDspSlotCount, sizeof(uint8_t));
  fm_dsp_ready = xQueueCreate(kFmDspSlotCount, sizeof(uint8_t));
  bool fm_dsp_ok = fm_dsp_free != nullptr && fm_dsp_ready != nullptr;
  for (uint8_t i = 0; fm_dsp_ok && i < kFmDspSlotCount; ++i) {
    fm_dsp_slots[i] = static_cast<uint8_t*>(
        heap_caps_malloc(kFmDspSlotBytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    if (fm_dsp_slots[i] == nullptr) {
      fm_dsp_ok = false;
      break;
    }
    (void)xQueueSend(fm_dsp_free, &i, 0);
  }
  if (fm_dsp_ok &&
      xTaskCreatePinnedToCore(fm_dsp_task, "fm_dsp", 8192, nullptr, 3, nullptr, 1) != pdPASS) {
    fm_dsp_ok = false;
  }
  Serial.printf("RTL_FM_DSP_TASK init=%s\\n", fm_dsp_ok ? "ok" : "fallback_inline");
  if (!fm_dsp_ok) {
    fm_dsp_free = nullptr;
    fm_dsp_ready = nullptr;
  }

  adsb_iq_free = xQueueCreate(kAdsbIqBlockCount, sizeof(uint8_t));
'''
if s.count(marker) != 1:
    raise SystemExit("modern initialize_rtl_sdr_host marker not found uniquely; source unchanged")
s = s.replace(marker, worker, 1)

p.write_text(s)
print("patched: FM/WBFM demod moved to dedicated core1 priority-3 task with two PSRAM IQ slots")
print("note: ADS-B/AM/CB/P25/LoRa paths are unchanged")
