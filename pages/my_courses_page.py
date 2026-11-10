import re
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class MyCoursesPage(BasePage):
    """Page Object reprezentující sekci Moje kurzy pro přihlášeného studenta."""

    URL = f"{settings.BASE_URL}/my-courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.header: Locator = page.get_by_test_id("courses_header")
        self.title: Locator = page.get_by_test_id("courses_title")
        self.section: Locator = page.get_by_test_id("courses_section")

        # Karta zapsaného kurzu a její atributy
        self.course_cards: Locator = page.get_by_test_id(re.compile(r"^course_\d+$"))
        self.primary_course_card: Locator = page.get_by_test_id("course_1")
        self.course_info: Locator = page.get_by_test_id("course_info")
        self.course_name: Locator = page.get_by_test_id("course_name")
        self.course_description: Locator = page.get_by_test_id("course_description")
        self.course_price: Locator = page.get_by_test_id("course_price")
        self.course_image: Locator = page.get_by_test_id("course_image")

        # Organizační údaje lekcí běhu kurzu
        self.date_time_div: Locator = page.get_by_test_id("date_time_div")
        self.date_time_from: Locator = page.get_by_test_id("date_time_from")
        self.date_time_to: Locator = page.get_by_test_id("date_time_to")
        self.day_information: Locator = page.get_by_test_id("day_information")
        self.place_information: Locator = page.get_by_test_id("place_information")

        # Tlačítko pro přechod na detail kurzu
        self.course_buttons: Locator = page.get_by_test_id("course_buttons")
        self.detail_button: Locator = self.course_buttons.get_by_test_id("registration_link")

    def open(self):
        """Otevře sekci Moje kurzy přímo."""
        self.navigate_to(self.URL)
        return self

    def click_course_detail(self, card: Locator = None):
        """Rozklikne detail zapsaného kurzu kliknutím na tlačítko 'Chci vidět více'."""
        target_card = card or self.primary_course_card
        target_card.get_by_test_id("registration_link").click()
        return self
