@echo off
echo Tennis Ball Tracker 패키징 도구
echo ------------------------------
echo 참고: PyInstaller 설치가 필요합니다. (pip install pyinstaller)
echo.

set APP_NAME=TennisBallTracker
set MAIN_SCRIPT=run.py
set ICON_PATH=src\resources\images\icons\play.png

echo 1. 기존 빌드 폴더 정리 중...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo 2. PyInstaller로 단일 exe 파일 생성 중...
pyinstaller --clean ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name %APP_NAME% ^
  --icon=%ICON_PATH% ^
  --add-data "src\resources\images;src\resources\images" ^
  --add-data "src\resources\videos;src\resources\videos" ^
  --add-data "src\resources\models;src\resources\models" ^
  --add-data "src\resources\tests;src\resources\tests" ^
  --add-data "src\resources\planned_features.json;src\resources" ^
  --add-data "tests\images;tests\images" ^
  %MAIN_SCRIPT%

echo.
if %ERRORLEVEL% EQU 0 (
  echo 패키징 성공! 생성된 실행 파일: dist\%APP_NAME%.exe
) else (
  echo 패키징 실패. 오류 코드: %ERRORLEVEL%
)

echo.
pause 