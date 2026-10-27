from playwright.sync_api import Page
from pages.components.navbar import NavbarComponent


class BasePage:
    """Základní třída pro Page Object Model (POM) obsahující společné metody pro práci se stránkou."""

    def __init__(self, page: Page):
        self.page = page
        self.navbar = NavbarComponent(page)

    def navigate_to(self, url: str):
        """Přejde na zadanou URL adresu a počká na ustálení síťového provozu (SPA renderování)."""
        self.page.goto(url, wait_until="networkidle")

    def get_title(self) -> str:
        """Vrátí titulek aktuální stránky."""
        return self.page.title()

    def get_current_url(self) -> str:
        """Vrátí aktuální URL adresu."""
        return self.page.url
