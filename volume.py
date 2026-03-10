# models/volume.py

class VolumeEstimator:
    # Sửa lại hàm nhận 3 tham số: box_coords, image_width, image_height
    def estimate(self, box_coords, image_width, image_height):
        """
        Tính gram dựa trên diện tích khung nhận diện.
        """
        x1, y1, x2, y2 = box_coords
        
        # 1. Tính diện tích khung nhận diện (pixel)
        box_area = (x2 - x1) * (y2 - y1)
        
        # 2. Tính diện tích toàn bộ ảnh
        total_area = image_width * image_height
        
        # 3. Tính tỷ lệ diện tích
        area_ratio = box_area / total_area
        
        # 4. Quy đổi ra gram
        estimated_gram = area_ratio * 1000.0 
        
        return max(50.0, round(estimated_gram, 1))

estimator = VolumeEstimator()