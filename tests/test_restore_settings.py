"""
테스트: 캘리브레이션 파일 설정을 기본값으로 복원
"""

import os
from pathlib import Path
from src.utils.settings_manager import SettingsManager

def main():
    """캘리브레이션 파일 설정을 기본값으로 복원"""
    
    # 기본 경로
    default_dir = os.path.join(Path.home(), ".tennis_tracker", "calibration")
    default_file = os.path.join(default_dir, "court_key_points.json")
    
    print(f"기본 디렉토리: {default_dir}")
    print(f"기본 파일 경로: {default_file}")
    
    # 현재 설정 확인
    settings = SettingsManager.instance()
    current_dir = settings.get("calibration_points_dir", "")
    current_file = settings.get("calibration_points_file", "")
    
    print(f"\n현재 설정된 디렉토리: {current_dir}")
    print(f"현재 설정된 파일: {current_file}")
    
    # 설정 복원
    settings.set("calibration_points_dir", default_dir)
    settings.set("calibration_points_file", default_file)
    success = settings.save_settings()
    
    # 설정 저장 결과 확인
    if success:
        print("\n설정이 복원되었습니다!")
        
        # 복원된 설정 확인
        restored_dir = settings.get("calibration_points_dir", "")
        restored_file = settings.get("calibration_points_file", "")
        print(f"복원된 디렉토리: {restored_dir}")
        print(f"복원된 파일 경로: {restored_file}")
    else:
        print("\n설정 복원 실패!")
    
    print("\n애플리케이션을 다시 실행하여 캘리브레이션 탭에서 좌표를 저장하면")
    print("이제 정규화된 좌표와 해상도 정보가 기본 위치에 저장됩니다.")

if __name__ == "__main__":
    main() 