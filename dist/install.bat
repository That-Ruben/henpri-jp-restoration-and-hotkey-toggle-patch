@echo off
setlocal
rem HENPRI Japanese language mod installer
rem Detects the Translation Improvement Patch (HENPRI.pfs.069) and installs
rem the matching build of the mod. Run this from inside the game folder,
rem or place the mod folder next to it and drag the game folder onto this
rem file.

set "GAMEDIR=%~1"
if "%GAMEDIR%"=="" set "GAMEDIR=%CD%"

if not exist "%GAMEDIR%\HENPRI.exe" (
    echo [!] HENPRI.exe not found in: %GAMEDIR%
    echo     Run this from the game folder, or drag the game folder onto
    echo     install.bat.
    pause
    exit /b 1
)

if exist "%GAMEDIR%\HENPRI.pfs.069" (
    echo Detected: Translation Improvement Patch ^(HENPRI.pfs.069^)
    echo Installing the compatible build ^(keeps the improved English^).
    echo NOTE: if you remove the Improvement Patch later, re-run this
    echo       installer so the mod switches back to official English.
    copy /Y "%~dp0hip\HENPRI.pfs.080" "%GAMEDIR%\HENPRI.pfs.080" >nul
) else (
    echo No Improvement Patch detected - installing the official-English
    echo build.
    copy /Y "%~dp0official\HENPRI.pfs.080" "%GAMEDIR%\HENPRI.pfs.080" >nul
)

if exist "%GAMEDIR%\HENPRI.pfs.080" (
    echo.
    echo Installed HENPRI.pfs.080 successfully.
    echo   - Japanese option: Config ^> Window ^> LANGUAGE
    echo   - Quick toggle in-game: press L
    echo   - Uninstall: delete HENPRI.pfs.080 from the game folder
) else (
    echo [!] Install failed - could not copy the patch file.
)
pause
