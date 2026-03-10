# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import shutil
import os
from typing import List
from PIL import Image # Thêm thư viện PIL để lấy kích thước ảnh

from database import FOOD_DATA
from models.detector import detector
from models.volume import estimator

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

class ScanResult(BaseModel):
    detected_items: List[str]
    total_gram: float
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

@app.post("/scan-food", response_model=ScanResult)
async def scan_food(file: UploadFile = File(...)):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Lấy kích thước ảnh thực tế (Width, Height)
        with Image.open(temp_file) as img:
            img_width, img_height = img.size

        # 1. Nhận diện món ăn + Tọa độ khung
        # items bây giờ là list: [('pizza', (x1,y1,x2,y2)), ...]
        raw_items = detector.predict(temp_file)
        
        if not raw_items:
            raise HTTPException(status_code=404, detail="Không tìm thấy món ăn nào.")

        food_names = []
        total_calo = 0
        total_protein = 0
        total_carb = 0
        total_fat = 0
        total_gram = 0
        
        for item in raw_items:
            food_name = item[0]
            box_coords = item[1]
            
            if food_name in FOOD_DATA:
                # 2. Tính gram từ model volume (dựa trên tọa độ box)
                gram = estimator.estimate(box_coords, img_width, img_height)
                
                # Cộng dồn
                total_gram += gram
                ratio = gram / 100.0
                
                data = FOOD_DATA[food_name]
                total_calo += data["calories"] * ratio
                total_protein += data["protein"] * ratio
                total_carb += data["carbs"] * ratio
                total_fat += data["fat"] * ratio
                
                food_names.append(food_name)
        
        return ScanResult(
            detected_items=food_names,
            total_gram=round(total_gram, 1),
            total_calories=round(total_calo, 1),
            total_protein=round(total_protein, 1),
            total_carbs=round(total_carb, 1),
            total_fat=round(total_fat, 1)
        )

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)