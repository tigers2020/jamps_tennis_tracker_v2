"""
테스트: 현재 설정 값과 저장된 캘리브레이션 파일을 확인
"""

import os
import json
from src.utils.settings_manager import SettingsManager
from src.models.calibration.point_io import CalibrationPointIO

def main():
    """현재 설정 값과 캘리브레이션 파일 위치 확인"""
    # SettingsManager 초기화
    settings = SettingsManager.instance()
    
    # 캘리브레이션 파일 관련 설정 확인
    print("=== 캘리브레이션 파일 설정 확인 ===")
    calibration_dir = settings.get("calibration_points_dir", "")
    calibration_file = settings.get("calibration_points_file", "")
    
    print(f"캘리브레이션 디렉토리: {calibration_dir}")
    print(f"캘리브레이션 파일: {calibration_file}")
    
    # PointIO를 통해 기본 경로 확인
    point_io = CalibrationPointIO()
    print(f"\nPointIO 기본 디렉토리: {point_io.base_dir}")
    print(f"PointIO 기본 파일: {point_io.default_file}")
    
    # 파일이 존재하는지 확인
    if os.path.exists(calibration_file):
        print(f"\n파일이 존재합니다: {calibration_file}")
        
        # 파일 내용 확인
        try:
            with open(calibration_file, 'r') as f:
                data = json.load(f)
                
            # 해상도 정보 확인
            if "resolution" in data:
                res = data.get("resolution", {})
                print(f"해상도 정보: {res}")
            else:
                print("해상도 정보가 없습니다!")
                
            # 첫 번째 좌표 확인
            if "left_camera" in data and len(data["left_camera"]) > 0:
                point = data["left_camera"][0]
                print(f"첫 번째 좌표: {point}")
                
                # 정규화 여부 확인
                is_normalized = 0 <= point.get("x", 999) <= 1 and 0 <= point.get("y", 999) <= 1
                print(f"정규화된 좌표입니까? {is_normalized}")
            else:
                print("좌표 데이터가 없습니다!")
                
        except Exception as e:
            print(f"파일 읽기 오류: {str(e)}")
    else:
        print(f"\n파일이 존재하지 않습니다: {calibration_file}")
    
    print("\n=== 모든 설정 값 확인 ===")
    for key, value in settings.settings.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 