"""
테스트: 원래 기본 위치의 캘리브레이션 파일 확인
"""

import os
import json
from pathlib import Path

def main():
    """기본 위치의 캘리브레이션 파일 확인"""
    
    # 기본 경로
    default_path = os.path.join(
        Path.home(), 
        ".tennis_tracker", 
        "calibration",
        "court_key_points.json"
    )
    
    print(f"원래 기본 경로: {default_path}")
    
    # 파일이 존재하는지 확인
    if os.path.exists(default_path):
        print(f"파일이 존재합니다!")
        
        # 파일 내용 확인
        try:
            with open(default_path, 'r') as f:
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
                
                if not is_normalized:
                    print("이 파일은 정규화되지 않은 좌표를 사용하는 이전 버전 파일입니다.")
                    
                    # 해당 파일 이름 변경 (백업)
                    backup_path = default_path + ".backup"
                    try:
                        os.rename(default_path, backup_path)
                        print(f"기존 파일을 {backup_path}로 백업했습니다.")
                    except Exception as e:
                        print(f"파일 백업 실패: {str(e)}")
            else:
                print("좌표 데이터가 없습니다!")
                
        except Exception as e:
            print(f"파일 읽기 오류: {str(e)}")
    else:
        print(f"파일이 존재하지 않습니다!")

if __name__ == "__main__":
    main() 