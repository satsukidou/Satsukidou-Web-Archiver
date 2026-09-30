# Satsukidou-Web-Archiver
Web記事やブログの月次ページをPDFとしてまとめて保存する汎用アーカイバーです。

## 使い方

- 既定の設定では 2021-04 〜 2024-03 の月次ページを順番に保存します。
- URL は `--base-url` で変更できます。
- 例: `python archive_web.py --base-url "https://example.com/blog.html?year={year}&month={month}"`

## 出力先

- `output/monthly/` に月別PDF
- `output/yearly/` に年度別結合PDF

## 既定の基本構成

- `archive_web.py` が本体
- `archive_ishikawa.py` は後方互換用のラッパー
- `run_windows.bat` / `START_HERE.cmd` はWindows向けの起動スクリプト
