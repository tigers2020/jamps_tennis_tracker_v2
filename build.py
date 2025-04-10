import os
import sys
import shutil
from pathlib import Path

# 현재 디렉토리 출력
print("현재 작업 디렉토리:", os.getcwd())

# 기존 빌드 폴더 정리
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

# 리소스 경로 계산
resources_dir = os.path.join("src", "resources")
images_dir = os.path.join(resources_dir, "images")
icons_dir = os.path.join(images_dir, "icons")
models_dir = os.path.join(resources_dir, "models")
resources_tests_dir = os.path.join(resources_dir, "tests")
resources_tests_images_dir = os.path.join(resources_tests_dir, "images")
tests_dir = os.path.join("tests", "images")

# 파일 존재 여부 확인 및 출력
print("\n포함할 파일/디렉토리 확인:")
print(f"- 이미지 디렉토리: {os.path.exists(images_dir)}")
print(f"- 아이콘 디렉토리: {os.path.exists(icons_dir)}")
print(f"- 모델 디렉토리: {os.path.exists(models_dir)}")
print(f"- 리소스 테스트 이미지: {os.path.exists(resources_tests_dir)}")
print(f"- 테스트 이미지: {os.path.exists(tests_dir)}")

# PyInstaller 명령어 생성
pyinstaller_cmd = [
    "pyinstaller",
    "--clean",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", "TennisBallTracker",
    "--icon", os.path.join(images_dir, "icons", "play.png"),
    
    # 이미지 리소스 추가
    "--add-data", f"{images_dir};src/resources/images",
    "--add-data", f"{icons_dir};src/resources/images/icons",
    
    # 비디오 리소스 추가
    "--add-data", f"{os.path.join(resources_dir, 'videos')};src/resources/videos",
    
    # 기타 리소스 파일 추가
    "--add-data", f"{os.path.join(resources_dir, 'planned_features.json')};src/resources",
    
    # 리소스 테스트 이미지 추가 (calibration에서 사용)
    "--add-data", f"{resources_tests_dir};src/resources/tests",
]

# tests/images 폴더가 있는 경우만 포함
if os.path.exists(tests_dir):
    pyinstaller_cmd.extend(["--add-data", f"{tests_dir};tests/images"])

# models 디렉토리 포함 (큰 파일들은 포함 여부를 선택할 수 있음)
include_models = True
if include_models and os.path.exists(models_dir):
    pyinstaller_cmd.append("--add-data")
    pyinstaller_cmd.append(f"{models_dir};src/resources/models")

# 실행 파일 지정
pyinstaller_cmd.append("run.py")

# 명령어 출력 및 실행
print("\n실행할 명령어:", " ".join(pyinstaller_cmd))
os.system(" ".join(pyinstaller_cmd))

print("\n빌드 완료! dist 폴더에서 TennisBallTracker.exe 파일을 확인하세요.") 