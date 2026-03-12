@echo off
REM NVDA Coach - Build Script
REM Packages the add-on as an .nvda-addon file (which is just a zip archive).
REM Run this from the nvdaCoach directory.

set ADDON_NAME=nvdaCoach
set VERSION=1.0.0

echo Building %ADDON_NAME% version %VERSION%...

REM Remove any old build.
if exist "%ADDON_NAME%-%VERSION%.nvda-addon" del "%ADDON_NAME%-%VERSION%.nvda-addon"

REM Create the zip archive. Requires 7-Zip or PowerShell.
REM Using PowerShell (available on Windows 10+):
powershell -Command "Compress-Archive -Path 'manifest.ini','globalPlugins','doc' -DestinationPath '%ADDON_NAME%-%VERSION%.zip' -Force"
ren "%ADDON_NAME%-%VERSION%.zip" "%ADDON_NAME%-%VERSION%.nvda-addon"

echo.
echo Build complete: %ADDON_NAME%-%VERSION%.nvda-addon
echo You can install this file by opening it with NVDA.
pause
