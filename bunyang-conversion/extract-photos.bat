@echo off
chcp 65001 >nul
title 휴아림 제안서 사진 꺼내기
echo.
echo ============================================
echo   파주 휴아림 제안서 - 사진 꺼내기
echo ============================================
echo.
echo 원본 PPT 파일을 찾고 있습니다. 잠시만 기다려 주십시오.
echo.

set "SRC="
for %%D in ("D:\DDownloads" "%USERPROFILE%\Downloads" "%USERPROFILE%\Desktop" "%USERPROFILE%\Documents" "%USERPROFILE%" "D:\") do (
  if not defined SRC if exist %%D (
    for /f "delims=" %%F in ('dir /b /s "%%~D\*휴아림*.pptx" 2^>nul') do (
      if not defined SRC set "SRC=%%F"
    )
  )
)

if not defined SRC (
  echo   [실패] PPT 파일을 찾지 못했습니다.
  echo.
  echo   이 프로그램을 PPT 파일과 같은 폴더에 두고 다시 실행해 주십시오.
  echo.
  pause
  exit /b
)

echo   찾았습니다.
echo   %SRC%
echo.
echo 사진을 꺼내는 중입니다...

set "WORK=%TEMP%\hua_extract"
if exist "%WORK%" rd /s /q "%WORK%" 2>nul
mkdir "%WORK%" 2>nul
copy /y "%SRC%" "%WORK%\hua.zip" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "try{ Expand-Archive -LiteralPath '%WORK%\hua.zip' -DestinationPath '%WORK%\out' -Force; exit 0 }catch{ exit 1 }"
if errorlevel 1 (
  echo   [실패] 압축을 푸는 데 문제가 생겼습니다.
  echo.
  pause
  exit /b
)

set "DEST=%USERPROFILE%\Desktop\휴아림_사진"
if exist "%DEST%" rd /s /q "%DEST%" 2>nul
mkdir "%DEST%" 2>nul

if not exist "%WORK%\out\ppt\media" (
  echo   [실패] 이미지 폴더를 찾지 못했습니다.
  echo.
  pause
  exit /b
)

copy /y "%WORK%\out\ppt\media\*.*" "%DEST%\" >nul 2>nul

set /a CNT=0
for %%F in ("%DEST%\*.*") do set /a CNT+=1

echo.
echo ============================================
echo   완료되었습니다.  사진 %CNT% 개
echo ============================================
echo.
echo   바탕화면에 [휴아림_사진] 폴더를 열어 드렸습니다.
echo.
echo   그 안의 파일을 전부 선택하고 (Ctrl+A)
echo   깃허브 업로드 창으로 끌어다 놓으신 뒤
echo   초록색 Commit changes 를 누르시면 끝입니다.
echo.
start "" "%DEST%"
pause
