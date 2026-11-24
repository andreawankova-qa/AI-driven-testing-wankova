---
name: hook-creator
description: >-
  Aktivuj tento skill VŽDY, když uživatel chce vytvořit, upravit, zkontrolovat nebo vysvětlit
  lifecycle hook v .agents/hooks.json a navázaný skript v .agents/hooks/ (např. 'vytvoř hook',
  'přidej PreToolUse guard', 'jak napsat hook', 'uprav hooks.json'). Definuje strukturu,
  I/O kontrakt, postup implementace, testování a zásady kvality hooků.
---

# 🪝 Tvorba kvalitních hooků (hook-creator)

## 📁 Umístění a pracovní adresář
- **Konfigurace:** `.agents/hooks.json` (nový hook vždy přidej jako nový top-level klíč – stávající klíče nepřepisuj).
- **Skripty:** `.agents/hooks/<nazev_hooku>.py` (nebo `.sh`).

> [!IMPORTANT]
> Pracovním adresářem při spuštění hooku je složka obsahující `hooks.json` (`.agents/`), nikoli kořen projektu. Cesty ke skriptům proto zapisuj relativně jako `./hooks/<nazev_hooku>.py`.

---

## 🎯 Lifecycle Eventy a I/O kontrakt

Vstup na **`stdin`** je JSON s klíči v **`camelCase`** (`conversationId`, `workspacePaths`, `cwd`, `hookEventName`, u tool hooků `toolCall: {id, name, args}`). Výstup na **`stdout`** musí být **výhradně jeden validní JSON objekt** (debug výpisy patří jen na `sys.stderr`).

| Událost | Struktura v `hooks.json` | Očekávaný JSON výstup (`stdout`) |
| :--- | :--- | :--- |
| **`PreToolUse`** | S `matcher` a `hooks` | `{"decision": "allow" \| "deny" \| "ask" \| "force_ask", "reason": "..."}` (volitelně `overwrite`) |
| **`PostToolUse`** | S `matcher` a `hooks` | `{}` |
| **`SessionStart`** | Ploché pole handlerů | `{"injectSteps": [...]}` |
| **`PreInvocation`** | Ploché pole handlerů | `{"injectSteps": [...], "terminationBehavior": "" \| "terminate"}` |
| **`PostInvocation`** | Ploché pole handlerů | `{"injectSteps": [...], "terminationBehavior": "" \| "force_continue" \| "terminate"}` |
| **`Stop`** | Ploché pole handlerů | `{"decision": "continue" \| "allow", "reason": "..."}` (jiná hodnota než `"continue"` zastaví běh) |

> [!NOTE]
> U `injectSteps` vyžaduje `systemMessage` vnořený objekt: `{"systemMessage": {"systemMessage": "Text instrukce"}}`. Další podporované kroky jsou `{"userMessage": "..."}` a `{"errorMessage": {"userMessage": "..."}}`.

---

## 🧩 Minimální šablony

### Konfigurace v `.agents/hooks.json` (ukázka `PreToolUse` s `matcher` vs. plochý `Stop`)
```json
{
  "nazev-guardu": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "write_file|edit_file|run_command",
        "hooks": [{ "type": "command", "command": "python3 ./hooks/nazev_guardu.py", "timeout": 10 }]
      }
    ]
  },
  "nazev-stop-hooku": {
    "Stop": [{ "type": "command", "command": "./hooks/check_done.sh", "timeout": 30 }]
  }
}
```

### Minimální Python skript (`.agents/hooks/<nazev>.py`)
```python
#!/usr/bin/env python3
import json
import sys

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        print(json.dumps({"decision": "deny", "reason": f"Chyba vstupu hooku: {exc}"}, ensure_ascii=False))
        return 0

    # Vlastní logika podle hookEventName / toolCall
    print(json.dumps({"decision": "allow"}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 🛠️ Postup tvorby (4 kroky)

1. **Vymez účel a event:** U `PreToolUse`/`PostToolUse` zvol co nejužší `matcher` regex nad názvy nástrojů (malými písmeny, např. `write_file|edit_file|run_command`; u bezpečnostních guardů pokryj i varianty `write_to_file`, `replace_file_content`, `delete_file`), aby se hook nespouštěl zbytečně.
2. **Napiš lehký skript v `.agents/hooks/`:** Zvol Python 3 (ideálně bez externích závislostí) nebo POSIX shell (u přímo spouštěného `.sh` skriptu nastav `chmod +x`).
3. **Zaregistruj v `.agents/hooks.json`:** Přidej nový top-level klíč a nastav přiměřený `timeout` (výchozí je `30` s, pro rychlé kontroly stačí `5`–`10` s). Pro ladění lze hook dočasně vypnout přes `"enabled": false`.
4. **Ověř validitu a funkčnost lokálně:** Zkontroluj syntaxi `hooks.json` a otestuj povolený i blokovaný/hraniční scénář přes `stdin`:
   ```bash
   python3 -m json.tool .agents/hooks.json > /dev/null
   echo '{"hookEventName": "PreToolUse", "toolCall": {"name": "write_file", "args": {"Path": "tests/test_x.py"}}, "cwd": ".", "workspacePaths": ["."]}' | python3 .agents/hooks/nazev.py
   ```

---

## ✅ Zásady kvality a specifika

- **Synchronní běh a rychlost:** Hooky blokují smyčku agenta – drž dobu běhu v milisekundách a vyhni se síťovým voláním.
- **Ochrana před smyčkou u `Stop` hooku:** Vždy kontroluj `payload.get("continuationActive")` (pokud je `true`, hook už agenta jednou vrátil a nesmí ho blokovat znovu) a respektuj `terminationReason` (při `USER_CANCELED` či `ERROR` nepokračuj).
- **Fail-closed vs. Fail-open:** Bezpečnostní guardy při chybě parsování vrací `"deny"` (fail-closed); informativní nebo formátovací hooky vrací `"allow"` / `{}` (fail-open).
- **Tipy pro `PreToolUse` ochranu souborů:** Cesty normalizuj přes `os.path.realpath` vůči `cwd` i `workspacePaths`, u souborových nástrojů kontroluj více klíčů (`Path`, `TargetFile`, `path`, `file_path`) a u `run_command` rozděluj příkaz na segmenty (`&&`, `||`, `;`, `|`, `\n`) včetně přesměrování (`>`, `>>`).
- **Referenční implementace:** [protect_test_cases.py](../../hooks/protect_test_cases.py) a [hooks.json](../../hooks.json).
