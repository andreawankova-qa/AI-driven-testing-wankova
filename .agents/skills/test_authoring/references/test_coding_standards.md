# 💻 Standardy implementace automatizovaných testů (Coding Standards)

Tento dokument shrnuje závazná pravidla pro psaní zdrojového kódu testů v Pytest + Playwright pro portál `testovani.kitner.cz` v souladu s [AGENTS.md](../../../AGENTS.md).

---

## 🏆 7 pilířů implementace testu

### 1. Struktura AAA (Arrange, Act, Assert)
Každý testovací kód je rozdělen do tří jasných a okomentovaných bloků:
* **Arrange (Příprava):** Inicializace Page Objectů, příprava dynamických testovacích dat a navigace na výchozí stránku.
* **Act (Akce):** Vyvolání uživatelských akcí prostřednictvím metod Page Objectů (vyplnění formuláře, kliknutí, odeslání).
* **Assert (Ověření):** Validace stavu systému pomocí web-first asercí Playwrightu (`expect`).

```python
    @pytest.mark.smoke
    def test_tc48_auth_user_registration(self, page: Page):
        """TC-48-AUTH: Úspěšná registrace nového uživatele."""
        # 1. ARRANGE
        reg_page = RegistrationPage(page)
        user = generate_unique_user()
        reg_page.open()

        # 2. ACT
        reg_page.register(
            name=user["name"],
            email=user["email"],
            password=user["password"],
            password_confirmation=user["password"]
        )

        # 3. ASSERT
        expect(page).to_have_url(CoursesPage.URL)
        expect(reg_page.navbar.logout_button).to_be_visible()
```

---

### 2. POM-First pravidlo a Shared Helpers (Zákaz přímých lokátorů a boilerplate)
* **Pravidlo pro lokátory:** Test nesmí obsahovat žádné přímé selektory (`page.locator(...)`, `page.get_by_test_id(...)`).
* **Řešení pro Page Objects:** Pokud nový scénář vyžaduje nový prvek nebo stránku, **nejprve** se vytvoří nebo rozšíří příslušný Page Object v `pages/`:
  1. Dědí z `pages/base_page.py`.
  2. Všechny lokátory využívají výhradně `self.page.get_by_test_id("...")`.
  3. **Page Object nesmí obsahovat aserce (`expect` ani `assert`).** Vrací pouze lokátory nebo provádí akce.
* **Řešení pro vícekrokové toky (`helpers/`):** Pokud sekvence $\ge 2$ kroků slouží jako příprava stavu pro jiný test (např. přihlášení uživatele nebo registrace a navigace), zapouzdří se do sdílené funkce v `helpers/` (např. `login_user(page, ...)`), aby se neopakoval boilerplate kód v testech.

---

### 3. Názvosloví a kanonické docstringy
* **Název metody:** `test_tc{cislo}_{modul}_{popis_snake_case}`
  * Příklad: `def test_tc06_auth_login_with_valid_credentials(self, page: Page):`
* **Docstring:** První řádek **musí** obsahovat kanonické ID a český název testu:
  * Příklad: `"""TC-06-AUTH: Ověření úspěšného přihlášení uživatele."""`

---

### 4. Povinné Pytest markery (2 úrovně)
Každý testovací soubor/třída a metoda musí mít definované 2 typy markerů:
1. **Doménový marker (na úrovni třídy):**
   * `@pytest.mark.auth`
   * `@pytest.mark.courses`
   * `@pytest.mark.enrollment`
   * `@pytest.mark.lecturer`
   * `@pytest.mark.navigation`
   * `@pytest.mark.profile`
   * `@pytest.mark.security`
2. **Marker závažnosti (na úrovni metody):**
   * `@pytest.mark.smoke` – pro P1 (Happy Path, kritické toky).
   * `@pytest.mark.regression` – pro P2 a P3 (negativní, validační, hraniční toky).

---

### 5. Zásada DRY a parametrizace (`@pytest.mark.parametrize`)
Pro testování více variant téhož vstupu (např. chybové stavy, neplatné formáty e-mailu/telefonu) vždy použijte parametrizaci s parametrem `ids=` pro přehledný report namísto kopírování testů:

```python
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "email, expected_error",
        [
            ("neplatny_email", "The email must be a valid email address."),
            ("", "The email field is required."),
        ],
        ids=["invalid-format", "empty-email"]
    )
    def test_tc04_auth_email_validation(self, page: Page, email: str, expected_error: str):
        """TC-04-AUTH: Validace chybových stavů e-mailu."""
        # 1. ARRANGE
        login_page = LoginPage(page)
        login_page.open()

        # 2. ACT
        login_page.fill_email(email)
        login_page.click_login()

        # 3. ASSERT
        expect(login_page.email_error).to_have_text(expected_error)
```

---

### 6. Idempotence a dynamická testovací data
* Nikdy nepoužívejte statické hodnoty pro vytváření nových entit (e-mail, IČO).
* Používejte generátor dat `utils.data_generator`:
  * `generate_unique_user()` – unikátní jméno a e-mail s časovým razítkem.
  * `generate_valid_ico()` – 8místné IČO s platným kontrolním součtem modulo 11.
  * `generate_invalid_ico()` – IČO s neplatným součtem.

---

### 7. Web-First Assertions Playwrightu
* **POVOLENO:** `expect(locator).to_be_visible()`, `expect(page).to_have_url(...)`, `expect(input).to_have_value(...)`.
* **ZAKÁZÁNO:**
  * ❌ `time.sleep()` – nahraďte automatickým čekáním Playwrightu (`expect(...).to_be_visible()`).
  * ❌ `assert locator.is_visible()` – nativní Python assert nemá auto-wait a vede k flakiness.
  * ❌ Testování absence prvku bezprostředně po akci bez ustálení stavu.
