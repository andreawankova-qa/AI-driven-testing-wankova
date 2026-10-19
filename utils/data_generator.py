"""
Generátor náhodných a dynamických testovacích dat a načítání externích datových sad.
Nahrazuje ad-hoc skládání řetězců a time.time() hacky.
"""

import json
import random
import string
import time
from pathlib import Path

# Cesta k adresáři s testovacími daty
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json_data(filename: str):
    """Načte a vrátí data ze zadaného JSON souboru v adresáři data/."""
    file_path = DATA_DIR / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_random_email(prefix: str = "tester") -> str:
    """Vygeneruje unikátní e-mailovou adresu na základě aktuálního časového razítka a náhodného čísla."""
    timestamp = int(time.time())
    rand_suffix = random.randint(1000, 9999)
    return f"{prefix}_{timestamp}_{rand_suffix}@kitner-test.cz"


def generate_random_password(length: int = 12) -> str:
    """Vygeneruje silné náhodné heslo obsahující velká i malá písmena a číslice."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_random_user(name_prefix: str = "Test Uživatel") -> dict:
    """Vygeneruje kompletní sadu údajů pro nového testovacího uživatele."""
    rand_id = random.randint(100, 999)
    return {
        "name": f"{name_prefix} {rand_id}",
        "email": generate_random_email(),
        "password": generate_random_password(10)
    }


def generate_valid_ico() -> str:
    """
    Vygeneruje platné 8místné IČO s kontrolním součtem podle oficiálního algoritmu modulo 11.
    """
    first_7 = [random.randint(0, 9) for _ in range(7)]
    if first_7[0] == 0:
        first_7[0] = random.randint(1, 9)
    
    weights = [8, 7, 6, 5, 4, 3, 2]
    weighted_sum = sum(d * w for d, w in zip(first_7, weights))
    rem = weighted_sum % 11
    if rem == 0:
        check_digit = 1
    elif rem == 1:
        check_digit = 0
    else:
        check_digit = 11 - rem
    
    return "".join(str(d) for d in first_7) + str(check_digit)


def generate_invalid_ico() -> str:
    """Vrátí neplatné IČO s chybným kontrolním součtem."""
    valid = generate_valid_ico()
    # Změníme poslední číslici, aby neseděl kontrolní součet
    last = int(valid[-1])
    wrong_last = (last + 1) % 10
    return valid[:-1] + str(wrong_last)

