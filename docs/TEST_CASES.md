# Testovací případy (Test Cases) – Demo-login

Tento dokument obsahuje ucelenou sadu testovacích případů navrženou na základě specifikace požadavků v [`docs/požadavky_ust_podle_src.md`](požadavky_ust_podle_src.md).  
Testovací případy používají průběžné číslování ve formátu **`TC-01-MODUL`** až **`TC-48-MODUL`** a pokrývají 100 % všech 19 User Stories (US-01 až US-19) včetně pozitivních, negativních, validačních i bezpečnostních scénářů.

> [!NOTE]
> **Stav testovací sady po auditu a sjednocení (1. 11. 2026):**
> * **Celkový počet testovacích případů v katalogu:** **48** (`TC-01` až `TC-48`)
> * **Pokrytí automatizovanými testy v kódu:** **47/48 (97.9 %)**
> * **Pokrytí požadavků:** 19/19 User Stories (100 %)
> * **Rozpad testů podle modulů:**
>   * Modul 1 (AUTH): 21 testů (`TC-01` až `TC-21`) – 100 % pokryto (2 evidované defekty xfail)
>   * Modul 2 (CRS): 5 testů (`TC-22` až `TC-26`) – 100 % pokryto
>   * Modul 3 (ENR): 6 testů (`TC-27` až `TC-31`, `TC-48`)
>   * Modul 4 (LEC): 7 testů (`TC-32` až `TC-38`) – 100 % pokryto (4 evidované defekty xfail)
>   * Modul 5 (PRF): 4 testy (`TC-39` až `TC-42`) – 100 % pokryto
>   * Modul 6 (SEC): 5 testů (`TC-43` až `TC-47`) – 100 % pokryto (1 evidovaný defekt xfail)

---

## 📋 Přehledová matice pokrytí (Traceability Matrix)

| Modul | User Story | Kód testovacího případu | Pokrytá AK | Název Test Casu | Typ / Priorita |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Autentizace (AUTH)** | **US-01** (Registrace) | `TC-01-AUTH` | AK-1, AK-7, AK-8 | Úspěšná registrace zákaznického účtu | Smoke / P1 |
| | | `TC-02-AUTH` | AK-3, AK-6 | Registrace s již existujícím e-mailem | Negativní / P2 |
| | | `TC-03-AUTH` | AK-5, AK-6 | Registrace s neshodujícími se hesly | Validační / P2 |
| | | `TC-04-AUTH` | AK-2, AK-3, AK-5, AK-6 | Validace povinných polí a neplatného e-mailu | Validační / P2 |
| | | `TC-05-AUTH` | AK-4 | Normalizace e-mailu (ořezání mezer, case-insensitive) | Hraniční / P3 |
| | **US-02** (Přihlášení) | `TC-06-AUTH` | AK-1, AK-5, AK-6 | Úspěšné přihlášení uživatele s platnými údaji | Smoke / P1 |
| | | `TC-07-AUTH` | AK-4 | Přihlášení s neplatným heslem / neexistujícím e-mailem | Negativní / P1 |
| | | `TC-08-AUTH` | AK-2 | Odeslání prázdného přihlašovacího formuláře | Validační / P2 |
| | | `TC-09-AUTH` | AK-3 | Přihlášení s velkými písmeny a mezerami v e-mailu | Hraniční / P2 |
| | | `TC-10-AUTH` | AK-7 | Navigace klávesnicí (Tab + Enter) ve formuláři | Přístupnost / P3 |
| | **US-03** (Odhlášení) | `TC-11-AUTH` | AK-1, AK-2, AK-3, AK-4 | Bezpečné odhlášení z horní navigace | Smoke / P1 |
| | **US-04** (Žádost o reset) | `TC-12-AUTH` | AK-1, AK-4 | Odeslání platné žádosti o reset hesla | Funkční / P2 |
| | | `TC-13-AUTH` | AK-2, AK-3 | Žádost o reset s neplatným / prázdným e-mailem | Validační / P3 |
| | **US-05** (Změna hesla) | `TC-14-AUTH` | AK-2, AK-4 | Úspěšná změna hesla pomocí platného tokenu | Funkční / P2 |
| | | `TC-15-AUTH` | AK-1, AK-5 | Pokus o změnu hesla s neplatným nebo expirovaným tokenem | Bezpečnostní / P2 |
| | | `TC-16-AUTH` | AK-3 | Změna hesla s neshodným potvrzením | Validační / P3 |
| | **US-06** (Ověření e-mailu) | `TC-17-AUTH` | AK-1, AK-2 | Úspěšné ověření e-mailu přes platný odkaz | Funkční / P2 |
| | | `TC-18-AUTH` | AK-3 | Pokus o ověření e-mailu s neplatným odkazem | Negativní / P2 |
| | | `TC-19-AUTH` | AK-4, AK-5 | Znovuzaslání ověřovacího e-mailu a časový limit | Funkční / P3 |
| | **US-07** (Rate Limiting) | `TC-20-AUTH` | AK-1, AK-2, AK-3 | Dočasná blokace po 5 neúspěšných pokusech o přihlášení | Bezpečnostní / P1 |
| | | `TC-21-AUTH` | AK-4 | Vynulování počítadla neúspěchů po úspěšném přihlášení | Funkční / P2 |
| **2. Katalog kurzů (CRS)**| **US-08** (Katalog) | `TC-22-CRS` | AK-1, AK-5 | Zobrazení katalogu kurzů pro nepřihlášeného návštěvníka | Smoke / P1 |
| | | `TC-23-CRS` | AK-2, AK-3, AK-4 | Ověření zobrazení atributů kurzu (cena, kapacita, náhled) | Funkční / P2 |
| | **US-09** (Detail kurzu) | `TC-24-CRS` | AK-1, AK-2, AK-3, AK-4 | Zobrazení detailu kurzu a seznamu vypsaných termínů | Funkční / P1 |
| | **US-10** (Kapacita) | `TC-25-CRS` | AK-1, AK-2 | Zobrazení tlačítka zápisu u termínu s volnou kapacitou | Funkční / P1 |
| | | `TC-26-CRS` | AK-3 | Zamezení registrace a indikace plně obsazeného běhu | Hraniční / P2 |
| **3. Zápis na kurz (ENR)**| **US-11** (Zápis s IČO/tel) | `TC-27-ENR` | AK-1, AK-5, AK-6, AK-7 | Úspěšný zápis na kurz s platným telefonem a platným IČO | Smoke / P1 |
| | | `TC-28-ENR` | AK-1, AK-3 | Úspěšný zápis na kurz bez vyplněného IČO | Funkční / P2 |
| | | `TC-29-ENR` | AK-3, AK-4 | Zápis s neplatným IČO (chyba kontrolního součtu modulo 11) | Validační / P2 |
| | | `TC-30-ENR` | AK-2, AK-4 | Zápis s neplatným telefonem (méně než 9 číslic) | Validační / P2 |
| | **US-12** (Moje kurzy) | `TC-31-ENR` | AK-1 až AK-8 | Zobrazení přehledu mých zapsaných kurzů a detailu lekcí | Funkční / P1 |
| | | `TC-48-ENR` | AK-1, AK-2 | Zobrazení sekce Moje kurzy bez aktivních zápisů (Empty State) | Negativní / P2 |
| **4. Správa lektorem (LEC)**| **US-13** (Tvorba kurzu) | `TC-32-LEC` | AK-1, AK-2, AK-4, AK-6 | Vytvoření nového kurzu s náhledem s poměrem stran 16:9 | Funkční / P2 |
| | | `TC-33-LEC` | AK-5 | Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran | Validační / P2 |
| | | `TC-34-LEC` | AK-2, AK-3 | Validace povinných polí a číselné kapacity/ceny kurzu | Validační / P2 |
| | **US-14** (Vypsání běhu) | `TC-35-LEC` | AK-1, AK-2, AK-4, AK-5 | Úspěšné vypsání nového termínu kurzu lektorem | Funkční / P2 |
| | | `TC-36-LEC` | AK-3 | Validace povinných polí při vypsání termínu | Validační / P3 |
| | **US-15** (Účastníci) | `TC-37-LEC` | AK-1, AK-2, AK-3 | Zobrazení tabulky přihlášených účastníků pro lektora | Funkční / P2 |
| | | `TC-38-LEC` | AK-4 | Zamezení přístupu k účastníkům pro zákazníka | Bezpečnostní / P1 |
| **5. Profil a nástěnka (PRF)**| **US-16** (Nástěnka) | `TC-39-PRF` | AK-1, AK-2 | Zobrazení personalizovaného uvítání na domovské nástěnce | Smoke / P2 |
| | **US-17** (Úprava profilu) | `TC-40-PRF` | AK-1, AK-3, AK-6 | Úspěšná aktualizace údajů profilu (jméno, IČO, telefon) | Funkční / P2 |
| | | `TC-41-PRF` | AK-4, AK-5 | Validace formátu IČO a telefonu v profilu | Validační / P2 |
| | | `TC-42-PRF` | AK-2 | Pokus o změnu e-mailu na již obsazenou adresu | Negativní / P2 |
| **6. Bezpečnost (SEC)** | **US-18** (RBAC) | `TC-43-SEC` | AK-1, AK-2, AK-6, AK-7 | Přesměrování nepřihlášeného z privátních stránek na katalog | Bezpečnostní / P1 |
| | | `TC-44-SEC` | AK-3, AK-4 | Zákaz lektorských operací pro uživatele v roli zákazníka | Bezpečnostní / P1 |
| | | `TC-45-SEC` | AK-5 | Zákaz zápisu na kurz pro uživatele v roli lektora | Bezpečnostní / P2 |
| | **US-19** (CSRF/Sezení) | `TC-46-SEC` | AK-1, AK-2 | Ochrana formulářů CSRF tokenem a odmítnutí neplatného požadavku | Bezpečnostní / P1 |
| | | `TC-47-SEC` | AK-3 | Regenerace session ID při přihlášení a odhlášení | Bezpečnostní / P2 |
---

## 🔍 Detailní specifikace Test Cases

---

### Modul 1: Autentizace a správa uživatelského sezení (AUTH)

#### `TC-01-AUTH`: Úspěšná registrace zákaznického účtu
* **Pokrytí:** US-01, AK-1, AK-7, AK-8
* **Předpoklady:** Uživatel je nepřihlášen a nachází se na registrační stránce `/registrace`.
* **Testovací data:** Jméno: `Jan Novák`, E-mail: `jan.novak.test@example.com` (unikátní), Heslo: `BezpecneHeslo123`, Potvrzení hesla: `BezpecneHeslo123`.
* **Kroky:**
  1. Do pole „Jméno“ zadejte `Jan Novák`.
  2. Do pole „E-mail“ zadejte unikátní e-mail.
  3. Do pole „Heslo“ zadejte `BezpecneHeslo123`.
  4. Do pole „Potvrzení hesla“ zadejte `BezpecneHeslo123`.
  5. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Účet je úspěšně vytvořen s rolí Zákazník.
  - Uživatel je automaticky přihlášen.
  - Uživatel je přesměrován na domovskou stránku.
  - V horní navigaci se zobrazí jméno uživatele a tlačítko „Odhlásit se“.

#### `TC-02-AUTH`: Registrace s již existujícím e-mailem
* **Pokrytí:** US-01, AK-3, AK-6
* **Předpoklady:** V systému již existuje registrovaný uživatel s e-mailem `existujici@example.com`.
* **Testovací data:** E-mail: `existujici@example.com`.
* **Kroky:**
  1. Vyplňte registrační formulář s e-mailem `existujici@example.com`.
  2. Vyplňte platné jméno a shodná hesla.
  3. Klikněte na „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Registrace se neprovede.
  - Uživatel zůstává na stránce registrace.
  - U pole e-mailu se zobrazí chybová hláška informující, že zadaný e-mail je již registrován.

#### `TC-03-AUTH`: Registrace s neshodujícími se hesly
* **Pokrytí:** US-01, AK-5, AK-6
* **Předpoklady:** Uživatel je na registrační stránce.
* **Testovací data:** Heslo: `Heslo123`, Potvrzení hesla: `JineHeslo456`.
* **Kroky:**
  1. Vyplňte jméno a platný unikátní e-mail.
  2. Do pole „Heslo“ zadejte `Heslo123`.
  3. Do pole „Potvrzení hesla“ zadejte `JineHeslo456`.
  4. Klikněte na „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Zobrazí se validační chybová zpráva o neshodě hesel.

#### `TC-04-AUTH`: Validace povinných polí a neplatného e-mailu
* **Pokrytí:** US-01, AK-2, AK-3, AK-5, AK-6
* **Předpoklady:** Uživatel je na registrační stránce.
* **Testovací data:** E-mail: `neplatny-email-bez-zavinace`.
* **Kroky:**
  1. Ponechte pole prázdná a klikněte na „Zaregistrovat se“.
  2. Zkontrolujte indikaci povinných polí.
  3. Vyplňte jméno a hesla, ale do e-mailu zadejte `neplatny-email-bez-zavinace`.
  4. Klikněte na „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Při prázdných polích systém zobrazí hlášení o povinnosti vyplnit všechna pole.
  - Při neplatném formátu e-mailu systém zobrazí chybu formátu e-mailové adresy.

#### `TC-05-AUTH`: Normalizace e-mailu při registraci
* **Pokrytí:** US-01, AK-4
* **Předpoklady:** V systému neexistuje e-mail `petr@example.com`.
* **Testovací data:** E-mail se znaky a mezerami: `  PETR@EXAMPLE.COM  `.
* **Kroky:**
  1. Zaregistrujte účet s e-mailem `  PETR@EXAMPLE.COM  `.
  2. Odhlaste se.
  3. Zkuste se přihlásit s malými písmeny `petr@example.com`.
* **Očekávaný výsledek:**
  - Účet je registrován s oříznutými mezerami a normalizovaným e-mailem.
  - Přihlášení s `petr@example.com` proběhne úspěšně.

#### `TC-06-AUTH`: Úspěšné přihlášení uživatele s platnými údaji
* **Pokrytí:** US-02, AK-1, AK-5, AK-6
* **Předpoklady:** V systému existuje aktivní uživatel (např. `student@kitner.cz` / `heslo123`).
* **Kroky:**
  1. Přejděte na přihlašovací stránku `/prihlaseni`.
  2. Zadejte e-mail `student@kitner.cz`.
  3. Zadejte heslo `heslo123`.
  4. Klikněte na tlačítko „Přihlásit se“.
* **Očekávaný výsledek:**
  - Uživatel je úspěšně autentizován.
  - Uživatel je přesměrován na domovskou stránku.
  - V navigaci zmizí odkaz na „Přihlásit se“ a zobrazí se „Můj profil“, „Moje kurzy“ a „Odhlásit se“.

#### `TC-07-AUTH`: Přihlášení s neplatným heslem / neexistujícím e-mailem
* **Pokrytí:** US-02, AK-4
* **Předpoklady:** Uživatel je na `/prihlaseni`.
* **Testovací data:** 
  - Scénář A: Neexistující e-mail `neexistuje@example.com`, heslo `cokoliv`.
  - Scénář B: Existující e-mail, ale špatné heslo `spatneheslo`.
* **Kroky:**
  1. Na stránce `/prihlaseni` zadejte testovací data (neexistující e-mail nebo chybné heslo).
  2. Klikněte na tlačítko „Přihlásit se“.
* **Očekávaný výsledek:**
  - V obou scénářích systém odmítne přihlášení a zobrazí jednotnou zprávu o neplatných přihlašovacích údajích (z důvodu bezpečnosti nerozlišuje, zda neexistuje e-mail nebo je špatné heslo).

#### `TC-08-AUTH`: Odeslání prázdného přihlašovacího formuláře
* **Pokrytí:** US-02, AK-2
* **Předpoklady:** Uživatel je na `/prihlaseni`.
* **Kroky:**
  1. Ponechte pole e-mail i heslo prázdná.
  2. Klikněte na tlačítko „Přihlásit se“.
* **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Zobrazí se validační upozornění vyžadující vyplnění obou polí.

#### `TC-09-AUTH`: Přihlášení s tolerancí mezer a velikosti písmen
* **Pokrytí:** US-02, AK-3
* **Předpoklady:** Existuje účet `student@kitner.cz`.
* **Kroky:**
  1. Do pole e-mail zadejte `  STUDENT@KITNER.CZ  `.
  2. Zadejte platné heslo a odešlete formulář.
* **Očekávaný výsledek:**
  - Přihlášení proběhne úspěšně (mezery jsou oříznuty, velikost písmen ignorována).

#### `TC-10-AUTH`: Ovládání přihlašovacího formuláře klávesnicí
* **Pokrytí:** US-02, AK-7
* **Předpoklady:** Uživatel otevře přihlašovací stránku.
* **Kroky:**
  1. Umístěte kurzor do pole E-mail a zadejte e-mail.
  2. Stiskněte klávesu `Tab`.
  3. Zadejte heslo do nově zafokusovaného pole Heslo.
  4. Stiskněte klávesu `Enter`.
* **Očekávaný výsledek:**
  - Fokus se korektně přesune z pole e-mailu na heslo.
  - Stisk `Enter` formulář odešle a provede přihlášení.

#### `TC-11-AUTH`: Bezpečné odhlášení ze systému
* **Pokrytí:** US-03, AK-1, AK-2, AK-3, AK-4
* **Předpoklady:** Uživatel je přihlášen.
* **Kroky:**
  1. V horní navigační liště klikněte na tlačítko „Odhlásit se“.
  2. Po přesměrování zkuste stisknout tlačítko „Zpět“ v prohlížeči nebo přejít přímo na URL chráněné sekce (např. `/profil`).
* **Očekávaný výsledek:**
  - Uživatelské sezení je okamžitě ukončeno.
  - Uživatel je přesměrován na veřejnou stránku (katalog).
  - V navigaci se opět zobrazuje volba pro přihlášení.
  - Návrat na privátní stránku je odmítnut.

#### `TC-12-AUTH`: Odeslání platné žádosti o reset hesla
* **Pokrytí:** US-04, AK-1, AK-4
* **Předpoklady:** Uživatel je na stránce zapomenutého hesla `/obnova-hesla`. V systému existuje e-mail `student@kitner.cz`.
* **Kroky:**
  1. Do pole E-mail zadejte `student@kitner.cz`.
  2. Klikněte na „Odeslat žádost o obnovu“.
* **Očekávaný výsledek:**
  - Systém vygeneruje bezpečný resetovací odkaz.
  - Zobrazí se potvrzovací hlášení o odeslání instrukcí k obnově hesla na zadaný e-mail.

#### `TC-13-AUTH`: Žádost o reset s neplatným / prázdným e-mailem
* **Pokrytí:** US-04, AK-2, AK-3
* **Předpoklady:** Uživatel je na `/obnova-hesla`.
* **Kroky:**
  1. Ponechte pole e-mail prázdné a odešlete.
  2. Zadejte neplatný e-mail `chybny-format` a odešlete.
* **Očekávaný výsledek:**
  - Systém formulář neodešle a zobrazí validační chybu o neplatném formátu e-mailu.

#### `TC-14-AUTH`: Úspěšná změna hesla pomocí platného tokenu
* **Pokrytí:** US-05, AK-2, AK-4
* **Předpoklady:** Uživatel otevře odkaz s platným resetovacím tokenem `/reset-hesla?token=PLATNY_TOKEN`.
* **Kroky:**
  1. Zadejte nové heslo `NoveSuperHeslo123`.
  2. Zadejte totéž heslo do potvrzovacího pole.
  3. Klikněte na „Uložit nové heslo“.
* **Očekávaný výsledek:**
  - Nové heslo je uloženo do systému.
  - Zobrazí se zpráva o úspěšné změně s odkazem na přihlášení.
  - Uživatel se nyní může úspěšně přihlásit novým heslem.

#### `TC-15-AUTH`: Změna hesla s neplatným nebo expirovaným tokenem
* **Pokrytí:** US-05, AK-1, AK-5
* **Předpoklady:** Otevřen odkaz s neplatným nebo expirovaným tokenem `/reset-hesla?token=NEPLATNY_NEBO_VYPRSENY`.
* **Kroky:**
  1. Otevřete odkaz `/reset-hesla?token=NEPLATNY_NEBO_VYPRSENY`.
  2. Vyplňte pole nového hesla a klikněte na „Uložit nové heslo“.
* **Očekávaný výsledek:**
  - Změna hesla je zamítnuta.
  - Systém zobrazí chybové hlášení o neplatnosti nebo expiraci odkazu.

#### `TC-16-AUTH`: Změna hesla s neshodným potvrzením
* **Pokrytí:** US-05, AK-3
* **Předpoklady:** Platný resetovací token.
* **Kroky:**
  1. Zadejte do nového hesla `HesloA` a do potvrzení `HesloB`.
  2. Klikněte na „Uložit nové heslo“.
* **Očekávaný výsledek:**
  - Systém požadavek zamítne a zobrazí chybu neshody hesel.

#### `TC-17-AUTH`: Úspěšné ověření e-mailu přes platný odkaz
* **Pokrytí:** US-06, AK-1, AK-2
* **Předpoklady:** Uživatel má čerstvě registrovaný účet s neověřeným e-mailem a obdržel platný odkaz.
* **Kroky:**
  1. Otevřete v prohlížeči platný verifikační odkaz `/overeni-emailu?token=PLATNY_VERIFIKACNI_TOKEN`.
  2. Zkontrolujte reakci rozhraní a potvrzení o úspěšném ověření účtu.
* **Očekávaný výsledek:**
  - E-mail uživatele je označen jako ověřený.
  - Zobrazí se informace o úspěšném ověření e-mailu.

#### `TC-18-AUTH`: Ověření e-mailu s neplatným odkazem
* **Pokrytí:** US-06, AK-3
* **Předpoklady:** Uživatel disponuje neplatným, pozměněným nebo expirovaným verifikačním tokenem.
* **Kroky:**
  1. Otevřete v prohlížeči neplatný verifikační odkaz `/overeni-emailu?token=NEPLATNY_TOKEN`.
  2. Zkontrolujte odmítnutí požadavku a zobrazení chybového hlášení.
* **Očekávaný výsledek:**
  - Systém požadavek odmítne a zobrazí informaci o neplatném či expirovaném ověřovacím odkazu.

#### `TC-19-AUTH`: Znovuzaslání ověřovacího e-mailu a rate limit
* **Pokrytí:** US-06, AK-4, AK-5
* **Předpoklady:** Přihlášený uživatel s neověřeným e-mailem.
* **Kroky:**
  1. V rozhraní klikněte na „Znovu odeslat ověřovací e-mail“.
  2. Zkontrolujte odeslání.
  3. Okamžitě klikněte na tlačítko znovu.
* **Očekávaný výsledek:**
  - První požadavek odešle nový e-mail.
  - Druhý okamžitý požadavek je omezen časovým limitem (ochrana proti zahlcení).

#### `TC-20-AUTH`: Dočasná blokace po 5 neúspěšných pokusech o přihlášení
* **Pokrytí:** US-07, AK-1, AK-2, AK-3
* **Předpoklady:** Uživatel je na přihlašovací stránce.
* **Kroky:**
  1. Zadejte existující e-mail a chybné heslo.
  2. Odešlete formulář celkem 5× za sebou.
  3. Proveďte 6. pokus o přihlášení.
* **Očekávaný výsledek:**
  - Po 5. neúspěšném pokusu systém zablokuje další přihlašování.
  - Při 6. pokusu se zobrazí chybová zpráva o dočasném zablokování s uvedením počtu sekund, po které musí vyčkat.

#### `TC-21-AUTH`: Vynulování počítadla po úspěšném přihlášení
* **Pokrytí:** US-07, AK-4
* **Předpoklady:** Uživatel provedl 3 neúspěšné pokusy o přihlášení.
* **Kroky:**
  1. Při 4. pokusu zadejte správné heslo a přihlaste se.
  2. Odhlaste se.
  3. Proveďte další 3 neúspěšné pokusy.
* **Očekávaný výsledek:**
  - Úspěšným přihlášením se počítadlo neúspěchů vynulovalo, takže uživatel není zablokován po celkových 6 neúspěšných pokusech rozdělených úspěšným přihlášením.

---

### Modul 2: Katalog a detail kurzů (CRS)

#### `TC-22-CRS`: Zobrazení katalogu kurzů pro nepřihlášeného návštěvníka
* **Pokrytí:** US-08, AK-1, AK-5
* **Předpoklady:** Nepřihlášený uživatel otevře hlavní stránku katalogu kurzů `/kurzy`.
* **Kroky:**
  1. Zkontrolujte přítomnost karet všech nabízených kurzů.
  2. Zkontrolujte dolní část stránky.
* **Očekávaný výsledek:**
  - Všechny aktivní kurzy jsou přehledně zobrazeny.
  - Pod nabídkou kurzů se zobrazuje výzva k registraci s přímým odkazem na registrační formulář.

#### `TC-23-CRS`: Ověření zobrazení atributů kurzu v katalogu
* **Pokrytí:** US-08, AK-2, AK-3, AK-4
* **Předpoklady:** Otevřen katalog kurzů.
* **Kroky:**
  1. Prohlédněte jednotlivé karty kurzů v katalogu a zkontrolujte název, popis, kapacitu a zaokrouhlenou cenu.
  2. Zkontrolujte přítomnost náhledového obrázku a ověřte klikatelnost odkazu na detail kurzu.
* **Očekávaný výsledek:**
  - Každá karta obsahuje název kurzu, stručný popis, maximální kapacitu účastníků.
  - Cena je zobrazena ve formátu zaokrouhleném na celé koruny (např. `12 500 Kč`).
  - U kurzů bez vlastního obrázku je zobrazen výchozí neutrální zástupný obrázek.
  - Z každé karty vede funkční odkaz na detail kurzu.

#### `TC-24-CRS`: Zobrazení detailu kurzu a seznamu vypsaných termínů
* **Pokrytí:** US-09, AK-1, AK-2, AK-3, AK-4
* **Předpoklady:** V katalogu kurzů klikněte na libovolný kurz.
* **Kroky:**
  1. Zkontrolujte obsah stránky detailu kurzu.
  2. Zkontrolujte sekci vypsaných běhů (termínů).
* **Očekávaný výsledek:**
  - Zobrazí se plný název, podrobný popis, obrázek a cena.
  - Sekce termínů obsahuje seznam běhů s datem začátku, konce a poměrem obsazenosti (např. `3/12`).
  - Nepřihlášenému návštěvníkovi se zobrazí výzva k přihlášení/vytvoření účtu.

#### `TC-25-CRS`: Zobrazení tlačítka zápisu u termínu s volnou kapacitou
* **Pokrytí:** US-10, AK-1, AK-2
* **Předpoklady:** Přihlášen uživatel v roli Zákazník na detailu kurzu, který má vypsaný termín s volnou kapacitou (např. 2/10).
* **Kroky:**
  1. Zkontrolujte řádek daného termínu.
  2. Klikněte na tlačítko zápisu/registrace.
* **Očekávaný výsledek:**
  - U volného termínu je viditelné tlačítko „Zapsat se na kurz“.
  - Kliknutím je zákazník přesměrován do objednávkového formuláře daného běhu.

#### `TC-26-CRS`: Zamezení registrace a indikace plně obsazeného běhu
* **Pokrytí:** US-10, AK-3
* **Předpoklady:** Přihlášen zákazník na detailu kurzu, kde je termín s plnou kapacitou (např. 12/12).
* **Kroky:**
  1. Na detailu kurzu vyhledejte termín s plně obsazenou kapacitou (např. 12/12).
  2. Zkontrolujte vizuální indikaci termínu a stav tlačítka pro registraci.
* **Očekávaný výsledek:**
  - Tlačítko pro registraci se nezobrazuje.
  - Běh je vizuálně označen jako „Plně obsazeno“ / „Kapacita naplněna“.

---

### Modul 3: Zápis na kurz a Moje kurzy (Role: Zákazník) (ENR)

#### `TC-27-ENR`: Úspěšný zápis na kurz s platným telefonem a platným IČO
* **Pokrytí:** US-11, AK-1, AK-5, AK-6, AK-7
* **Předpoklady:** Přihlášený zákazník na objednávkovém formuláři volného běhu kurzu.
* **Testovací data:** Telefon: `+420 777 123 456` (nebo `777123456`), IČO: `25596641` (platné 8místné IČO splňující modulo 11).
* **Kroky:**
  1. Zadejte telefonní číslo.
  2. Zadejte platné IČO.
  3. Klikněte na tlačítko „Potvrdit nezávaznou registraci“.
* **Očekávaný výsledek:**
  - Formulář projde validací.
  - IČO a telefon se uloží do profilu uživatele.
  - Vytvoří se zápis zákazníka na daný běh kurzu.
  - Zákazník obdrží potvrzení o registraci a je přesměrován do sekce „Moje kurzy“.

#### `TC-28-ENR`: Úspěšný zápis na kurz bez vyplněného IČO
* **Pokrytí:** US-11, AK-1, AK-3
* **Předpoklady:** Přihlášený zákazník na formuláři zápisu.
* **Testovací data:** Telefon: `777123456`, pole IČO ponecháno prázdné.
* **Kroky:**
  1. Vyplňte pouze telefon.
  2. Klikněte na „Potvrdit nezávaznou registraci“.
* **Očekávaný výsledek:**
  - Protože IČO je nepovinné, registrace proběhne úspěšně a uživatel je zapsán.
* **Poznámka / Defekt:** V testovacím prostředí aplikace chybně vyžaduje IČO jako povinné a hlásí „Neplatné IČO“ (evidováno jako BR-04, test v kódu označen @pytest.mark.xfail).

#### `TC-29-ENR`: Zápis s neplatným IČO (chyba kontrolního součtu modulo 11)
* **Pokrytí:** US-11, AK-3, AK-4
* **Předpoklady:** Přihlášený zákazník na formuláři zápisu.
* **Testovací data:** Telefon: `777123456`, Neplatné IČO: `12345678` (nevyhovuje algoritmu kontrolního součtu) nebo text `ABCDEFGH`.
* **Kroky:**
  1. Zadejte platný telefon.
  2. Zadejte neplatné IČO `12345678`.
  3. Klikněte na „Potvrdit nezávaznou registraci“.
* **Očekávaný výsledek:**
  - Registrace se neprovede.
  - U pole IČO se zobrazí chybová hláška informující o neplatném formátu či neplatném kontrolním součtu IČO.

#### `TC-30-ENR`: Zápis s neplatným telefonem (méně než 9 číslic)
* **Pokrytí:** US-11, AK-2, AK-4
* **Předpoklady:** Přihlášený zákazník na formuláři zápisu.
* **Testovací data:** Telefon: `12345` (méně než 9 číslic).
* **Kroky:**
  1. Do pole telefon zadejte `12345`.
  2. Klikněte na „Potvrdit nezávaznou registraci“.
* **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Zobrazí se validační chyba vyžadující platné telefonní číslo o délce minimálně 9 číslic.

#### `TC-31-ENR`: Zobrazení přehledu mých zapsaných kurzů
* **Pokrytí:** US-12, AK-1, AK-2, AK-3, AK-4, AK-5, AK-6, AK-7, AK-8
* **Předpoklady:** Přihlášen zákazník, který má alespoň jeden zapsaný běh kurzu.
* **Kroky:**
  1. V horní navigaci klikněte na položku „Moje kurzy“.
  2. Zkontrolujte přehled kurzů.
* **Očekávaný výsledek:**
  - Zobrazí se seznam všech kurzů zapsaných přihlášeným uživatelem.
  - U každého kurzu jsou viditelné organizační údaje: datum 1. a poslední lekce, den v týdnu a čas lekcí, forma výuky/adresa.
  - Z každé položky lze kliknout na detail kurzu.

#### `TC-48-ENR`: Zobrazení sekce Moje kurzy bez aktivních zápisů (Empty State)
* **Pokrytí:** US-12, AK-1, AK-2
* **Předpoklady:** V systému je přihlášen zákazník, který nemá zapsán žádný běh kurzu (např. čerstvě registrovaný účet).
* **Testovací data:** Nově vytvořený uživatelský účet bez provedeného zápisu na kurz.
* **Kroky:**
  1. V horní navigaci klikněte na položku „Moje kurzy“ (`/my-courses`).
  2. Zkontrolujte zobrazenou stránku a obsah sekce přehledu.
* **Očekávaný výsledek:**
  - Uživatel je úspěšně přesměrován na URL `/my-courses`.
  - V horní navigaci je indikován přihlášený stav (tlačítko „Odhlásit se“).
  - Nadpis sekce „Mé zapsané kurzy“ je zobrazen.
  - V přehledu se nenachází žádná karta kurzu (`course_\d+`).
  - Stránka nevykazuje žádné vizuální chyby ani rozpad layoutu.

---

### Modul 4: Správa kurzů a výuky (Role: Lektor) (LEC)

#### `TC-32-LEC`: Úspěšné vytvoření kurzu lektorem s obrázkem 16:9
* **Pokrytí:** US-13, AK-1, AK-2, AK-4, AK-6
* **Předpoklady:** Přihlášen uživatel v roli Lektor na stránce tvorby kurzu `/lektor/novy-kurz`.
* **Testovací data:** Název: `Automatizované testování v Playwrightu`, Popis: `Kompletní kurz pro pokročilé testery`, Kapacita: `15`, Cena: `14900`, Obrázek: `preview_16_9.jpg` (rozlišení např. 1920x1080 = poměr 16:9).
* **Kroky:**
  1. Vyplňte název, popis, kapacitu a cenu.
  2. Nahrajte obrázek se správným poměrem stran 16:9.
  3. Klikněte na „Vytvořit kurz“.
* **Očekávaný výsledek:**
  - Kurz je vytvořen a uložen.
  - Lektor je přesměrován do přehledu kurzů a kurz je zařazen do katalogu.

#### `TC-33-LEC`: Odmítnutí náhledu kurzu s nevyhovujícím poměrem stran
* **Pokrytí:** US-13, AK-5
* **Předpoklady:** Přihlášen lektor na formuláři tvorby kurzu.
* **Testovací data:** Obrázek čtvercový `square_1_1.jpg` (poměr 1:1, odchylka od 16:9 je výrazně vyšší než 5 %).
* **Kroky:**
  1. Vyplňte povinná pole kurzu.
  2. Nahrajte čtvercový obrázek `1:1`.
  3. Klikněte na „Vytvořit kurz“.
* **Očekávaný výsledek:**
  - Systém nahrání odmítne.
  - Zobrazí se chybová hláška požadující širokoúhlý formát přibližně 16:9 s povolenou odchylkou do 5 %.

#### `TC-34-LEC`: Validace povinných polí a číselné kapacity/ceny
* **Pokrytí:** US-13, AK-2, AK-3
* **Předpoklady:** Přihlášen lektor na formuláři tvorby kurzu.
* **Testovací data:** Kapacita: `-5` nebo text `deset`, Cena: `zdarma`.
* **Kroky:**
  1. Zadejte zápornou nebo nečíselnou kapacitu a cenu.
  2. Klikněte na „Vytvořit kurz“.
* **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Systém zobrazí validační chybu: kapacita musí být kladné celé číslo a cena číselná hodnota.

#### `TC-35-LEC`: Úspěšné vypsání nového termínu kurzu lektorem
* **Pokrytí:** US-14, AK-1, AK-2, AK-4, AK-5
* **Předpoklady:** Přihlášen lektor u existujícího kurzu.
* **Testovací data:** Datum začátku: `01.12.2026`, Datum konce: `20.12.2026`, Den: `Úterý`, Čas: `18:00`, Místo: `Online (Google Meet)`.
* **Kroky:**
  1. Otevřete formulář nového termínu kurzu (`/courses/:id/create-iteration`).
  2. Vyplňte všechna povinná pole rozvrhu (datum začátku, konce, den, čas, místo).
  3. Klikněte na tlačítko „Přidat iteraci“.
* **Očekávaný výsledek:**
  - Termín je uložen a přiřazen ke kurzu.
  - Lektor je přesměrován na detail kurzu, kde je nový termín zobrazen.

#### `TC-36-LEC`: Validace povinných polí při vypsání termínu
* **Pokrytí:** US-14, AK-3
* **Předpoklady:** Přihlášen lektor na formuláři nového termínu (`/courses/:id/create-iteration`).
* **Kroky:**
  1. Na formuláři nového termínu ponechte pole pro data nebo čas prázdná.
  2. Klikněte na tlačítko „Přidat iteraci“.
* **Očekávaný výsledek:**
  - Systém zobrazí validační chyby u nevyplněných povinných polí a formulář zůstane zobrazen.
* **Poznámka / Defekt:** Aplikace v testovacím prostředí odesílá formulář termínu bez klientské validace povinných polí (test v kódu označen @pytest.mark.xfail).

#### `TC-37-LEC`: Zobrazení tabulky přihlášených účastníků pro lektora
* **Pokrytí:** US-15, AK-1, AK-2, AK-3
* **Předpoklady:** Přihlášen lektor na detailu kurzu, kde jsou zapsaní studenti (student A s IČO, student B bez IČO).
* **Kroky:**
  1. U daného běhu klikněte na „Zobrazit účastníky“.
  2. Zkontrolujte zobrazenou tabulku.
* **Očekávaný výsledek:**
  - Tabulka přehledně zobrazuje jméno, příjmení, e-mail, telefon a IČO každého studenta.
  - U studenta B, který IČO nezadal, je v buňce IČO zobrazen text „Neuvedeno“.

#### `TC-38-LEC`: Zamezení přístupu k účastníkům pro zákazníka
* **Pokrytí:** US-15, AK-4
* **Předpoklady:** Přihlášen běžný uživatel v roli Zákazník.
* **Kroky:**
  1. Přihlaste se jako zákazník a do adresního řádku zadejte URL seznamu účastníků `/lektor/beh/123/ucastnici`.
  2. Potvrďte načtení stránky a ověřte reakci systému na nepovolený přístup.
* **Očekávaný výsledek:**
  - Přístup je odmítnut (zobrazí se chybová stránka 403 Forbidden nebo přesměrování).
  - Citlivé osobní a fakturační údaje studentů nejsou zákazníkovi zobrazeny.

---

### Modul 5: Uživatelský profil a domovská nástěnka (PRF)

#### `TC-39-PRF`: Zobrazení personalizovaného uvítání na nástěnce
* **Pokrytí:** US-16, AK-1, AK-2
* **Předpoklady:** Uživatel se jménem `Andrea Wanková` se přihlásí do aplikace.
* **Kroky:**
  1. Zkontrolujte obsah po přesměrování na domovskou stránku.
  2. Klikněte v navigaci na odkaz „Domů“.
* **Očekávaný výsledek:**
  - Nástěnka zobrazuje personalizované uvítání obsahující jméno uživatele (např. `Vítejte zpět, Andrea Wanková!`).
  - Stránka je kdykoliv dostupná z horní navigace přes tlačítko „Domů“.

#### `TC-40-PRF`: Úspěšná aktualizace údajů profilu
* **Pokrytí:** US-17, AK-1, AK-3, AK-6
* **Předpoklady:** Přihlášený uživatel přejde do sekce „Můj profil“ `/profil`.
* **Kroky:**
  1. Zkontrolujte předvyplněná data (jméno, e-mail).
  2. Změňte telefon na `+420 777 999 888`.
  3. Zadejte platné IČO `25596641`.
  4. Klikněte na „Uložit profil“.
* **Očekávaný výsledek:**
  - Zobrazí se potvrzovací hláška o úspěšné aktualizaci profilu.
  - Uživatel je přesměrován na domovskou stránku a nová data zůstávají uložena.

#### `TC-41-PRF`: Validace formátu IČO a telefonu v profilu
* **Pokrytí:** US-17, AK-4, AK-5
* **Předpoklady:** Přihlášený uživatel v editaci profilu.
* **Kroky:**
  1. Zadejte neplatné IČO (např. `99999999`) a neplatný telefon `123`.
  2. Klikněte na „Uložit profil“.
* **Očekávaný výsledek:**
  - Profil se neuloží a systém zobrazí validační chyby u obou neplatných polí.

#### `TC-42-PRF`: Pokus o změnu e-mailu na již obsazenou adresu
* **Pokrytí:** US-17, AK-2
* **Předpoklady:** V systému existuje jiný uživatel s e-mailem `druhy@example.com`.
* **Kroky:**
  1. V profilu změňte svůj e-mail na `druhy@example.com`.
  2. Klikněte na „Uložit profil“.
* **Očekávaný výsledek:**
  - Změna je zamítnuta s chybovou zprávou, že e-mail je již používán jiným účtem.

---

### Modul 6: Bezpečnost a autorizace (Security & Architecture) (SEC)

#### `TC-43-SEC`: Přesměrování nepřihlášeného uživatele z privátních URL
* **Pokrytí:** US-18, AK-1, AK-2, AK-6, AK-7
* **Předpoklady:** Uživatel není přihlášen.
* **Kroky:**
  1. Zkuste v prohlížeči přímo otevřít URL `/profil`.
  2. Zkuste přímo otevřít URL `/moje-kurzy`.
* **Očekávaný výsledek:**
  - Neautentizovaný přístup je zablokován.
  - Uživatel je automaticky přesměrován na katalog kurzů `/kurzy` nebo na přihlašovací formulář.

#### `TC-44-SEC`: Zákaz lektorských operací pro zákazníka
* **Pokrytí:** US-18, AK-3, AK-4
* **Předpoklady:** Přihlášen uživatel v roli Zákazník.
* **Kroky:**
  1. Zadejte do adresního řádku URL pro vytvoření kurzu `/lektor/novy-kurz`.
  2. Zkuste odeslat POST požadavek na lektorský API endpoint.
* **Očekávaný výsledek:**
  - Požadavek je odmítnut s chybou 403 Forbidden nebo přesměrováním s upozorněním na nedostatečná oprávnění.

#### `TC-45-SEC`: Zákaz zápisu na kurz pro lektora
* **Pokrytí:** US-18, AK-5
* **Předpoklady:** Přihlášen uživatel v roli Lektor.
* **Kroky:**
  1. Přihlaste se jako lektor a otevřete detail vybraného kurzu.
  2. Zkontrolujte vypsané termíny a pokuste se odeslat požadavek zápisu na běh kurzu.
* **Očekávaný výsledek:**
  - Možnost zápisu na běh kurzu se lektorovi nenabízí (zápis je vyhrazen zákazníkům).
  - Pokud lektor zkusí odeslat požadavek zápisu přímo, je systémem zamítnut.

#### `TC-46-SEC`: Ochrana formulářů CSRF tokenem
* **Pokrytí:** US-19, AK-1, AK-2
* **Předpoklady:** Otevřen libovolný stavový formulář (přihlášení, registrace, profil, zápis na kurz).
* **Kroky:**
  1. Zkontrolujte přítomnost skrytého bezpečnostního CSRF tokenu v kódu formuláře.
  2. Zkuste odeslat formulář s odstraněným nebo pozměněným CSRF tokenem.
* **Očekávaný výsledek:**
  - Všechny formuláře obsahují platný CSRF token.
  - Požadavek s chybějícím nebo neplatným tokenem server striktně odmítne (HTTP 403 / CSRF Error).

#### `TC-47-SEC`: Regenerace session ID při přihlášení a odhlášení
* **Pokrytí:** US-19, AK-3
* **Předpoklady:** Otevřená session před přihlášením.
* **Kroky:**
  1. Zaznamenejte si hodnotu session cookie před přihlášením.
  2. Přihlaste se do aplikace a porovnejte hodnotu session cookie.
  3. Odhlaste se a porovnejte hodnotu session cookie.
* **Očekávaný výsledek:**
  - Při každé změně autentizačního stavu (login i logout) systém vygeneruje zcela nové session ID (ochrana proti Session Fixation).
