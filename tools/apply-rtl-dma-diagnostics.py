#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "components/rtl_sdr_v4_esp/src/rtl_sdr_v4_esp.cpp"
text = p.read_text()


def replace_once(old: str, new: str, label: str):
    global text
    if new in text:
        print(f"already patched: {label}")
        return
    if old not in text:
        raise SystemExit(f"marker not found: {label}")
    text = text.replace(old, new, 1)
    print(f"patched: {label}")

replace_once(
    "static uint32_t now_ms(void)\n{\n",
    "static void dma_diag(const char *stage)\n{\n"
    "    ESP_LOGI(TAG, \"RTL_DMA_DIAG stage=%s dma_free=%u dma_largest=%u int_free=%u int_largest=%u psram_free=%u\",\n"
    "             stage,\n"
    "             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_DMA)),\n"
    "             static_cast<unsigned>(heap_caps_get_largest_free_block(MALLOC_CAP_DMA)),\n"
    "             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),\n"
    "             static_cast<unsigned>(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL)),\n"
    "             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)));\n"
    "}\n\n"
    "static uint32_t now_ms(void)\n{\n",
    "dma helper",
)

replace_once(
    "        esp_err_t ret = usb_host_install(&hc);\n",
    "        dma_diag(\"before_usb_host_install\");\n"
    "        esp_err_t ret = usb_host_install(&hc);\n",
    "before usb_host_install",
)

replace_once(
    "        h->host_installed = true;\n",
    "        h->host_installed = true;\n"
    "        dma_diag(\"after_usb_host_install\");\n",
    "after usb_host_install",
)

replace_once(
    "    if (usb_host_transfer_alloc(kCtrlXferBytes, 0, &h->ctrl_xfer) != ESP_OK) {\n",
    "    dma_diag(\"before_ctrl_xfer_alloc\");\n"
    "    if (usb_host_transfer_alloc(kCtrlXferBytes, 0, &h->ctrl_xfer) != ESP_OK) {\n",
    "before control transfer alloc",
)

replace_once(
    "    h->info.vid = kVid;\n",
    "    dma_diag(\"after_ctrl_xfer_alloc\");\n"
    "    h->info.vid = kVid;\n",
    "after control transfer alloc",
)

replace_once(
    "static esp_err_t ensure_ring(rtl_sdr_v4_esp_handle *h, size_t slot_bytes)\n{\n    if (h->free_q != nullptr) {\n",
    "static esp_err_t ensure_ring(rtl_sdr_v4_esp_handle *h, size_t slot_bytes)\n{\n"
    "    dma_diag(\"ensure_ring_enter\");\n"
    "    if (h->free_q != nullptr) {\n",
    "ring enter",
)

replace_once(
    "    if (h->free_q == nullptr || h->filled_q == nullptr) {\n        return ESP_ERR_NO_MEM;\n    }\n",
    "    if (h->free_q == nullptr || h->filled_q == nullptr) {\n"
    "        return ESP_ERR_NO_MEM;\n"
    "    }\n"
    "    dma_diag(\"after_ring_queues\");\n",
    "ring queues",
)

replace_once(
    "        IqSlot *p = &h->ring[i];\n",
    "        char dma_stage[40];\n"
    "        std::snprintf(dma_stage, sizeof(dma_stage), \"after_ring_slot_%u\", static_cast<unsigned>(i));\n"
    "        dma_diag(dma_stage);\n"
    "        IqSlot *p = &h->ring[i];\n",
    "ring slots",
)

replace_once(
    "    h->bulk_num = num;\n    h->bulk_len = len;\n    for (uint32_t i = 0; i < num; ++i) {\n",
    "    h->bulk_num = num;\n"
    "    h->bulk_len = len;\n"
    "    dma_diag(\"before_bulk_pool\");\n"
    "    for (uint32_t i = 0; i < num; ++i) {\n",
    "bulk pool enter",
)

replace_once(
    "        h->bulk[i]->device_handle = h->dev;\n",
    "        char dma_stage[40];\n"
    "        std::snprintf(dma_stage, sizeof(dma_stage), \"after_bulk_urb_%u\", static_cast<unsigned>(i));\n"
    "        dma_diag(dma_stage);\n"
    "        h->bulk[i]->device_handle = h->dev;\n",
    "bulk URBs",
)

p.write_text(text)
print("RTL-SDR DMA diagnostics applied.")
