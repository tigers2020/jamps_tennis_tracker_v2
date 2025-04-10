"""
테스트: 정규화된 좌표로 저장되는지 확인하는 코드
"""

import os
import json
from pathlib import Path
from src.models.calibration.point_io import CalibrationPointIO
from src.utils.math.vector import Vector2D

def main():
    # 테스트 좌표 데이터 생성
    left_points = [
        Vector2D(242, 79),
        Vector2D(277, 79),
        Vector2D(379, 79),
        Vector2D(482, 79),
        Vector2D(518, 78),
        Vector2D(245, 203),
        Vector2D(375, 203),
        Vector2D(505, 204),
        Vector2D(136, 383),
        Vector2D(196, 383),
        Vector2D(540, 383),
        Vector2D(599, 383)
    ]
    
    right_points = [
        Vector2D(272, 78),
        Vector2D(306, 80),
        Vector2D(410, 79),
        Vector2D(513, 80),
        Vector2D(550, 82),
        Vector2D(283, 203),
        Vector2D(413, 203),
        Vector2D(543, 204),
        Vector2D(188, 382),
        Vector2D(246, 382),
        Vector2D(586, 382),
        Vector2D(649, 382)
    ]
    
    # 테스트용 파일 경로 (현재 디렉토리에 저장)
    test_file = os.path.join(os.getcwd(), "test_calibration_points.json")
    print(f"저장할 파일 경로: {test_file}")
    
    # PointIO 인스턴스 생성
    point_io = CalibrationPointIO()
    
    # 해상도 설정 (1080p = 1920x1080)
    resolution = "1080p"
    width, height = point_io.STANDARD_RESOLUTIONS[resolution]
    print(f"사용할 해상도: {resolution} ({width}x{height})")
    
    # 저장 전 좌표 출력 (픽셀 기반)
    print("\n원본 좌표 (픽셀):")
    print(f"좌측 첫 좌표: ({left_points[0].x}, {left_points[0].y})")
    
    # 정규화된 좌표 수동 계산
    norm_x = left_points[0].x / width
    norm_y = left_points[0].y / height
    print(f"정규화 예상 값: ({norm_x:.4f}, {norm_y:.4f})")
    
    # 'left_key_points'와 'right_key_points'에 저장
    success, filepath = point_io.save_points(
        left_points, 
        right_points, 
        filepath=test_file,
        resolution=resolution
    )
    
    if success:
        print(f"\n저장 성공: {filepath}")
        
        # 저장된 파일 내용 확인
        with open(test_file, 'r') as f:
            data = json.load(f)
            
        # 해상도 정보 확인
        if "resolution" in data:
            res = data["resolution"]
            print(f"해상도 정보: {res['name']} ({res['width']}x{res['height']})")
        else:
            print("해상도 정보가 저장되지 않았습니다!")
            
        # 첫 번째 좌표 확인 (정규화 여부 체크)
        if "left_camera" in data and len(data["left_camera"]) > 0:
            point = data["left_camera"][0]
            if 0 <= point["x"] <= 1 and 0 <= point["y"] <= 1:
                print(f"정규화된 좌표 확인: ({point['x']:.4f}, {point['y']:.4f})")
            else:
                print(f"정규화되지 않은 좌표: ({point['x']}, {point['y']})")
        
        # 저장된 내용 일부 출력
        print("\n저장된 JSON 일부 내용:")
        print(f"resolution: {data.get('resolution')}")
        print(f"첫 번째 좌표: {data.get('left_camera', [])[0] if data.get('left_camera') else 'None'}")
    else:
        print(f"저장 실패: {filepath}")

if __name__ == "__main__":
    main() 