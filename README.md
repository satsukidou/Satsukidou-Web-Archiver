# Satsukidou-Web-Archiver
Web記事やブログの月次ページをPDFとしてまとめて保存する汎用アーカイバーです。

このツールは、サイト上で「月ごとにURLが変わるページ」を自動で開いて、各月のページをPDFとして保存し、さらに年度単位でまとめて結合します。

---

## 1. 何をするツールか

このツールは次のようなサイト向けです。

- ブログや学校の更新ページが月別になっている
- 例: 2024年5月のページが `...?year=2024&month=5` で、2024年6月が `...?year=2024&month=6`
- そのURLを順番に開いてPDFに保存したい

このスクリプトの役割は、月ごとのURLを自動で生成して開くことです。

---

## 2. 事前準備

Python と Playwright が使える環境が必要です。

1. このフォルダを開く
2. ターミナルを起動する
3. 必要なら依存関係を入れる
4. 実行コマンドを使う

例:

```bash
python archive_web.py --base-url "https://example.com/blog.html?year={year}&month={month}" \
  --start-year 2021 --end-year 2024 --fiscal-start-month 4 --fiscal-end-month 3
```

---

## 3. どのURLを使うべきか

ここが一番大事です。ホームページのURLではなく、月次ページのURLを使います。

### 3-1. 対象サイトを開く

ブラウザで、月別のページを1か月分だけ開いてください。

たとえば次のようなページがあるとします。

- `https://example.com/archive?year=2024&month=5`
- `https://example.com/archive?year=2024&month=6`
- `https://example.com/archive?year=2024&month=7`

このように、URLの中に年と月が入っているページが対象です。

### 3-2. アドレスバーのURLを確認する

1. ブラウザのアドレスバーを見ます
2. URLをコピーします
3. 変わる部分を探します

変わる部分は、通常次のどちらかです。

- `year` / `month`
- `blogYear` / `blogMonth`

### 3-3. URLをテンプレートに変換する

変わる部分を `{year}` と `{month}` に置き換えます。

#### 例1: 変数名が year / month の場合

元URL:

```text
https://example.com/archive?year=2024&month=5
```

テンプレート:

```text
https://example.com/archive?year={year}&month={month}
```

#### 例2: 変数名が blogYear / blogMonth の場合

元URL:

```text
https://example.com/viewer/blog.html?blogYear=2024&blogMonth=5
```

テンプレート:

```text
https://example.com/viewer/blog.html?blogYear={year}&blogMonth={month}
```

#### 例3: URLの見た目が少し違ってもOK

次のような形でも大丈夫です。

```text
https://example.com/blog.html?year=2024&month=5
https://example.com/blog.html?year=2024&m=5
https://example.com/blog.html?blogYear=2024&blogMonth=5
```

重要なのは、「月と年がURLの中で変わる場所」を見つけて、そこだけ `{year}` と `{month}` に置き換えることです。

---

## 4. `--base-url` の渡し方

対象サイトのテンプレートを用意したら、次のように実行します。

```bash
python archive_web.py --base-url "https://example.com/archive?year={year}&month={month}"
```

年の範囲を指定したい場合は次のようにします。

```bash
python archive_web.py \
  --base-url "https://example.com/archive?year={year}&month={month}" \
  --start-year 2021 \
  --end-year 2024
```

年度を跨ぐ形式でまとめたい場合:

```bash
python archive_web.py \
  --base-url "https://example.com/archive?year={year}&month={month}" \
  --start-year 2021 \
  --end-year 2024 \
  --fiscal-start-month 4 \
  --fiscal-end-month 3
```

---

## 5. 実行後の出力

PDFは次のフォルダに保存されます。

- `output/monthly/` : 月別PDF
- `output/yearly/` : 年度別結合PDF

例:

```text
output/monthly/2024-05.pdf
output/yearly/2023-04_2024-03.pdf
```

---

## 6. よくある間違い

### 間違い1: ホームページURLを使う

```text
https://example.com/
```

これは月ごとのページではないので、正しく動きません。

### 間違い2: 年月をテンプレートに変えない

```text
https://example.com/archive?year=2024&month=5
```

これは 2024年5月しか拾えません。

正しくは:

```text
https://example.com/archive?year={year}&month={month}
```

### 間違い3: 変数名を誤る

```text
https://example.com/archive?year={year}&month={month}
```

といったテンプレートをそのまま書けばOKです。サイト側の変数名が `blogYear` / `blogMonth` の場合は、それに合わせて書いてください。

---

## 7. 最短の手順

1. 月別ページをブラウザで開く
2. URLをコピーする
3. 年と月が入っている部分を `{year}` と `{month}` に置き換える
4. `--base-url` にそのテンプレートを設定する
5. スクリプトを実行する
6. `output/` フォルダを確認する

---

## 8. 既定の基本構成

- `archive_web.py` が本体
- `archive_ishikawa.py` は後方互換用のラッパー
- `run_windows.bat` / `START_HERE.cmd` はWindows向けの起動スクリプト
- `run_mac.command` はMac向けの起動スクリプト

## Macでの使い方

1. ZIPを展開します。
2. Python 3をインストールします: https://www.python.org/downloads/macos/
3. `run_mac.command` をダブルクリックし、ブログURL・開始年・終了年・開始月・終了月を入力します。各項目を空欄にすると、表示された既定値を使います。

初回起動時にプロジェクト内の `.venv` に必要なPythonライブラリとPlaywright用Chromiumを準備します。macOSの「開発元を確認できない」警告が表示された場合は、ファイルをControlキーを押しながらクリックして「開く」を選択してください。完了すると `output/yearly/` がFinderで開きます。

年月が指定されたブログURLをそのまま貼り付けられます。`blogYear` / `blogMonth`（または `year` / `month`）の値は実行時に各対象月へ置き換えます。開始月が終了月より大きい場合は、年度をまたぐ期間として扱います（例: 4月〜翌年3月）。

月別PDFは取得元URLが前回と同じ場合だけ再利用します。以前に別の学校から保存したPDFや、取得元記録のないPDFは再取得して置き換えます。

ターミナルから起動する場合は、プロジェクトフォルダで `chmod +x run_mac.command` を一度実行し、続けて `./run_mac.command` を実行してください。

必要なら、次の段階として「このサイトに合わせた `--base-url` を実際に作る例」を、1サイトごとのケースで追加できます。
