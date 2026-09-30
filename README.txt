Web Blog PDF Archive
====================

目的
----
ブログや月次公開ページを、実際にブラウザで表示した状態からPDFとして保存します。
デフォルト設定は 2021年4月〜2024年3月 の範囲ですが、
`--base-url` や年数設定を変えることで別サイトにも使えます。

Windowsでの使い方
-----------------
1. ZIPを展開します。
2. 「run_windows.bat」をダブルクリックします。
3. 初回のみ Playwright / Chromium の準備が入ります。
4. 月別ページを順番に保存し、必要なら年度別に結合します。
5. 完了すると output/yearly が自動で開きます。

大事な点
--------
- 元ページをブラウザで表示して保存するので、画像付きのページもそのままPDF化します。
- 途中で止まっても、完成済みの月別PDFは次回スキップします。
- 月別PDFは output/monthly に残ります。
- サイト側のURL構成が変わった場合は、`--base-url` を変更して再実行できます。
- 作業中はPCをスリープさせない方が安全です。

必要なもの
----------
- Windows 11
- Python 3
- インターネット接続

Macでの使い方
-------------
1. ZIPを展開します。
2. Python 3をインストールします: https://www.python.org/downloads/macos/
3. 「run_mac.command」をダブルクリックします。
4. 初回のみ仮想環境、必要なPythonライブラリ、Playwright用Chromiumを自動で準備します。
5. 完了すると output/yearly がFinderで開きます。

macOSの「開発元を確認できない」警告が表示された場合は、ファイルをControlキーを押しながらクリックして「開く」を選択してください。

必要なもの (Mac)
----------------
- macOS
- Python 3
- インターネット接続

保存元を変えるとき
------------------
`archive_web.py` を次のように実行してください。

python archive_web.py --base-url "https://example.com/viewer/blog.html?year={year}&month={month}"

※公開ページの保存を目的とした個人用アーカイブです。
