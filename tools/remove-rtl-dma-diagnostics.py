#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "components/rtl_sdr_v4_esp/src/rtl_sdr_v4_esp.cpp"
text = p.read_text()

repls = [
("static void dma_diag(const char *stage)\n{\n    ESP_LOGI(TAG, \"RTL_DMA_DIAG stage=%s dma_free=%u dma_largest=%u int_free=%u int_largest=%u psram_free=%u\",\n             stage,\n             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_DMA)),\n             static_cast<unsigned>(heap_caps_get_largest_free_block(MALLOC_CAP_DMA)),\n             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),\n             static_cast<unsigned>(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL)),\n             static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)));\n}\n\n", ""),
("        dma_diag(\"before_usb_host_install\");\n", ""),
("        dma_diag(\"after_usb_host_install\");\n", ""),
("    dma_diag(\"before_ctrl_xfer_alloc\");\n", ""),
("    dma_diag(\"after_ctrl_xfer_alloc\");\n", ""),
("    dma_diag(\"ensure_ring_enter\");\n", ""),
("    dma_diag(\"after_ring_queues\");\n", ""),
("        char dma_stage[40];\n        std::snprintf(dma_stage, sizeof(dma_stage), \"after_ring_slot_%u\", static_cast<unsigned>(i));\n        dma_diag(dma_stage);\n", ""),
("    dma_diag(\"before_bulk_pool\");\n", ""),
("        char dma_stage[40];\n        std::snprintf(dma_stage, sizeof(dma_stage), \"after_bulk_urb_%u\", static_cast<unsigned>(i));\n        dma_diag(dma_stage);\n", ""),
]

changed = False
for old, new in repls:
    if old in text:
        text = text.replace(old, new)
        changed = True

if not changed:
    print("No DMA diagnostics found; nothing to remove.")
else:
    p.write_text(text)
    print("RTL-SDR DMA diagnostics removed.")
