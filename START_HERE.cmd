@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo Ishikawa Elementary School Blog PDF Archive
echo 2021-04 to 2024-03
echo ==================================================
echo.
echo This window will stay open so errors can be checked.
echo.
pause

set "PYEXE="
where py >nul 2>nul
if not errorlevel 1 set "PYEXE=py -3"

if not defined PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYEXE=python"
)

if not defined PYEXE (
  echo.
  echo [ERROR] Python was not found.
  echo Install Python 3 from:
  echo https://www.python.org/downloads/windows/
  echo.
  echo IMPORTANT: Check "Add python.exe to PATH" during installation.
  echo.
  echo A log file was created: archive_log.txt
  echo Python was not found. > archive_log.txt
  pause
  exit /b 1
)

echo Python command: %PYEXE%
echo Python command: %PYEXE% > archive_log.txt
%PYEXE% --version >> archive_log.txt 2>&1

echo.
echo Step 1/3: Installing required Python packages...
%PYEXE% -m pip install --upgrade playwright pypdf >> archive_log.txt 2>&1
if errorlevel 1 goto :FAIL

echo.
echo Step 2/3: Installing Chromium for Playwright...
%PYEXE% -m playwright install chromium >> archive_log.txt 2>&1
if errorlevel 1 goto :FAIL

echo.
echo Step 3/3: Creating monthly PDFs and 3 yearly PDFs...
echo This can take a while. Please keep this window open.
echo.
%PYEXE% archive_ishikawa.py 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath archive_run.txt"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" goto :FAILRUN

echo.
echo ==================================================
echo COMPLETED
echo ==================================================
echo.
echo Opening output\yearly ...
if exist "%~dp0output\yearly" explorer "%~dp0output\yearly"
echo.
echo Logs:
echo   archive_log.txt
echo   archive_run.txt
echo.
pause
exit /b 0

:FAIL
echo.
echo ==================================================
echo SETUP FAILED
echo ==================================================
echo Open archive_log.txt and send its contents to ChatGPT.
echo.
type archive_log.txt
echo.
pause
exit /b 1

:FAILRUN
echo.
echo ==================================================
echo ARCHIVE RUN FAILED
echo ==================================================
echo Open archive_run.txt and send its contents to ChatGPT.
echo.
pause
exit /b %RC%
