from playwright.sync_api import Page


class BasePage:
    """Základní třída pro Page Object Model (POM) obsahující společné metody pro práci se stránkou."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        """Přejde na zadanou URL adresu."""
        self.page.goto(url, wait_until="domcontentloaded")

    def get_title(self) -> str:
        """Vrátí titulek aktuální stránky."""
        return self.page.title()

    def get_current_url(self) -> str:
        """Vrátí aktuální URL adresu."""
        return self.page.url
