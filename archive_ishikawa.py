# -*- coding: utf-8 -*-
"""
水戸市立石川小学校 公式ブログ 保存用PDF作成スクリプト
対象: 2021年4月〜2024年3月
出力:
  monthly/2021-04.pdf ... monthly/2024-03.pdf
  yearly/令和3年度_2021-04_2022-03.pdf
  yearly/令和4年度_2022-04_2023-03.pdf
  yearly/令和5年度_2023-04_2024-03.pdf

特徴:
- 元ページをブラウザで実際に表示してPDF化するので、掲載画像を含めて保存
- 途中で止まっても、既存の月別PDFは自動でスキップ
- 年度別に12か月分を結合
"""

from pathlib import Path
import asyncio
import sys
from pypdf import PdfReader, PdfWriter
from playwright.async_api import async_playwright

BASE_URL = "https://www.magokoro.ed.jp/isikawa-e/viewer/blog.html?blogYear={year}&blogMonth={month}"

OUT = Path(__file__).resolve().parent / "output"
MONTHLY = OUT / "monthly"
YEARLY = OUT / "yearly"

TARGETS = []
for year in range(2021, 2025):
    for month in range(1, 13):
        if year == 2021 and month < 4:
            continue
        if year == 2024 and month > 3:
            continue
        TARGETS.append((year, month))

FISCAL_YEARS = [
    ("令和3年度_2021-04_2022-03.pdf",
     [(2021, m) for m in range(4, 13)] + [(2022, m) for m in range(1, 4)]),
    ("令和4年度_2022-04_2023-03.pdf",
     [(2022, m) for m in range(4, 13)] + [(2023, m) for m in range(1, 4)]),
    ("令和5年度_2023-04_2024-03.pdf",
     [(2023, m) for m in range(4, 13)] + [(2024, m) for m in range(1, 4)]),
]

async def wait_for_images(page):
    # 画像の読み込み完了をできるだけ待つ
    try:
        await page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass

    try:
        await page.evaluate("""
        async () => {
          const imgs = Array.from(document.images);
          await Promise.all(imgs.map(img => {
            if (img.complete) return Promise.resolve();
            return new Promise(resolve => {
              img.addEventListener('load', resolve, {once:true});
              img.addEventListener('error', resolve, {once:true});
            });
          }));
        }
        """)
    except Exception:
        pass

    # 遅延読み込み対策でページを一度最後までスクロール
    try:
        await page.evaluate("""
        async () => {
          const step = Math.max(600, window.innerHeight);
          for (let y = 0; y < document.body.scrollHeight; y += step) {
            window.scrollTo(0, y);
            await new Promise(r => setTimeout(r, 120));
          }
          window.scrollTo(0, 0);
        }
        """)
        await page.wait_for_timeout(1500)
    except Exception:
        pass

async def save_month(page, year, month):
    MONTHLY.mkdir(parents=True, exist_ok=True)
    out = MONTHLY / f"{year}-{month:02d}.pdf"
    if out.exists() and out.stat().st_size > 10000:
        print(f"[skip] {year}-{month:02d} 既存PDFあり")
        return out

    url = BASE_URL.format(year=year, month=month)
    print(f"[open] {year}-{month:02d} {url}")

    await page.goto(url, wait_until="domcontentloaded", timeout=90000)
    await page.emulate_media(media="screen")
    await wait_for_images(page)

    # ページ内リンク先は触らず、表示中の月ページ全体を保存
    await page.pdf(
        path=str(out),
        format="A4",
        print_background=True,
        display_header_footer=False,
        margin={
            "top": "8mm",
            "right": "8mm",
            "bottom": "8mm",
            "left": "8mm",
        },
        prefer_css_page_size=True,
    )
    print(f"[saved] {out.name}  {out.stat().st_size/1024/1024:.1f} MB")
    return out

def merge_yearly():
    YEARLY.mkdir(parents=True, exist_ok=True)
    for filename, months in FISCAL_YEARS:
        output = YEARLY / filename
        print(f"[merge] {filename}")
        writer = PdfWriter()
        missing = []
        for year, month in months:
            src = MONTHLY / f"{year}-{month:02d}.pdf"
            if not src.exists():
                missing.append(src.name)
                continue
            reader = PdfReader(str(src))
            for page in reader.pages:
                writer.add_page(page)

        if missing:
            print("  !! 未作成の月があります:", ", ".join(missing))
            continue

        with output.open("wb") as f:
            writer.write(f)

        # 読み直して壊れていないか最低限確認
        check = PdfReader(str(output))
        print(f"[done] {output.name}  {len(check.pages)} pages  {output.stat().st_size/1024/1024:.1f} MB")

async def main():
    MONTHLY.mkdir(parents=True, exist_ok=True)
    YEARLY.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            locale="ja-JP",
        )
        page = await context.new_page()

        for year, month in TARGETS:
            try:
                await save_month(page, year, month)
            except Exception as e:
                print(f"[ERROR] {year}-{month:02d}: {e}", file=sys.stderr)

        await browser.close()

    merge_yearly()

    print("\n完了しました。")
    print("年度別PDFは次のフォルダです:")
    print(YEARLY)

if __name__ == "__main__":
    asyncio.run(main())
