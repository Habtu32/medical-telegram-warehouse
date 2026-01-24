from ultralytics import YOLO
import pandas as pd
import os

model = YOLO(os.path.join(os.path.dirname(__file__), "yolov8n.pt"))

# Paths relative to project root (one level above `src`)
IMAGE_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "raw", "images")
)
OUTPUT_CSV = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "yolo_detections.csv")
)

rows = []

for root, dirs, files in os.walk(IMAGE_ROOT):
    for file in files:
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(root, file)
        channel_name = os.path.basename(root)

        result = model(image_path, verbose=False)[0]

        detected_classes = []
        confidences = []

        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls)
                cls_name = model.names[cls_id]
                conf = float(box.conf)

                detected_classes.append(cls_name)
                confidences.append(conf)

        # ---- classification logic ----
        has_person = "person" in detected_classes
        has_product = any(c in ["bottle", "cup", "box"] for c in detected_classes)

        if has_person and has_product:
            category = "promotional"
        elif has_product:
            category = "product_display"
        elif has_person:
            category = "lifestyle"
        else:
            category = "other"

        rows.append({
            "channel_name": channel_name,
            "image_name": file,
            "detected_objects": ",".join(detected_classes),
            "avg_confidence": round(sum(confidences) / len(confidences), 3) if confidences else None,
            "image_category": category
        })

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False)

print(f"YOLO detection completed. {len(df)} images processed.")