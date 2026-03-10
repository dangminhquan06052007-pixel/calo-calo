# models/detector.py
from ultralytics import YOLO

class FoodDetector:
    def __init__(self):
        print("Dang load model AI...")
        self.model = YOLO("yolov8n.pt")
        
    def predict(self, image_path: str) -> list:
        results = self.model.predict(source=image_path, conf=0.25, verbose=False)
        
        detected_items = []
        
        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                # Lấy tọa độ khung
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = xyxy
                
                # Trả về tuple: (Tên món, Tọa độ khung)
                detected_items.append((class_name, (x1, y1, x2, y2)))
        
        return detected_items

detector = FoodDetector()