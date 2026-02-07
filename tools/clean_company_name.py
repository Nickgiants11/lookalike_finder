"""
Clean Company Name utility for BuzzLead waterfall enrichment.
Removes legal suffixes, normalizes formatting, handles edge cases.
"""

import re
from typing import Optional


# Comprehensive list of legal suffixes to remove (case-insensitive)
LEGAL_SUFFIXES = [
    # English
    r"inc\.?", r"incorporated", r"corp\.?", r"corporation", r"company", r"co\.?",
    r"llc", r"l\.l\.c\.?", r"llp", r"l\.l\.p\.?", r"lp", r"l\.p\.?",
    r"ltd\.?", r"limited", r"plc", r"p\.l\.c\.?",
    r"holdings?", r"enterprises?", r"group", r"intl\.?", r"international",
    # German
    r"gmbh", r"g\.m\.b\.h\.?", r"ag", r"a\.g\.?", r"kg", r"k\.g\.?", r"ohg", r"ug",
    # French
    r"sarl", r"s\.a\.r\.l\.?", r"sas", r"s\.a\.s\.?", r"sa", r"s\.a\.?", r"snc", r"sci",
    # Spanish/Portuguese
    r"s\.l\.?", r"sl", r"s\.a\.?", r"ltda\.?", r"cia\.?",
    # Italian
    r"spa", r"s\.p\.a\.?", r"srl", r"s\.r\.l\.?", r"snc",
    # Dutch/Belgian
    r"bv", r"b\.v\.?", r"nv", r"n\.v\.?", r"bvba", r"cvba",
    # Nordic
    r"ab", r"a\.b\.?", r"as", r"a\.s\.?", r"oy", r"oyj", r"aps",
    # Czech/Slovak
    r"s\.r\.o\.?", r"sro", r"a\.s\.?", r"spol\.?\s*s\s*r\.?\s*o\.?",
    # Asian
    r"pte\.?\s*ltd\.?", r"pty\.?\s*ltd\.?", r"pvt\.?\s*ltd\.?",
    r"kk", r"k\.k\.?", r"kabushiki\s*kaisha", r"gk", r"g\.k\.?",
    # Australian
    r"pty", r"proprietary",
    # Indian
    r"pvt\.?", r"private",
    # Other
    r"psc", r"pc", r"pllc", r"professional",
]

# Words to remove if at the end
END_WORDS_TO_STRIP = [
    r"and", r"&", r"the",
]


def clean_company_name(raw_name: Optional[str]) -> str:
    """
    Clean and normalize a company name field.
    
    Handles:
    - Legal suffixes: "Acme Inc." → "Acme"
    - Parenthetical notes: "Acme Corp (formerly XYZ)" → "Acme"
    - Comma separation: "Acme, Inc." → "Acme"
    - ALL CAPS: "ACME CORPORATION" → "Acme"
    - "The" prefix: "The Coca-Cola Company" → "Coca-Cola"
    - DBA names: "Acme Corp DBA Cool Brand" → "Acme" (keeps legal name)
    - Special characters and emojis
    - Trailing punctuation: "Acme," → "Acme"
    
    Returns:
        Cleaned company name in Title Case, or empty string if invalid
    """
    if not raw_name:
        return ""
    
    name = str(raw_name).strip()
    if not name:
        return ""
    
    # === STEP 1: Remove ALL parenthetical content ===
    # "Acme Corp (formerly XYZ)" → "Acme Corp"
    # "Acme Inc. (US)" → "Acme Inc."
    name = re.sub(r'\s*\([^)]*\)', '', name)  # Remove all parentheticals
    
    # === STEP 2: Handle "DBA" / "d/b/a" / "trading as" ===
    # Keep the part BEFORE dba (the legal name)
    dba_match = re.split(r'\s+(?:d\.?b\.?a\.?|d/b/a|trading\s+as|t/a)\s+', name, flags=re.IGNORECASE)
    if len(dba_match) > 1:
        name = dba_match[0].strip()
    
    # === STEP 3: Take first part before comma (but be smart about it) ===
    # "Acme, Inc." → "Acme"
    # But "Smith, Johnson & Associates" should stay together
    if ',' in name:
        parts = name.split(',')
        # If second part looks like a suffix, just take first part
        if len(parts) >= 2:
            second = parts[1].strip().lower()
            suffix_pattern = '|'.join(LEGAL_SUFFIXES)
            if re.match(rf'^({suffix_pattern})\.?\s*$', second, re.IGNORECASE):
                name = parts[0].strip()
    
    # === STEP 4: Remove legal suffixes ===
    suffix_pattern = r'\b(?:' + '|'.join(LEGAL_SUFFIXES) + r')\.?\b'
    # Also handle "and company", "& co", etc.
    name = re.sub(rf'\s*(?:and|&)?\s*{suffix_pattern}', '', name, flags=re.IGNORECASE)
    
    # === STEP 5: Remove "The" from beginning ===
    name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
    
    # === STEP 6: Clean special characters ===
    # Keep: letters (including accented), numbers, spaces, &, -, ', .
    # This preserves: "AT&T", "Johnson & Johnson", "Ben & Jerry's"
    name = re.sub(r'[^\w\s&\-\'.·]', ' ', name, flags=re.UNICODE)
    
    # === STEP 7: Remove trailing junk ===
    # Remove trailing &, -, commas, periods
    name = re.sub(r'[\s&\-,\.]+$', '', name)
    
    # === STEP 8: Normalize whitespace ===
    name = re.sub(r'\s+', ' ', name).strip()
    
    if not name:
        return ""
    
    # === STEP 9: Clean up any remaining dots at end ===
    name = re.sub(r'\.+$', '', name).strip()
    
    # === STEP 10: Smart Title Case ===
    # Handle ALL CAPS → Title Case
    # But preserve intentional caps like "BMW", "IBM", "AT&T"
    def smart_title_case(text):
        words = text.split()
        result = []
        
        # Check if entire text is ALL CAPS
        all_caps_input = text.isupper()
        
        # Words that should stay lowercase (unless first word)
        lowercase_words = {'and', 'or', 'the', 'a', 'an', 'of', 'for', 'to', 'in', 'on', 'at', 'by'}
        
        # Known acronyms that should stay uppercase
        known_acronyms = {'IBM', 'BMW', 'SAP', 'AWS', 'USA', 'UK', 'AI', 'IT', 'HR', 'CEO', 'CFO', 'CTO', 'VP', '3M'}
        
        for i, word in enumerate(words):
            upper_word = word.upper()
            
            # If it's a known acronym, keep it uppercase
            if upper_word in known_acronyms:
                result.append(upper_word)
            # Handle & in words like AT&T, H&M
            elif '&' in word and len(word) <= 5:
                result.append(word.upper())
            # If original input was ALL CAPS, convert to title case
            elif all_caps_input:
                if word.lower() in lowercase_words and i > 0:
                    result.append(word.lower())
                else:
                    result.append(word.capitalize())
            # Mixed case - preserve it (e.g., McDonald's)
            elif not word.isupper() and not word.islower():
                result.append(word)
            # ALL CAPS single word in otherwise mixed text - might be acronym
            elif word.isupper() and len(word) <= 4:
                result.append(word)
            # ALL CAPS longer word - title case it
            elif word.isupper():
                result.append(word.capitalize())
            else:
                result.append(word.capitalize() if word.islower() else word)
        
        return ' '.join(result)
    
    name = smart_title_case(name)
    
    return name


# === TESTS ===
if __name__ == "__main__":
    test_cases = [
        # Basic suffix removal
        ("Acme Inc.", "Acme"),
        ("Acme, Inc.", "Acme"),
        ("Acme Corporation", "Acme"),
        ("Acme Corp", "Acme"),
        ("Acme LLC", "Acme"),
        ("Acme Ltd.", "Acme"),
        ("Acme Limited", "Acme"),
        ("Acme Holdings", "Acme"),
        ("Acme Group", "Acme"),
        
        # International suffixes
        ("Acme GmbH", "Acme"),
        ("Acme S.A.", "Acme"),
        ("Acme B.V.", "Acme"),
        ("Acme Pte. Ltd.", "Acme"),
        ("Acme Pty Ltd", "Acme"),
        ("Acme Pvt. Ltd.", "Acme"),
        ("Acme AB", "Acme"),
        ("Acme K.K.", "Acme"),
        
        # ALL CAPS
        ("ACME CORPORATION", "Acme"),
        ("JOHNSON & JOHNSON", "Johnson & Johnson"),
        
        # The prefix
        ("The Coca-Cola Company", "Coca-Cola"),
        ("The Home Depot", "Home Depot"),
        
        # Preserve acronyms
        ("IBM Corporation", "IBM"),
        ("AT&T Inc.", "AT&T"),
        ("BMW AG", "BMW"),
        ("3M Company", "3M"),
        
        # Parenthetical notes
        ("Acme Corp (formerly XYZ)", "Acme"),
        ("Acme Inc. (US)", "Acme"),
        
        # DBA handling
        ("Legal Name LLC DBA Cool Brand", "Legal Name"),
        ("Acme Corp d/b/a Widget Co", "Acme"),
        
        # Preserve ampersand
        ("Johnson & Johnson", "Johnson & Johnson"),
        ("Ben & Jerry's", "Ben & Jerry's"),
        ("Ernst & Young", "Ernst & Young"),
        
        # Edge cases
        ("Acme", "Acme"),
        ("Acme, LLC.", "Acme"),
        ("Acme and Company", "Acme"),
        ("Acme & Co.", "Acme"),
        ("", ""),
        (None, ""),
        
        # Complex cases
        ("THE BOEING COMPANY", "Boeing"),
        ("McDonald's Corporation", "McDonald's"),
    ]
    
    print("Testing clean_company_name():\n")
    passed = 0
    failed = []
    for raw, expected in test_cases:
        result = clean_company_name(raw)
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
