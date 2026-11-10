---
name: story-to-testcases
description: >-
  POVINNĚ aktivuj tento skill VŽDY, když uživatel zadá User Story, byznysové požadavky,
  akceptační kritéria (AK/AC) nebo požádá o návrh testovacích případů a scénářů
  (např. 'navrhni testy pro US-xx', 'připrav test casy', 'jak otestovat tuto story',
  'vytvoř manuální testy ze zadání'), a to i když název skillu výslovně nezmíní.
  Vynucuje 4krokový postup: 1. Analýza požadavků a otázky na nejasnosti, 2. Návrh test
  casů dle šablony (Happy Path, negativní toky, hraniční hodnoty BVA/EP), 3. Strojové ověření
  Definice hotovo (DoD) skriptem verify_tc.py (zákaz ohlásit hotovo před exit code 0)
  a 4. Předání testerovi ke schválení.
---

# 📋 Pracovní postup: User Story ➔ Manuální Test Casy

Tento skill slouží k bezpečnému převodu byznysových požadavků (**User Story**) na detailní **manuální testovací případy (Test Cases)** a jejich zaevidování do centrálního katalogu `docs/TEST_CASES.md`.

---

## 🧭 Tabulka pracovního postupu

| Krok | Název kroku | Kdo ho dělá | Vstup | Výstup | Závazná pravidla kroku |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.** | **Review User Story** | **Agent** (analýza)<br>+ **Vy** (rozhodnutí) | Text User Story a Akceptační kritéria (AK / AC) | Seznam doplňujících otázek (nebo potvrzení bezvadnosti) | **Pravidlo IF/ELSE:**<br>• *Pokud v zadání cokoliv chybí* (limity, formáty, chování chyb): **zastav se a polož konkrétní otázky**. Bez odpovědí nepokračuj.<br>• *Pokud je zadání prokazatelně úplné a bez mezer*: výslovně to potvrď a pokračuj ke Kroku 2. |
| **2.** | **Návrh test casů** | **Agent** | Vyjasněná User Story + šablona `tc_template.md` | Zápis test casů do `docs/TEST_CASES.md` | Doplň testy do centrálního katalogu `docs/TEST_CASES.md`. Každé AK musí mít alespoň 1 test case. Povinně navrhni Happy Path, negativní testy i hraniční hodnoty (BVA/EP). Každý test musí mít vazbu na AK. |
| **3.** | **Skript hotovo (DoD)** | **Agent** (spustí)<br>+ **Skript** (vyhodnotí) | `docs/TEST_CASES.md` (+ specifikace story) | Exit code 0 (PASS) nebo výpis chyb (FAIL) | Povinně spusť `verify_tc.py`. Pokud skript nahlásí chyby, oprav test casy a spusť znovu. **Zákaz ohlásit hotovo před dosažením exit code 0.** |
| **4.** | **Lidské schválení** | **Vy (Tester)** | Zelený výstup skriptu + zapsané test casy | Schválená sada test casů (nebo připomínky k úpravě) | Předlož výsledek testerovi a vyčkej na schválení či připomínky. |

---

## 🔒 Práva na zápis

* ✏️ **Agent MŮŽE měnit:** Centrální katalog testů `docs/TEST_CASES.md` (přidává nové scénáře).
* 🛑 **Read-Only pro agenta (ZÁKAZ editace):** Specifikace User Story (`docs/požadavky_ust_podle_src.md`), validační skript `scripts/verify_tc.py` a šablona `templates/tc_template.md`.

---

## 🛠️ Příkaz pro spuštění skriptu hotovo (DoD)

V Kroku 3 agent povinně spustí validaci pro právě zpracovávanou User Story:

```bash
python3 .agents/skills/story-to-testcases/scripts/verify_tc.py \
  --tc docs/TEST_CASES.md \
  --story docs/požadavky_ust_podle_src.md \
  --story-id <ID_STORY>
```

*(Poznámka: Hodnotu `<ID_STORY>` nahraďte ID konkrétní řešené story, např. `--story-id US-08`)*

---

## ⚠️ Závazné pravidlo Definice hotovo (DoD)

> **Agent nesmí prohlásit úkol za hotový ani jej předat ke schválení v Kroku 4, dokud skript `scripts/verify_tc.py` neskončí s exit code `0`.**
