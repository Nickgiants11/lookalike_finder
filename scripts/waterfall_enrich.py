#!/usr/bin/env python3
"""
BuzzLead Email Waterfall Enrichment

Waterfall sequence:
1. Million Verifier (validate existing)
2. TryKit (find email)
3. LeadMagic (find email)
4. Icypeas (find email)
5. Million Verifier (validate found)
6. TryKit Validation (risky check)
7. BounceBan (final validation)
8. ESP Lookup (identify provider)

Usage:
    python waterfall_enrich.py input.csv -o output.csv
    python waterfall_enrich.py input.csv --secrets ~/.clawdbot/secrets/buzzlead-api-keys.env
"""

import os
import sys
import csv
import time
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

# Add tools directory to path for cleaners
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from clean_first_name import clean_first_name
from clean_company_name import clean_company_name


def load_env_file(path: str) -> Dict[str, str]:
    """Load environment variables from a file."""
    keys = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                keys[k] = v.strip().strip('"').strip("'")
    return keys


@dataclass
class EnrichmentResult:
    """Result of email enrichment for a single contact."""
    full_name: str
    first_name_clean: str
    domain: str
    company_name_clean: str
    original_email: Optional[str] = None
    found_email: Optional[str] = None
    valid_email: Optional[str] = None
    email_source: Optional[str] = None
    quality: Optional[str] = None
    validity: Optional[str] = None
    esp_host: Optional[str] = None
    error: Optional[str] = None


class WaterfallEnricher:
    """Email waterfall enrichment with cascading providers."""
    
    def __init__(self, keys: Dict[str, str]):
        self.millionverifier_key = keys.get("MILLIONVERIFIER_API_KEY", "").strip()
        self.trykit_key = keys.get("TRYKIT_API_KEY", "").strip()
        self.leadmagic_key = keys.get("LEADMAGIC_API_KEY", "").strip()
        self.icypeas_key = keys.get("ICYPEAS_API_KEY", "").strip()
        self.bounceban_key = keys.get("BOUNCEBAN_API_KEY", "").strip()
        self.emailguard_key = keys.get("EMAILGUARD_API_KEY", "").strip()
        
        # Validate required keys
        missing = []
        if not self.trykit_key: missing.append("TRYKIT_API_KEY")
        if not self.leadmagic_key: missing.append("LEADMAGIC_API_KEY")
        if not self.millionverifier_key: missing.append("MILLIONVERIFIER_API_KEY")
        
        if missing:
            print(f"⚠️  Warning: Missing API keys: {', '.join(missing)}")
    
    def _safe_request(self, method: str, url: str, timeout: int = 20, **kwargs) -> Optional[Dict]:
        """Make API request with error handling."""
        try:
            response = requests.request(method, url, timeout=timeout, allow_redirects=True, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"    API error: {e}")
            return None
    
    # ========== EMAIL FINDERS ==========
    
    def find_email_trykit(self, full_name: str, domain: str) -> Optional[str]:
        """TryKit email finder."""
        print(f"  → TryKit: Finding email...")
        result = self._safe_request(
            "POST", "https://api.trykitt.ai/job/find_email",
            params={"src": "BuzzLead"},
            json={"fullName": full_name, "domain": domain, "realtime": True},
            headers={"x-api-key": self.trykit_key}
        )
        if result and result.get("email"):
            print(f"    ✓ Found: {result['email']}")
            return result["email"]
        return None
    
    def find_email_leadmagic(self, full_name: str, domain: str) -> Optional[str]:
        """LeadMagic email finder."""
        print(f"  → LeadMagic: Finding email...")
        result = self._safe_request(
            "POST", "https://api.leadmagic.io/business-email",
            json={"name": full_name, "domain": domain},
            headers={"X-API-Key": self.leadmagic_key}
        )
        if result and result.get("email"):
            print(f"    ✓ Found: {result['email']}")
            return result["email"]
        return None
    
    def find_email_icypeas(self, full_name: str, domain: str) -> Optional[str]:
        """Icypeas email finder."""
        if not self.icypeas_key:
            return None
        print(f"  → Icypeas: Finding email...")
        result = self._safe_request(
            "POST", "https://app.icypeas.com/api/email-search",
            json={"full_name": full_name, "domain_name": domain},
            headers={"Authorization": f"Bearer {self.icypeas_key}", "Content-Type": "application/json"}
        )
        if result and result.get("email"):
            print(f"    ✓ Found: {result['email']}")
            return result["email"]
        return None
    
    # ========== VALIDATORS ==========
    
    def validate_millionverifier(self, email: str) -> Optional[str]:
        """Million Verifier quality check."""
        print(f"  → Million Verifier: Validating...")
        result = self._safe_request(
            "GET", "https://api.millionverifier.com/api/v3/",
            params={"api": self.millionverifier_key, "email": email, "timeout": "10"}
        )
        if result:
            quality = result.get("quality", "unknown")
            print(f"    Quality: {quality}")
            return quality
        return None
    
    def validate_trykit(self, email: str) -> Optional[str]:
        """TryKit validation for risky emails."""
        print(f"  → TryKit Validation: Re-checking...")
        result = self._safe_request(
            "POST", "https://api.trykitt.ai/job/verify_email",
            params={"src": "BuzzLead"},
            json={"email": email, "realtime": True},
            headers={"x-api-key": self.trykit_key}
        )
        if result:
            validity = result.get("validity", "unknown")
            print(f"    Validity: {validity}")
            return validity
        return None
    
    def validate_bounceban(self, email: str) -> Optional[str]:
        """BounceBan final validation."""
        if not self.bounceban_key:
            return None
        print(f"  → BounceBan: Final check...")
        result = self._safe_request(
            "GET", "https://api.bounceban.com/v1/verify/single",
            params={"email": email},
            headers={"Authorization": self.bounceban_key}
        )
        if result:
            status = result.get("result", "unknown")
            print(f"    Result: {status}")
            return status
        return None
    
    def lookup_esp(self, email: str) -> Optional[str]:
        """ESP Lookup to identify email provider."""
        if not self.emailguard_key:
            return None
        print(f"  → ESP Lookup: Identifying provider...")
        auth_header = self.emailguard_key
        if not auth_header.startswith("Bearer "):
            auth_header = f"Bearer {auth_header}"
        result = self._safe_request(
            "POST", "https://app.emailguard.io/api/v1/email-host-lookup",
            json={"email": email},
            headers={"Authorization": auth_header}
        )
        if result and result.get("data"):
            host = result["data"].get("email_host", "unknown")
            print(f"    ESP: {host}")
            return host
        return None
    
    # ========== MAIN WATERFALL ==========
    
    def enrich_contact(self, full_name: str, domain: str, company_name: str = "", 
                       existing_email: Optional[str] = None) -> EnrichmentResult:
        """Run full waterfall enrichment for a single contact."""
        
        # Clean names
        first_name_clean = clean_first_name(full_name.split()[0] if full_name else "")
        company_name_clean = clean_company_name(company_name) if company_name else ""
        
        result = EnrichmentResult(
            full_name=full_name,
            first_name_clean=first_name_clean,
            domain=domain,
            company_name_clean=company_name_clean,
            original_email=existing_email or None
        )
        
        print(f"\n{'='*50}")
        print(f"Processing: {full_name} @ {domain}")
        print(f"{'='*50}")
        
        email = existing_email if existing_email else None
        quality = None
        
        # Step 1: Validate existing email (if provided)
        if email:
            quality = self.validate_millionverifier(email)
            result.quality = quality
            if quality == "good":
                result.valid_email = email.lower()
                result.email_source = "original"
                print(f"  ✓ Original email is good!")
            elif quality == "bad":
                print(f"  ✗ Original email is bad, searching...")
                email = None
        
        # Step 2-4: Waterfall email finding
        if not email or quality == "bad":
            email = self.find_email_trykit(full_name, domain)
            if email:
                result.found_email = email
                result.email_source = "trykit"
            
            if not email:
                email = self.find_email_leadmagic(full_name, domain)
                if email:
                    result.found_email = email
                    result.email_source = "leadmagic"
            
            if not email:
                email = self.find_email_icypeas(full_name, domain)
                if email:
                    result.found_email = email
                    result.email_source = "icypeas"
        
        if not email:
            print(f"  ✗ No email found for {full_name}")
            return result
        
        # Step 5: Validate waterfall-found email
        if result.email_source and result.email_source != "original":
            quality = self.validate_millionverifier(email)
            result.quality = quality
            if quality == "good":
                result.valid_email = email.lower()
                print(f"  ✓ Found email is good!")
        
        # Step 6-7: Handle risky emails
        if quality == "risky":
            print(f"  ⚠ Email is risky, running additional validation...")
            validity = self.validate_trykit(email)
            result.validity = validity
            if validity in ["valid", "valid-risky"]:
                result.valid_email = email.lower()
                print(f"  ✓ TryKit confirms email is usable!")
            elif validity in ["invalid", "unknown"]:
                bounceban_result = self.validate_bounceban(email)
                if bounceban_result == "deliverable":
                    result.valid_email = email.lower()
                    print(f"  ✓ BounceBan confirms email is deliverable!")
                else:
                    print(f"  ✗ Email failed validation")
        
        # Step 8: ESP Lookup
        if result.valid_email:
            esp = self.lookup_esp(result.valid_email)
            result.esp_host = esp
            print(f"\n  ★ VALID EMAIL: {result.valid_email} (source: {result.email_source}, esp: {result.esp_host})")
        else:
            print(f"\n  ✗ NO VALID EMAIL FOUND")
        
        return result


def enrich_csv(input_file: str, output_file: str, secrets_file: str, delay: float = 0.5):
    """Enrich contacts from CSV file."""
    
    # Load API keys
    keys = load_env_file(secrets_file)
    enricher = WaterfallEnricher(keys)
    
    # Read input CSV
    contacts = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        contacts = list(reader)
    
    print(f"\n📂 Loaded {len(contacts)} contacts from {input_file}")
    
    # Detect column names
    name_col = next((c for c in fieldnames if c.lower() in ['full name', 'full_name', 'name', 'fullname']), None)
    domain_col = next((c for c in fieldnames if c.lower() in ['domain', 'company website', 'website', 'company_domain']), None)
    company_col = next((c for c in fieldnames if c.lower() in ['company', 'company name', 'company_name', 'org', 'organization']), None)
    email_col = next((c for c in fieldnames if c.lower() in ['email', 'email business', 'email_business', 'work_email']), None)
    first_name_col = next((c for c in fieldnames if c.lower() in ['first name', 'first_name', 'firstname']), None)
    
    print(f"   Detected columns: name={name_col}, domain={domain_col}, company={company_col}, email={email_col}")
    
    # Enrich contacts
    results = []
    for i, contact in enumerate(contacts, 1):
        print(f"\n[{i}/{len(contacts)}]")
        
        full_name = contact.get(name_col, "") if name_col else ""
        
        # Get domain, clean it
        domain = contact.get(domain_col, "") if domain_col else ""
        domain = domain.replace('http://', '').replace('https://', '').rstrip('/')
        
        company = contact.get(company_col, "") if company_col else ""
        existing_email = contact.get(email_col, "") if email_col else ""
        
        # If we have first name col, use that for cleaning
        if first_name_col and contact.get(first_name_col):
            first_name_raw = contact.get(first_name_col, "")
        else:
            first_name_raw = full_name.split()[0] if full_name else ""
        
        result = enricher.enrich_contact(
            full_name=full_name,
            domain=domain,
            company_name=company,
            existing_email=existing_email
        )
        
        # Override first_name_clean if we have the raw first name
        result.first_name_clean = clean_first_name(first_name_raw)
        
        # Merge original data with enrichment results
        enriched_row = dict(contact)
        enriched_row['First Name'] = result.first_name_clean
        enriched_row['Company Name Clean'] = result.company_name_clean
        enriched_row['Valid Email'] = result.valid_email or ""
        enriched_row['Email Host'] = result.esp_host or ""
        enriched_row['Email Source'] = result.email_source or ""
        enriched_row['Email Quality'] = result.quality or ""
        
        results.append(enriched_row)
        
        if i < len(contacts):
            time.sleep(delay)
    
    # Determine output columns
    output_fieldnames = list(fieldnames) if fieldnames else []
    for col in ['First Name', 'Company Name Clean', 'Valid Email', 'Email Host', 'Email Source', 'Email Quality']:
        if col not in output_fieldnames:
            output_fieldnames.append(col)
    
    # Write output CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    valid_count = sum(1 for r in results if r.get('Valid Email'))
    print(f"\n{'='*50}")
    print(f"📊 SUMMARY")
    print(f"{'='*50}")
    print(f"Total contacts: {len(results)}")
    print(f"Valid emails found: {valid_count}")
    print(f"Success rate: {valid_count/len(results)*100:.1f}%")
    print(f"Output saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="BuzzLead Email Waterfall Enrichment")
    parser.add_argument("input", help="Input CSV file with contacts")
    parser.add_argument("-o", "--output", help="Output CSV file (default: input_enriched.csv)")
    parser.add_argument("-d", "--delay", type=float, default=0.5, help="Delay between contacts in seconds")
    parser.add_argument("-s", "--secrets", default="~/.clawdbot/secrets/buzzlead-api-keys.env",
                        help="Path to secrets/env file with API keys")
    
    args = parser.parse_args()
    
    output = args.output or args.input.replace(".csv", "_waterfall.csv")
    secrets = os.path.expanduser(args.secrets)
    
    if not os.path.exists(secrets):
        print(f"❌ Secrets file not found: {secrets}")
        print(f"   Create it with your API keys:")
        print(f"   TRYKIT_API_KEY=xxx")
        print(f"   LEADMAGIC_API_KEY=xxx")
        print(f"   MILLIONVERIFIER_API_KEY=xxx")
        sys.exit(1)
    
    enrich_csv(args.input, output, secrets, delay=args.delay)


if __name__ == "__main__":
    main()
