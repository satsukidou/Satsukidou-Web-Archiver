# -*- coding: utf-8 -*-
"""
汎用のブログ/サイト月次PDFアーカイブスクリプト。

既定値は匿名の例示URLですが、以下の引数で任意のサイトに合わせて使えます。

  python archive_web.py --base-url "https://example.com/blog.html?year={year}&month={month}" \
      --start-year 2021 --end-year 2024 --fiscal-start-month 4 --fiscal-end-month 3

使い方のコツ:
  - ブラウザで月別ページのURLを開き、そのアドレスバーの内容をコピーする
  - 変わる年/月の部分だけを {year} / {month} に置き換える
  - 例: https://example.com/archive?year=2024&month=5
        -> https://example.com/archive?year={year}&month={month}
  - 「サイトのトップページ」ではなく、「月ごとに変わるページURL」を使う

保存先:
  output/monthly/2021-04.pdf ...
  output/yearly/2021-04_2022-03.pdf ...
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlparse, urlunparse

from pypdf import PdfReader, PdfWriter
from playwright.async_api import async_playwright

DEFAULT_BASE_URL = "https://example.com/blog.html?year={year}&month={month}"


def normalize_base_url(base_url: str) -> str:
    """Example URL with a current year/month is converted to the `{year}` / `{month}` template."""
    if "{year}" in base_url or "{month}" in base_url:
        return base_url

    parts = urlparse(base_url)
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    if not query_pairs:
        return base_url

    replaced = []
    changed = False
    for key, value in query_pairs:
        lowered = key.lower()
        if lowered in {"year", "blogyear", "y", "yyyy"} and re.fullmatch(r"\d{4}", value):
            replaced.append((key, "{year}"))
            changed = True
        elif lowered in {"month", "blogmonth", "m"} and re.fullmatch(r"\d{1,2}", value):
            replaced.append((key, "{month}"))
            changed = True
        else:
            replaced.append((key, value))

    if changed:
        encoded_pairs = "&".join(
            f"{quote(key, safe='')}={quote(value, safe='{}')}" for key, value in replaced
        )
        return urlunparse(parts._replace(query=encoded_pairs))

    return base_url


def build_targets(start_year: int, end_year: int, start_month: int = 1, end_month: int = 12):
    if start_year > end_year:
        raise ValueError("start_year must be <= end_year")
    if not 1 <= start_month <= 12 or not 1 <= end_month <= 12:
        raise ValueError("start_month and end_month must be between 1 and 12")
    if start_month > end_month:
        raise ValueError("start_month must be <= end_month")

    targets = []
    for year in range(start_year, end_year + 1):
        for month in range(start_month, end_month + 1):
            targets.append((year, month))
    return targets


def build_archive_targets(start_year: int, end_year: int, fiscal_start_month: int = 1, fiscal_end_month: int = 12):
    """跨年の会計年度や年度を自然に表せるように月を生成する。"""
    if fiscal_start_month == 1 and fiscal_end_month == 12:
        return build_targets(start_year, end_year, 1, 12)

    targets = []
    for year in range(start_year, end_year + 1):
        if year == start_year:
            targets.extend((year, month) for month in range(fiscal_start_month, 13))
        elif year < end_year:
            targets.extend((year, month) for month in range(1, 13))
        else:
            targets.extend((year, month) for month in range(1, fiscal_end_month + 1))
    return targets


def build_yearly_ranges(start_year: int, end_year: int, fiscal_start_month: int = 4, fiscal_end_month: int = 3):
    """年度別のラベルと月リストを生成する。例: 2021-04_2022-03"""
    if start_year >= end_year:
        return []

    ranges = []
    for year in range(start_year, end_year):
        months = [
            (year, month) for month in range(fiscal_start_month, 13)
        ] + [
            (year + 1, month) for month in range(1, fiscal_end_month + 1)
        ]
        label = f"{year}-{fiscal_start_month:02d}_{year + 1}-{fiscal_end_month:02d}"
        ranges.append((label, months))
    return ranges


async def wait_for_images(page):
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


async def save_month(page, year, month, base_url, monthly_dir):
    monthly_dir.mkdir(parents=True, exist_ok=True)
    out = monthly_dir / f"{year}-{month:02d}.pdf"
    if out.exists() and out.stat().st_size > 10000:
        print(f"[skip] {year}-{month:02d} 既存PDFあり")
        return out

    url = base_url.format(year=year, month=month)
    print(f"[open] {year}-{month:02d} {url}")

    await page.goto(url, wait_until="domcontentloaded", timeout=90000)
    await page.emulate_media(media="screen")
    await wait_for_images(page)

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
    print(f"[saved] {out.name}  {out.stat().st_size / 1024 / 1024:.1f} MB")
    return out


def merge_yearly(output_dir: Path, yearly_ranges):
    yearly_dir = output_dir / "yearly"
    yearly_dir.mkdir(parents=True, exist_ok=True)

    for filename, months in yearly_ranges:
        output = yearly_dir / f"{filename}.pdf"
        print(f"[merge] {output.name}")
        writer = PdfWriter()
        missing = []
        for year, month in months:
            src = output_dir / "monthly" / f"{year}-{month:02d}.pdf"
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

        check = PdfReader(str(output))
        print(f"[done] {output.name}  {len(check.pages)} pages  {output.stat().st_size / 1024 / 1024:.1f} MB")


async def main():
    parser = argparse.ArgumentParser(description="Web blog/monthly page archive to PDF.")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BLOG_BASE_URL", DEFAULT_BASE_URL),
        help="URL template with {year} and {month} placeholders, or an example URL such as https://example.com/archive?year=2024&month=5.",
    )
    parser.add_argument("--start-year", type=int, default=2021)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--fiscal-start-month", type=int, default=4)
    parser.add_argument("--fiscal-end-month", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()

    args.base_url = normalize_base_url(args.base_url)

    out_dir = args.output_dir.resolve()
    monthly_dir = out_dir / "monthly"
    yearly_dir = out_dir / "yearly"

    if args.fiscal_start_month <= args.fiscal_end_month:
        targets = build_targets(args.start_year, args.end_year, args.fiscal_start_month, args.fiscal_end_month)
    else:
        targets = build_archive_targets(args.start_year, args.end_year, args.fiscal_start_month, args.fiscal_end_month)

    yearly_ranges = build_yearly_ranges(args.start_year, args.end_year, args.fiscal_start_month, args.fiscal_end_month)

    monthly_dir.mkdir(parents=True, exist_ok=True)
    yearly_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            locale="ja-JP",
        )
        page = await context.new_page()

        for year, month in targets:
            try:
                await save_month(page, year, month, args.base_url, monthly_dir)
            except Exception as e:
                print(f"[ERROR] {year}-{month:02d}: {e}", file=sys.stderr)

        await browser.close()

    merge_yearly(out_dir, yearly_ranges)

    print("\n完了しました。")
    print("年度別PDFは次のフォルダです:")
    print(yearly_dir)


if __name__ == "__main__":
    asyncio.run(main())
