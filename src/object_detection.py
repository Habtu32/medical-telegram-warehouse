import os
import glob
import torch
from ultralytics import YOLO
from loguru import logger
import pandas as pd

# Paths
RAW_IMAGES_DIR = os.path.join("data", "raw", "images")
DETECTION_RESULTS_DIR = os.path.join("data", "processed", "detection_results")

# Ensure processed directory exists
os.makedirs(DETECTION_RESULTS_DIR, exist_ok=True)

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        # Using nano model for speed/demo, upgrade to larger model (e.g. yolov8m.pt) for better accuracy
        self.model = YOLO(model_path)
        logger.info(f"Loaded YOLO model: {model_path}")

    def process_images(self):
        images = glob.glob(os.path.join(RAW_IMAGES_DIR, "*.jpg"))
        
        if not images:
            logger.warning("No images found to process.")
            return

        all_results = []
        
        logger.info(f"Starting detection on {len(images)} images...")
        
        # Batch inference
        results = self.model(images, stream=True)  # stream=True for generator to handle memory better
        
        for result in results:
            path = result.path
            filename = os.path.basename(path)
            
            # detections
            boxes = result.boxes
            for box in boxes:
                # bounding box
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                # confidence
                conf = box.conf[0].item()
                # class id
                cls_id = int(box.cls[0].item())
                # class name
                cls_name = result.names[cls_id]
                
                all_results.append({
                    "image_file": filename,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": cls_name
                })
        
        # Save results to CSV
        if all_results:
            df = pd.DataFrame(all_results)
            output_file = os.path.join(DETECTION_RESULTS_DIR, "yolo_detections.csv")
            df.to_csv(output_file, index=False)
            logger.success(f"Saved detection results for {len(df)} objects to {output_file}")
            
            # Summary
            logger.info("Detection Summary by Class:")
            logger.info(df['class_name'].value_counts())

if __name__ == "__main__":
    detector = ObjectDetector()
    detector.process_images()
