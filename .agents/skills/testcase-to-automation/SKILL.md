---
name: testcase-to-automation
description: >-
  POVINNĚ aktivuj tento skill VŽDY, když uživatel požaduje automatizaci schválených testovacích případů
  (Test Cases) z docs/TEST_CASES.md do Playwright + Pytest kódu v tests/, a to i v případě, že název skillu
  výslovně nezmíní (např. při zadání 'zautomatizuj TC-xx', 'napiš automat pro tento scénář', 'převeď TC na kód',
  'tc-to-at', 'udělej z test casu automat', či při implementaci testů podle katalogu). Skill je určen
  výhradně pro implementaci existujících schválených scénářů (nemění zadání v TEST_CASES.md). Vynucuje 5krokový
  postup: 1. Příprava vstupů (TC, konvence, POM, data), 2. Generování testů agentem, 3. Review lokátorů a assertů
  (vazba na existující skilly locators a assertions), 4. Skript hotovo verify_at.py (3x stabilní běh bez pádu,
  žádná pevná čekání sleep/wait_for_timeout, pre-flight lint; striktní zákaz ohlásit hotovo před exit code 0)
  a 5. Lidské schválení a Merge.
---

# 🚀 Pracovní postup: Test Case ➔ Automatizovaný test (testcase-to-automation)

Tento skill slouží k bezpečnému a standardizovanému převodu schválených manuálních testovacích případů (**Test Cases**) z centrálního katalogu `docs/TEST_CASES.md` na robustní automatizované testy (**Playwright + Pytest**) v `tests/`.

---

## 🧭 Tabulka pracovního postupu

| Krok | Název kroku | Kdo ho dělá | Vstup | Výstup | Závazná pravidla kroku |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.** | **Příprava vstupů** | **Agent** (analýza)<br>+ **Vy** (potvrzení) | Schválený test case z `docs/TEST_CASES.md` | Připravené vstupy (konvence, POM, testovací data) | **Read-Only:** Test casy v dokumentaci se nemění.<br>Agent ověří konvence projektu ([AGENTS.md](../../../AGENTS.md)), identifikuje potřebné Page Objects v `pages/`, toky v `helpers/` a dynamická data z `utils.data_generator`. |
| **2.** | **Generování testů agentem** | **Agent** | Chybějící prvky v `pages/` + specifikace TC | Kód testu v `tests/<modul>/test_<oblast>.py` + aktualizované Page Objects | **POM-First & Ochrana kódu:**<br>• Nejprve doplnit prvky a akce do `pages/` (v POM nesmí být aserce!).<br>• Test umístit do doménové složky dle modulu v ID (např. `tests/auth/` pro `TC-xx-AUTH`).<br>• **Existující kód se nemaže:** Nový test se doplní k existujícím; pokud již test existuje, pouze se cíleně aktualizuje.<br>• Test psát v AAA struktuře s dynamickými daty. Povinné kanonické ID (`TC-xx-MODUL`) v docstringu a v názvu metody. |
| **3.** | **Review lokátorů a assertů** | **Agent** | Kód v `pages/` a `tests/` | Kód bez anti-patternů | **Použití existujících skillů:**<br>• **Lokátory:** Striktně dle skillu [locators](../locators/SKILL.md) (priorita #1 `get_by_test_id`, zákaz přímých selektorů v testech).<br>• **Aserce:** Striktně dle skillu [assertions](../assertions/SKILL.md) (web-first `expect()`, zákaz Python `assert` na UI). |
| **4.** | **Skript hotovo** | **Agent** (spustí)<br>+ **Skript** (vyhodnotí) | Kód testu v `tests/` | Exit code 0 (PASS) nebo výpis chyb (FAIL) | Povinně spusť `verify_at.py`. Skript ověří mapování TC, zákaz pevných čekání, pre-flight lint a 3x stabilní běh.<br>**Zákaz ohlásit hotovo před dosažením exit code 0.** |
| **5.** | **Lidské schválení a Merge** | **Vy (Tester)** | Zelený výstup skriptu (PASS) + diff kódu | Schválený a začleněný test v sadě | Agent předloží testerovi report a kód ke kontrole. Po schválení je kód začleněn (merge) do testovací sady. |

---

## 🔒 Práva na zápis

* ✏️ **Agent MŮŽE měnit:**
  - `tests/` (vytváření a úprava testů),
  - `pages/` (doplňování nových lokátorů a metod do Page Objects),
  - `helpers/` (znovupoužitelné pomocné toky).
* 🛑 **Read-Only pro agenta (ZÁKAZ editace):**
  - Schválené test casy v `docs/TEST_CASES.md` a specifikace požadavků v `docs/požadavky_ust_podle_src.md`,
  - Validační skript Definice hotovo `scripts/verify_at.py`.

---

## 🛠️ Příkaz pro spuštění skriptu hotovo (DoD)

V Kroku 4 agent povinně spustí validaci pro právě automatizovaný test case:

```bash
python3 .agents/skills/testcase-to-automation/scripts/verify_at.py --tc <ID_TEST_CASU>
```

*(Příklad: `python3 .agents/skills/testcase-to-automation/scripts/verify_at.py --tc TC-01-AUTH`)*

Alternativně pro konkrétní soubor testu:

```bash
python3 .agents/skills/testcase-to-automation/scripts/verify_at.py --file tests/auth/test_login.py
```

---

## ⚠️ Závazné pravidlo Definice hotovo (DoD)

> **Agent nesmí prohlásit úkol za hotový ani jej předat ke schválení v Kroku 5, dokud skript `scripts/verify_at.py` neskončí s exit code `0`.**
