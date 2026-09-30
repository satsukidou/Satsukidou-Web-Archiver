#!/bin/bash

cd "$(dirname "$0")"
set -o pipefail

pause_on_exit() {
    printf "\nEnterキーを押すと閉じます..."
    read -r
}

printf "============================================\n"
printf "Web Blog PDF Archive (macOS)\n"
printf "保存するURLと期間を設定できます。空欄は [] 内の既定値を使います。\n"
printf "============================================\n\n"

read -r -p "URLテンプレート [https://www.magokoro.ed.jp/isikawa-e/viewer/blog.html?blogYear={year}&blogMonth={month}]: " BASE_URL
BASE_URL=${BASE_URL:-"https://www.magokoro.ed.jp/isikawa-e/viewer/blog.html?blogYear={year}&blogMonth={month}"}
read -r -p "開始年 [2021]: " START_YEAR
START_YEAR=${START_YEAR:-2021}
read -r -p "終了年 [2024]: " END_YEAR
END_YEAR=${END_YEAR:-2024}
read -r -p "開始月 [4]: " START_MONTH
START_MONTH=${START_MONTH:-4}
read -r -p "終了月 [3]: " END_MONTH
END_MONTH=${END_MONTH:-3}

if [[ ! "$START_YEAR" =~ ^[0-9]{4}$ || ! "$END_YEAR" =~ ^[0-9]{4}$ ]] || (( START_YEAR > END_YEAR )); then
    printf "開始年と終了年は4桁の西暦で入力し、開始年を終了年以前にしてください。\n"
    pause_on_exit
    exit 1
fi

case "$START_MONTH" in 1|2|3|4|5|6|7|8|9|10|11|12) ;; *) printf "開始月は1〜12で入力してください。\n"; pause_on_exit; exit 1 ;; esac
case "$END_MONTH" in 1|2|3|4|5|6|7|8|9|10|11|12) ;; *) printf "終了月は1〜12で入力してください。\n"; pause_on_exit; exit 1 ;; esac

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
if ! "$PYTHON" archive_web.py \
    --base-url "$BASE_URL" \
    --start-year "$START_YEAR" \
    --end-year "$END_YEAR" \
    --fiscal-start-month "$START_MONTH" \
    --fiscal-end-month "$END_MONTH" 2>&1 | tee archive_run.txt; then
    printf "\n処理中にエラーが発生しました。archive_run.txt を確認してください。\n"
    pause_on_exit
    exit 1
fi

printf "\n完了しました。年度別PDFフォルダを開きます。\n"
open output/yearly
pause_on_exit