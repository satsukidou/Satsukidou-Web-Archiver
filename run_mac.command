#!/bin/bash

cd "$(dirname "$0")"
set -o pipefail

pause_on_exit() {
    printf "\nEnterキーを押すと閉じます..."
    read -r
}

printf "============================================\n"
printf "Web Blog PDF Archive (macOS)\n"
printf "2021年4月 - 2024年3月 (デフォルト設定)\n"
printf "============================================\n\n"

if ! command -v python3 >/dev/null 2>&1; then
    printf "Python 3 が見つかりません。https://www.python.org/downloads/macos/ からインストールしてください。\n"
    pause_on_exit
    exit 1
fi

if [ ! -x .venv/bin/python ]; then
    printf "Pythonの仮想環境を作成しています...\n"
    if ! python3 -m venv .venv; then
        printf "仮想環境を作成できませんでした。Python 3のインストールを確認してください。\n"
        pause_on_exit
        exit 1
    fi
fi

PYTHON=".venv/bin/python"

printf "必要なPythonライブラリを準備しています...\n"
if ! "$PYTHON" -m pip install --upgrade playwright pypdf 2>&1 | tee -a archive_log.txt; then
    printf "ライブラリの準備に失敗しました。archive_log.txt を確認してください。\n"
    pause_on_exit
    exit 1
fi

printf "Playwright用Chromiumを準備しています...\n"
if ! "$PYTHON" -m playwright install chromium 2>&1 | tee -a archive_log.txt; then
    printf "Chromiumの準備に失敗しました。archive_log.txt を確認してください。\n"
    pause_on_exit
    exit 1
fi

printf "\n月別ページを順番にPDF化します。完了までこのウィンドウを開いたままにしてください。\n\n"
if ! "$PYTHON" archive_web.py 2>&1 | tee archive_run.txt; then
    printf "\n処理中にエラーが発生しました。archive_run.txt を確認してください。\n"
    pause_on_exit
    exit 1
fi

printf "\n完了しました。年度別PDFフォルダを開きます。\n"
open output/yearly
pause_on_exit