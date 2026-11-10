"""Ukázkový soubor se záměrnými chybami pro otestování skillu qa-auditor."""
import time
import pytest
from playwright.sync_api import Page


def test_user_login_with_intentional_bugs(page: Page):
    """Tento test schválně porušuje pravidla projektu AGENTS.md pro otestování QA auditora."""
    # CHYBA 1: Chybí povinné markery (@pytest.mark.auth a @pytest.mark.smoke / regression)
    # CHYBA 2: Chybí kanonické ID v docstringu (např. TC-01-AUTH) a AAA struktura

    # CHYBA 3: Hardcoded URL bez použití konfigurace nebo Page Objectu
    page.goto("https://testovani.kitner.cz/login")

    # CHYBA 4: Zakázané statické čekání time.sleep()
    time.sleep(2)

    # CHYBA 5: Přímé křehké CSS selektory v testu namísto Page Objectu
    page.locator("#username-input").fill("student@kitner.cz")
    page.locator(".password-field").fill("TajneHeslo123")
    page.locator("button.btn-primary").click()

    # CHYBA 6: Zakázaný nativní Python assert na UI prvek namísto Playwright expect()
    assert page.get_by_test_id("user_profile_badge").is_visible()
