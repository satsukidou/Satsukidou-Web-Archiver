@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo Web Blog PDF Archive
echo 2021年4月 - 2024年3月 (デフォルト設定)
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo Python が見つかりません。
  echo https://www.python.org/ から Python 3 をインストールしてください。
  echo インストール時に "Add Python to PATH" にチェックを入れてください。
  pause
  exit /b 1
)

echo 必要なライブラリを確認・インストールします...
py -m pip install --upgrade playwright pypdf
if errorlevel 1 goto :err

echo Chromium を準備します...
py -m playwright install chromium
if errorlevel 1 goto :err

echo.
echo 保存対象のページを順番に開いてPDF化します。
echo 途中で止めても、次回は完成済みの月をスキップします。
echo.
py archive_web.py

echo.
echo 完了しました。
echo output\yearly フォルダを開きます。
explorer "%~dp0output\yearly"
pause
exit /b 0

:err
echo.
echo セットアップ中にエラーが発生しました。
pause
exit /b 1
