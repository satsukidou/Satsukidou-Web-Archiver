import unittest

from archive_web import DEFAULT_BASE_URL, build_targets, build_yearly_ranges, normalize_base_url


class ArchiveWebTests(unittest.TestCase):
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

    def test_default_base_url_is_anonymous_example_template(self):
        self.assertIn("example.com", DEFAULT_BASE_URL)
        self.assertNotIn("isikawa", DEFAULT_BASE_URL.lower())
        self.assertNotIn("magokoro", DEFAULT_BASE_URL.lower())

    def test_normalize_base_url_accepts_example_urls_without_manual_template_replacement(self):
        self.assertEqual(
            normalize_base_url("https://example.com/archive?year=2024&month=5"),
            "https://example.com/archive?year={year}&month={month}",
        )
        self.assertEqual(
            normalize_base_url("https://example.com/viewer/blog.html?blogYear=2024&blogMonth=5"),
            "https://example.com/viewer/blog.html?blogYear={year}&blogMonth={month}",
        )


if __name__ == "__main__":
    unittest.main()
