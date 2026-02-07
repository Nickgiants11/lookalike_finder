"""
Clean First Name utility for BuzzLead waterfall enrichment.
Handles edge cases: parentheses, quotes, Dr. prefix, emojis, accented chars, ALL CAPS, etc.
"""

import re
import unicodedata
from typing import Optional


def clean_first_name(raw_name: Optional[str]) -> str:
    """
    Clean and normalize a first name field.
    
    Handles:
    - Parenthetical preferred names: "John (Johnny)" → "Johnny"
    - Quoted preferred names: '"Nick" John' → "Nick"
    - Dr./Doctor prefix: "Dr. John Smith" → "Dr. John"
    - Emojis and special characters: "John 🚀" → "John"
    - Accented characters: "José" → "José" (preserved)
    - ALL CAPS: "JOHN" → "John"
    - Single-letter initials: "J. Robert" → "Robert"
    - Hyphenated names: "Mary-Jane" → "Mary-Jane"
    
    Returns:
        Cleaned first name in Title Case, or empty string if invalid
    """
    if not raw_name:
        return ""
    
    name = str(raw_name).strip()
    if not name:
        return ""
    
    # === STEP 1: Check for parenthetical preferred name ===
    # "John (Johnny) Smith" → "Johnny"
    paren_match = re.search(r'\(([^)]+)\)', name)
    if paren_match:
        name = paren_match.group(1).strip()
    
    # === STEP 2: Check for quoted preferred name ===
    # "Nick" John or 'Nick' John or "Nick" or "Nick" → Nick
    elif re.search(r'["\'""]', name):
        quote_match = re.search(r'["\'""]([^"\'""]+)["\'""]', name)
        if quote_match:
            name = quote_match.group(1).strip()
    
    # === STEP 3: Check for Dr./Doctor prefix ===
    dr_prefix = ""
    dr_match = re.match(r'^\s*(dr\.?|doctor)\s+', name, re.IGNORECASE)
    if dr_match:
        dr_prefix = "Dr. "
        name = name[dr_match.end():].strip()
    
    # === STEP 4: Remove emojis and weird unicode ===
    # Keep letters (including accented), spaces, apostrophes, hyphens, periods
    cleaned = ""
    for char in name:
        cat = unicodedata.category(char)
        # L = Letter, Zs = Space separator, also allow specific punctuation
        if cat.startswith('L') or cat == 'Zs' or char in " '-.\u2019":  # \u2019 is '
            cleaned += char
    name = cleaned
    
    # === STEP 5: Normalize whitespace ===
    name = re.sub(r'\s+', ' ', name).strip()
    
    if not name:
        return ""
    
    # === STEP 6: Split into words and find the first "real" name ===
    words = name.split()
    
    # Filter out single-letter initials (J. or J)
    real_words = [w for w in words if not re.match(r'^[A-Za-z]\.?$', w)]
    
    # Also filter out common suffixes that might appear
    suffixes = {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii', 'iv', 'v'}
    real_words = [w for w in real_words if w.lower() not in suffixes]
    
    if not real_words:
        # Fall back to first word if all were filtered
        real_words = words
    
    first_name = real_words[0] if real_words else ""
    
    if not first_name:
        return ""
    
    # === STEP 7: Title case (handles ALL CAPS and all lowercase) ===
    # Special handling for hyphenated names: Mary-Jane → Mary-Jane
    def title_case_word(word):
        if '-' in word:
            return '-'.join(part.capitalize() for part in word.split('-'))
        # Handle apostrophes: O'Brien → O'Brien, not O'brien
        if "'" in word or "'" in word:
            parts = re.split(r"(['\'])", word)
            result = ""
            for i, part in enumerate(parts):
                if part in ("'", "'"):
                    result += part
                elif i == 0 or (i > 0 and parts[i-1] in ("'", "'")):
                    result += part.capitalize()
                else:
                    result += part.lower()
            return result
        return word.capitalize()
    
    first_name = title_case_word(first_name)
    
    # === STEP 8: Add back Dr. prefix if present ===
    return dr_prefix + first_name


# === TESTS ===
if __name__ == "__main__":
    test_cases = [
        ("John", "John"),
        ("john", "John"),
        ("JOHN", "John"),
        ("John (Johnny) Smith", "Johnny"),
        ('"Nick" John', "Nick"),
        ("'Bobby' Robert", "Bobby"),
        ("\u201cPreferred\u201d Name", "Preferred"),
        ("Dr. John Smith", "Dr. John"),
        ("Doctor Jane Doe", "Dr. Jane"),
        ("dr john", "Dr. John"),
        ("John 🚀 Smith", "John"),
        ("🚀 John", "John"),
        ("José García", "José"),
        ("François", "François"),
        ("J. Robert Smith", "Robert"),
        ("Mary-Jane Watson", "Mary-Jane"),
        ("mary-jane", "Mary-Jane"),
        ("O'Brien", "O'Brien"),
        ("o'connor", "O'Connor"),
        ("John Jr.", "John"),
        ("III John", "John"),
        ("  John  ", "John"),
        ("", ""),
        (None, ""),
        ("J.", "J."),  # Edge case: only initial
    ]
    
    print("Testing clean_first_name():\n")
    passed = 0
    failed = []
    for raw, expected in test_cases:
        result = clean_first_name(raw)
        if result == expected:
            passed += 1
            print(f"✓ {repr(raw)} → {repr(result)}")
        else:
            failed.append((raw, expected, result))
            print(f"✗ {repr(raw)} → {repr(result)} (expected {repr(expected)})")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")
    
    if failed:
        print("\nFailed tests:")
        for raw, expected, result in failed:
            print(f"  {repr(raw)} → {repr(result)} (expected {repr(expected)})")
