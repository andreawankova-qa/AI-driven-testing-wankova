# 🎯 Doporučené vzory lokátorů (Locator Patterns) – Playwright & POM

Tento dokument slouží jako referenční katalog osvědčených návrhových vzorů pro tvorbu lokátorů v Page Objects podle architektonických standardů projektu.

---

## 1. Základní prvky s `get_by_test_id`

Pro jednoznačné formulářové prvky, nadpisy a tlačítka používejte nativní metodu `page.get_by_test_id("...")`:

```python
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Nativní Playwright lokátory
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.login_button: Locator = page.get_by_test_id("login_button")
        self.heading: Locator = page.get_by_test_id("login_text")
        self.email_error: Locator = page.get_by_test_id("email_input_errors")
```

---

## 2. Řetězení kontejnerů (Locator Chaining)

Pokud se prvek se stejným `data-testid` vyskytuje na stránce vícekrát (např. odkaz na login v horní navigaci vs. v patičce vs. pod registračním formulářem), **nikdy nepoužívejte indexy (`.first`, `.last`)**. Místo toho zúžete vyhledávání zřetězením s rodičovským kontejnerem:

```python
# Odkaz na přihlášení v horní liště navigace
self.nav_login_link: Locator = page.get_by_test_id("navigation").get_by_test_id("login_link")

# Odkaz na přihlášení v sekci pod registračním formulářem
self.register_login_link: Locator = page.get_by_test_id("register_section").get_by_test_id("login_link")

# Tlačítko registrace / přidání v hlavičce kurzů
self.add_course_button: Locator = page.get_by_test_id("courses_header").get_by_test_id("registration_link")
```

---

## 3. Dynamické seznamy a regulární výrazy

Pro seznam dynamických položek (např. karty kurzů generované v cyklu) využijte možnost předat regulární výraz do `get_by_test_id`:

```python
import re
from playwright.sync_api import Page, Locator

class CoursesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Všechny karty začínající na 'course_' (např. course_1, course_2, ...)
        self.course_cards: Locator = page.get_by_test_id(re.compile(r"^course_"))
        
        # Obecné lokátory pro vnitřek libovolné karty
        self.course_names: Locator = page.get_by_test_id("course_name")
        self.course_prices: Locator = page.get_by_test_id("course_price")

    def get_card_name(self, card: Locator) -> Locator:
        """Scoped lokátor uvnitř konkrétní karty."""
        return card.get_by_test_id("course_name")

    def get_card_price(self, card: Locator) -> Locator:
        """Scoped lokátor uvnitř konkrétní karty."""
        return card.get_by_test_id("course_price")
```

---

## 4. Filtrování položek podle textu v kontejneru (`.filter(has_text=...)`)

Pokud mají prvky v rámci jednoho kontejneru identický `data-testid` (např. navigační odkazy v menu), upřesněte vyhledání pomocí `.filter(has_text="...")`:

```python
class NavbarComponent:
    def __init__(self, page: Page):
        self.container: Locator = page.get_by_test_id("navigation")
        
        # Odlíšení odkazů se stejným data-testid="courses_link"
        self.courses_link: Locator = self.container.get_by_test_id("courses_link").filter(has_text="Přehled kurzů")
        self.my_courses_link: Locator = self.container.get_by_test_id("courses_link").filter(has_text="Moje kurzy")
```

---

## 5. Komponentový přístup a delegace

Opakující se prvky (hlavička, menu, dialogy) definujte jako samostatné komponenty v `pages/components/` a vkládejte do Page Objects (Single Source of Truth dle principu DRY):

```python
from pages.components.navbar import NavbarComponent

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.navbar = NavbarComponent(page)
```

Testy ani odvozené Page Objects tak nedefinují navigaci znovu, ale využívají sdílenou instanci.
