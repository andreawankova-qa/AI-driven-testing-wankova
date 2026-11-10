---
name: test_overview
description: >-
  Aktivuj tento skill VŽDY, když uživatel požaduje technický přehled kroků a kontrol v automatizovaných
  testech (např. 'jaké kroky testy provádí', 'přehled kroků a kontrol', 'co přesně testy ověřují').
  Vytvoří nebo aktualizuje Markdown dokument docs/TEST_STEPS_OVERVIEW.md s detailním rozpadem akcí a asercí.
---

# 📋 Test Overview (Přehled testů)

Tento skill slouží k vytvoření Markdown souboru s přehledem všech automatizovaných testů (AT).

### 🎯 Kroky, které musí agent udělat pro vytvoření souboru:

- **1. Projít testovací soubory:**
  - Prohledej složku `tests/` a projdi všechny testovací soubory (`test_*.py`).

- **2. Z každého testu extrahovat:**
  - **Název a ID testu:** Označení testu (např. `TC-xx-MODUL`), název testovací funkce a stručný cíl z docstringu.
  - **Kroky testu:** Všechny prováděné akce (otevření stránky, kliknutí na prvky, vyplnění formulářů, volání helperů).
  - **Kontroly:** Všechna ověření a aserce (co test kontroluje – např. `expect(...).to_be_visible()`, `to_have_url()`, ověření textů a chybových stavů).

- **3. Sestavit Markdown dokument:**
  - Vytvoř strukturu obsahující:
    - Souhrnnou tabulku všech testů.
    - Detailní rozpad jednotlivých testů s očíslovanými kroky a kontrolami.

- **4. Uložit výsledek do MD souboru:**
  - Ulož vytvořený přehled do `docs/TEST_STEPS_OVERVIEW.md` (nebo do souboru určeného uživatelem).
  *(Tip: Kroky 1 až 4 lze provést i automatizovaně skriptem `python3 .agents/skills/test_overview/scripts/generate_test_overview.py`)*

- **5. Rozhodnout, zda je hotovo:**
  - Spusť validační skript pro ověření výsledku:
    ```bash
    python3 .agents/skills/test_overview/scripts/verify_done.py
    ```
  - Skript ověří 100% přítomnost všech testů, kroků i kontrol a vrátí jasný verdikt:
    - **`HOTOVO`** (návratový kód `0`) -> úkol je úspěšně dokončen.
    - **`NENÍ HOTOVO`** (návratový kód `1`) -> vypíše co chybí k nápravě.
