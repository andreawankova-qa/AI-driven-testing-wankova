"""
Sdílené pomocné funkce pro práci s kurzy a katalogem (Shared Course Actions).
"""

from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage


def open_courses_page(page: Page) -> CoursesPage:
    """Otevře přehled kurzů a ověří přítomnost záhlaví."""
    courses_page = CoursesPage(page)
    courses_page.open()
    expect(courses_page.courses_header).to_be_visible()
    return courses_page
