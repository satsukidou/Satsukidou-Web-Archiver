import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pypdf import PdfWriter

from archive_web import build_targets, build_yearly_ranges, is_cached_pdf, write_pdf_source


class ArchiveWebTests(unittest.TestCase):
    def test_cached_pdf_is_reused_only_for_the_same_source_url(self):
        with TemporaryDirectory() as temp_dir:
            pdf = Path(temp_dir) / "2021-04.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            writer.add_metadata({"/Title": "test" * 3000})
            with pdf.open("wb") as stream:
                writer.write(stream)
            url = "https://example.com/umegaoka/2021/4"
            write_pdf_source(pdf, url)

            self.assertTrue(is_cached_pdf(pdf, url))
            self.assertFalse(is_cached_pdf(pdf, "https://example.com/ishikawa/2021/4"))
            self.assertFalse(pdf.with_suffix(".url").exists())

    def test_build_targets_uses_custom_year_and_month_window(self):
        self.assertEqual(
            build_targets(2022, 2023, start_month=5, end_month=6),
            [(2022, 5), (2022, 6), (2023, 5), (2023, 6)],
        )

    def test_build_yearly_ranges_supports_fiscal_cycles(self):
        self.assertEqual(
            build_yearly_ranges(2021, 2024, fiscal_start_month=4, fiscal_end_month=3),
            [
                ("2021-04_2022-03", [(2021, 4), (2021, 5), (2021, 6), (2021, 7), (2021, 8), (2021, 9), (2021, 10), (2021, 11), (2021, 12), (2022, 1), (2022, 2), (2022, 3)]),
                ("2022-04_2023-03", [(2022, 4), (2022, 5), (2022, 6), (2022, 7), (2022, 8), (2022, 9), (2022, 10), (2022, 11), (2022, 12), (2023, 1), (2023, 2), (2023, 3)]),
                ("2023-04_2024-03", [(2023, 4), (2023, 5), (2023, 6), (2023, 7), (2023, 8), (2023, 9), (2023, 10), (2023, 11), (2023, 12), (2024, 1), (2024, 2), (2024, 3)]),
            ],
        )


if __name__ == "__main__":
    unittest.main()
