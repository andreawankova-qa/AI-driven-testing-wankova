# Testovací případy (Test Cases) – Experimentální soubor pro US-01

Tento dokument představuje zkušební sadu manuálních testovacích případů navrženou pro **US-01: Registrace zákaznického účtu s automatickým přihlášením** ze specifikace [`docs/požadavky_ust_podle_src.md`](požadavky_ust_podle_src.md).

---

### Přehledová tabulka scénářů (US-01)

| ID testu | Akceptační kritérium | Název testovacího případu | Typ testu | Priorita |
| :--- | :--- | :--- | :--- | :--- |
| `TC-01-AUTH` | AK-1, AK-7 | Úspěšná registrace zákaznického účtu (Happy Path) | Happy Path / Pozitivní | P1 (Kritická) |
| `TC-02-AUTH` | AK-3, AK-6 | Pokus o registraci s již obsazeným e-mailem | Negativní / Validační | P2 (Vysoká) |
| `TC-03-AUTH` | AK-3, AK-6 | Registrace s neplatným formátem e-mailové adresy | Negativní / Validační | P2 (Vysoká) |
| `TC-04-AUTH` | AK-2, AK-6 | Odeslání prázdného formuláře a validace povinných polí | Negativní / Validační | P2 (Vysoká) |
| `TC-05-AUTH` | AK-5, AK-6 | Registrace s neshodujícími se hesly | Negativní / Validační | P2 (Vysoká) |
| `TC-06-AUTH` | AK-5, AK-6 | Registrace s heslem nesplňujícím minimální délku | Hraniční (BVA) / Validační | P2 (Vysoká) |
| `TC-07-AUTH` | AK-4 | Normalizace e-mailu – ořezání mezer a case-insensitivity | Hraniční (BVA) / Funkční | P3 (Střední) |
| `TC-08-AUTH` | AK-8 | Dostupnost a funkčnost odkazů pro přihlášení a obnovu hesla | Funkční / Pozitivní | P3 (Střední) |

---

### Detailní specifikace testovacích případů

#### `TC-01-AUTH`: Úspěšná registrace zákaznického účtu (Happy Path)
* **Pokrytí:** US-01 (AK-1, AK-7)
* **Typ testu:** Happy Path / Pozitivní
* **Priorita:** P1
* **Předpoklady:**
  - Uživatel není přihlášen do systému.
  - Uživatel má otevřenou registrační stránku `/register`.
  - V systému neexistuje uživatel se zadanou e-mailovou adresou.
* **Testovací data:**
  - Jméno: `Jan Novák`
  - E-mail: `jan.novak.test@example.com` (unikátní)
  - Heslo: `BezpecneHeslo123`
  - Potvrzení hesla: `BezpecneHeslo123`
* **Kroky:**
  1. Zkontrolujte, že formulář obsahuje viditelná pole pro Jméno, E-mail, Heslo a Potvrzení hesla.
  2. Do pole „Jméno“ zadejte `Jan Novák`.
  3. Do pole „E-mail“ zadejte unikátní e-mailovou adresu `jan.novak.test@example.com`.
  4. Do pole „Heslo“ zadejte `BezpecneHeslo123`.
  5. Do pole „Potvrzení hesla“ zadejte `BezpecneHeslo123`.
  6. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Zákaznický účet je úspěšně vytvořen v databázi.
  - Uživatel je automaticky přihlášen a systém ho přesměruje na domovskou stránku `/home`.
  - Na domovské stránce se zobrazí uvítací sekce s textem `Vítej uživateli Jan Novák!`.
  - V horní navigační liště je viditelné tlačítko „Odhlásit se“ (potvrzení aktivního sezení).

---

#### `TC-02-AUTH`: Pokus o registraci s již obsazeným e-mailem
* **Pokrytí:** US-01 (AK-3, AK-6)
* **Typ testu:** Negativní / Validační
* **Priorita:** P2
* **Předpoklady:**
  - Uživatel je na registrační stránce `/register`.
  - V systému již existuje registrovaný uživatel s e-mailem `existujici@example.com`.
* **Testovací data:**
  - Jméno: `Petr Novotný`
  - E-mail: `existujici@example.com` (již obsazený)
  - Heslo: `PlatneHeslo123`
  - Potvrzení hesla: `PlatneHeslo123`
* **Kroky:**
  1. Do pole „Jméno“ zadejte `Petr Novotný`.
  2. Do pole „E-mail“ zadejte již existující e-mail `existujici@example.com`.
  3. Do polí „Heslo“ a „Potvrzení hesla“ zadejte shodné heslo `PlatneHeslo123`.
  4. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Registrace se neprovede a nový účet nevznikne.
  - Uživatel zůstává na registrační stránce `/register`.
  - Pod polem pro e-mail se zobrazí chybová hláška `The email has already been taken.`.
  - Zadané hodnoty v polích Jméno a E-mail zůstávají zachovány ve formuláři.

---

#### `TC-03-AUTH`: Registrace s neplatným formátem e-mailové adresy
* **Pokrytí:** US-01 (AK-3, AK-6)
* **Typ testu:** Negativní / Validační
* **Priorita:** P2
* **Předpoklady:**
  - Uživatel má otevřenou registrační stránku `/register`.
* **Testovací data:**
  - Jméno: `Eva Testovací`
  - E-mail: `neplatny-format-bez-zavinace`
  - Heslo: `PlatneHeslo123`
  - Potvrzení hesla: `PlatneHeslo123`
* **Kroky:**
  1. Do pole „Jméno“ zadejte `Eva Testovací`.
  2. Do pole „E-mail“ zadejte neplatnou adresu bez zavináče a domény: `neplatny-format-bez-zavinace`.
  3. Do polí „Heslo“ a „Potvrzení hesla“ zadejte `PlatneHeslo123`.
  4. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Formulář se neodešle a registrace neproběhne.
  - Uživatel zůstává na registrační stránce `/register`.
  - Systém zobrazí validační chybu neplatného formátu e-mailové adresy.

---

#### `TC-04-AUTH`: Odeslání prázdného formuláře a validace povinných polí
* **Pokrytí:** US-01 (AK-2, AK-6)
* **Typ testu:** Negativní / Validační
* **Priorita:** P2
* **Předpoklady:**
  - Uživatel má otevřenou registrační stránku `/register`.
  - Formulář je ve výchozím prázdném stavu.
* **Testovací data:**
  - Všechna pole ponechána prázdná.
* **Kroky:**
  1. Ponechte všechna pole formuláře (Jméno, E-mail, Heslo, Potvrzení hesla) nevyplněná.
  2. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Formulář se neodešle a uživatel zůstává na registrační stránce `/register`.
  - Pod polem pro jméno se zobrazí chybová hláška `The name field is required.`.
  - Pod polem pro e-mail se zobrazí chybová hláška `The email field is required.`.
  - Pod polem pro heslo se zobrazí chybová hláška `The password field is required.`.

---

#### `TC-05-AUTH`: Registrace s neshodujícími se hesly
* **Pokrytí:** US-01 (AK-5, AK-6)
* **Typ testu:** Negativní / Validační
* **Priorita:** P2
* **Předpoklady:**
  - Uživatel má otevřenou registrační stránku `/register`.
* **Testovací data:**
  - Jméno: `Karel Neshodný`
  - E-mail: `karel.neshodny@example.com` (unikátní)
  - Heslo: `HesloPrvni123`
  - Potvrzení hesla: `ZcelaJineHeslo999`
* **Kroky:**
  1. Do pole „Jméno“ zadejte `Karel Neshodný`.
  2. Do pole „E-mail“ zadejte platný unikátní e-mail `karel.neshodny@example.com`.
  3. Do pole „Heslo“ zadejte `HesloPrvni123`.
  4. Do pole „Potvrzení hesla“ zadejte odlišné heslo `ZcelaJineHeslo999`.
  5. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Účet není vytvořen a uživatel zůstává na registrační stránce `/register`.
  - Pod polem pro heslo se zobrazí chybová hláška `The password field confirmation does not match.`.
  - Zadané jméno a e-mail zůstávají v polích předvyplněné.

---

#### `TC-06-AUTH`: Registrace s heslem nesplňujícím minimální délku
* **Pokrytí:** US-01 (AK-5, AK-6)
* **Typ testu:** Hraniční (BVA) / Validační
* **Priorita:** P2
* **Předpoklady:**
  - Uživatel má otevřenou registrační stránku `/register`.
  - Systém požaduje minimální délku hesla 8 znaků.
* **Testovací data:**
  - Jméno: `Kratke Heslo`
  - E-mail: `kratke.heslo@example.com` (unikátní)
  - Heslo: `1234567` (7 znaků – hodnota těsně pod hranicí)
  - Potvrzení hesla: `1234567`
* **Kroky:**
  1. Do pole „Jméno“ zadejte `Kratke Heslo`.
  2. Do pole „E-mail“ zadejte platný unikátní e-mail `kratke.heslo@example.com`.
  3. Do pole „Heslo“ zadejte 7místné heslo `1234567`.
  4. Do pole „Potvrzení hesla“ zadejte shodné 7místné heslo `1234567`.
  5. Klikněte na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek:**
  - Registrace je zamítnuta a uživatel zůstává na stránce `/register`.
  - Pod polem pro heslo se zobrazí validační zpráva `The password field must be at least 8 characters.`.

---

#### `TC-07-AUTH`: Normalizace e-mailu – ořezání mezer a case-insensitivity
* **Pokrytí:** US-01 (AK-4)
* **Typ testu:** Hraniční (BVA) / Funkční
* **Priorita:** P3
* **Předpoklady:**
  - Uživatel má otevřenou registrační stránku `/register`.
  - V systému neexistuje účet s e-mailem `normalizovany@example.com`.
* **Testovací data:**
  - Jméno: `Normalizace User`
  - E-mail se znaky a mezerami: `  NORMALIZOVANY@EXAMPLE.COM  `
  - Heslo: `PlatneHeslo123`
  - Potvrzení hesla: `PlatneHeslo123`
* **Kroky:**
  1. Do pole „Jméno“ zadejte `Normalizace User`.
  2. Do pole „E-mail“ zadejte adresu s mezerami na začátku/konci a velkými písmeny: `  NORMALIZOVANY@EXAMPLE.COM  `.
  3. Do polí hesel zadejte shodné heslo `PlatneHeslo123`.
  4. Klikněte na tlačítko „Zaregistrovat se“.
  5. Po úspěšné registraci klikněte v horní navigaci na tlačítko „Odhlásit se“.
  6. Přejděte na přihlašovací stránku `/login`.
  7. Přihlaste se s malými písmeny bez mezer: `normalizovany@example.com` a heslem `PlatneHeslo123`.
* **Očekávaný výsledek:**
  - Účet se úspěšně vytvoří a e-mail se uloží v normalizované podobě bez okrajových mezer.
  - Po odhlášení je možné se úspěšně přihlásit pomocí adresy `normalizovany@example.com`.

---

#### `TC-08-AUTH`: Dostupnost a funkčnost odkazů pro přihlášení a obnovu hesla
* **Pokrytí:** US-01 (AK-8)
* **Typ testu:** Funkční / Pozitivní
* **Priorita:** P3
* **Předpoklady:**
  - Uživatel má otevřenou registrační stránku `/register` a není přihlášen.
* **Testovací data:**
  - Žádná (navigační scénář).
* **Kroky:**
  1. Na stránce registrace lokalizujte odkaz pro přihlášení existujících uživatelů („Přihlásit se“).
  2. Klikněte na odkaz „Přihlásit se“.
  3. Zkontrolujte, že systém přesměroval uživatele na URL přihlašovací stránky `/login`.
  4. Vraťte se na registrační stránku `/register`.
  5. Lokalizujte odkaz pro obnovu zapomenutého hesla („Zapomenuté heslo“).
  6. Klikněte na odkaz pro obnovu hesla.
* **Očekávaný výsledek:**
  - Odkaz pro přihlášení úspěšně přesměruje uživatele na `/login`.
  - Odkaz pro obnovu hesla úspěšně přesměruje uživatele na stránku obnovy hesla `/forgot-password`.
  - Oba odkazy jsou plně funkční a dostupné přímo z registračního formuláře.
