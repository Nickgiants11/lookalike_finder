#!/usr/bin/env python3
"""
Contact Enrichment Script
Takes CSV from /lookalike skill → enriches with decision-makers via AI Ark → outputs CSV for Clay

Usage:
    python enrich_contacts.py <input_csv> [--output <output_csv>] [--limit <N>]

Example:
    python enrich_contacts.py exports/foreverfierce/2026-02-04_v1.csv --output enriched.csv
"""

import requests
import csv
import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from time import sleep

# =============================================================================
# CONFIGURATION
# =============================================================================

AIARK_API_KEY = os.environ.get("AIARK_API_KEY", "")
AIARK_BASE_URL = "https://api.ai-ark.com/api/developer-portal/v1"

# Rate limits: 5/sec, 300/min, 18000/hour
RATE_LIMIT_DELAY = 0.25  # 4 requests/sec to be safe

# Target decision-maker profiles
TARGET_SENIORITIES = ["C-Level", "VP", "Director", "Owner", "Founder", "Partner"]
TARGET_DEPARTMENTS = ["Executive", "Sales", "Business Development", "Marketing", "Management", "Operations"]

# Max contacts per company
MAX_CONTACTS_PER_COMPANY = 5


# =============================================================================
# AI ARK API
# Reference: https://docs.ai-ark.com/reference/people-search-1
# =============================================================================

def aiark_headers() -> Dict[str, str]:
    """Get headers for AI Ark API requests."""
    return {
        "Content-Type": "application/json",
        "x-api-key": AIARK_API_KEY,
    }


def search_people_at_company(
    domain: str,
    seniorities: List[str] = None,
    departments: List[str] = None,
    page_size: int = 10
) -> List[Dict]:
    """
    Search for people at a company using AI Ark People Search API.

    API Endpoint: POST https://api.ai-ark.com/api/developer-portal/v1/people

    Rate Limits:
        - 5 requests/second
        - 300 requests/minute
        - 18,000 requests/hour

    Args:
        domain: Company domain (e.g., "acme.com")
        seniorities: List of seniority levels to filter by
        departments: List of departments to filter by
        page_size: Number of results per page (max 100)

    Returns:
        List of person dictionaries with contact info
    """
    endpoint = f"{AIARK_BASE_URL}/people"

    # Build request payload
    # See: https://docs.ai-ark.com/reference/people-search-1
    payload = {
        "page": 0,
        "size": min(page_size, 100),
        "account_filter": {
            "domain": {
                "include": [domain]
            }
        }
    }

    # Add contact filters if specified
    contact_filter = {}

    if seniorities:
        contact_filter["seniority"] = {
            "include": seniorities
        }

    if departments:
        contact_filter["department"] = {
            "include": departments
        }

    if contact_filter:
        payload["contact_filter"] = contact_filter

    try:
        response = requests.post(
            endpoint,
            headers=aiark_headers(),
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            # Response structure: { content: [...], pageable: {...}, totalElements: N }
            return data.get("content", data.get("results", data.get("people", [])))
        elif response.status_code == 401:
            print(f"  ⚠️  AI Ark auth failed - check AIARK_API_KEY")
        elif response.status_code == 429:
            print(f"  ⚠️  Rate limited - waiting...")
            sleep(5)
            return search_people_at_company(domain, seniorities, departments, page_size)
        else:
            # Silent fail for individual lookups
            pass

    except requests.exceptions.Timeout:
        print(f"  ⚠️  Timeout for {domain}")
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:50]}")

    return []


def enrich_person_email(person_id: str) -> Optional[str]:
    """
    Get verified email for a person (if available in your plan).

    Note: This may require additional API credits depending on your plan.
    """
    # Implement if needed based on your AI Ark plan
    pass


# =============================================================================
# DATA EXTRACTION
# =============================================================================

def extract_person(person: Dict) -> Dict:
    """
    Extract and normalize person data from AI Ark response.

    AI Ark returns profiles with varying field names depending on data source.
    This normalizes them to a consistent format.
    """
    # Handle different name formats
    full_name = person.get("name", person.get("full_name", ""))
    first_name = person.get("first_name", person.get("firstName", ""))
    last_name = person.get("last_name", person.get("lastName", ""))

    # Parse full name if first/last not provided
    if full_name and not first_name:
        parts = full_name.split(" ", 1)
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""

    # Get LinkedIn URL (various field names)
    linkedin = (
        person.get("linkedin_url") or
        person.get("linkedinUrl") or
        person.get("linkedin") or
        person.get("profile_url") or
        ""
    )

    # Get email (may be in different locations)
    email = (
        person.get("email") or
        person.get("work_email") or
        person.get("workEmail") or
        person.get("personal_email") or
        ""
    )

    # Get phone
    phone = (
        person.get("phone") or
        person.get("mobile") or
        person.get("direct_phone") or
        ""
    )

    # Get title/job info
    title = (
        person.get("title") or
        person.get("job_title") or
        person.get("jobTitle") or
        person.get("current_title") or
        ""
    )

    seniority = person.get("seniority", person.get("level", ""))
    department = person.get("department", person.get("function", ""))

    return {
        "first_name": first_name,
        "last_name": last_name,
        "title": title,
        "seniority": seniority,
        "department": department,
        "email": email,
        "phone": phone,
        "linkedin_url": linkedin,
    }


# =============================================================================
# CSV PROCESSING
# =============================================================================

def read_lookalike_csv(filepath: str) -> List[Dict]:
    """
    Read CSV exported from /lookalike skill.

    Expected columns: domain, name, similarity, employees, score, city, state, ...
    """
    companies = []

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize column names (handle variations)
            domain = (
                row.get('domain') or
                row.get('company_domain') or
                row.get('website') or
                ""
            ).strip()

            if not domain:
                continue

            # Clean domain (remove protocol, www, trailing slash)
            domain = domain.lower()
            domain = domain.replace('https://', '').replace('http://', '')
            domain = domain.replace('www.', '')
            domain = domain.rstrip('/')

            companies.append({
                'domain': domain,
                'company_name': row.get('name', row.get('company_name', '')),
                'similarity': row.get('similarity', ''),
                'employees': row.get('employees', ''),
                'score': row.get('score', ''),
                'city': row.get('city', ''),
                'state': row.get('state', ''),
                'country': row.get('country', 'US'),
                'primary_industry': row.get('primary_industry', ''),
                'description': row.get('description', '')[:200] if row.get('description') else '',
            })

    return companies


def write_enriched_csv(filepath: str, rows: List[Dict]):
    """Write enriched data to CSV (Clay-compatible format)."""

    fieldnames = [
        # Company fields
        'company_name',
        'domain',
        'company_linkedin',
        'employees',
        'city',
        'state',
        'country',
        'primary_industry',
        'similarity',
        # Contact fields
        'first_name',
        'last_name',
        'title',
        'seniority',
        'department',
        'email',
        'phone',
        'linkedin_url',
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def enrich_companies(
    input_csv: str,
    output_csv: str = None,
    limit: int = None,
    skip_no_contacts: bool = False
) -> str:
    """
    Main enrichment workflow.

    Args:
        input_csv: Path to CSV from /lookalike skill
        output_csv: Output path (auto-generated if not provided)
        limit: Max companies to process (None = all)
        skip_no_contacts: If True, skip rows where no contacts found

    Returns:
        Path to output CSV
    """
    print("=" * 60)
    print("CONTACT ENRICHMENT")
    print("=" * 60)

    # Validate API key
    if not AIARK_API_KEY:
        print("❌ Error: AIARK_API_KEY environment variable not set")
        print("   export AIARK_API_KEY='your-api-key'")
        sys.exit(1)

    # Read input
    print(f"📂 Reading: {input_csv}")
    companies = read_lookalike_csv(input_csv)

    if not companies:
        print("❌ No companies found in CSV")
        return ""

    if limit:
        companies = companies[:limit]

    print(f"📊 Companies to enrich: {len(companies)}")
    print()

    # Process each company
    results = []
    companies_with_contacts = 0
    total_contacts = 0

    for i, company in enumerate(companies):
        domain = company['domain']

        # Progress indicator
        if (i + 1) % 10 == 0 or i == 0:
            print(f"🔍 Processing {i + 1}/{len(companies)}: {domain}")

        # Search for decision-makers
        people = search_people_at_company(
            domain=domain,
            seniorities=TARGET_SENIORITIES,
            departments=TARGET_DEPARTMENTS,
            page_size=MAX_CONTACTS_PER_COMPANY
        )

        if people:
            companies_with_contacts += 1
            for person in people[:MAX_CONTACTS_PER_COMPANY]:
                person_data = extract_person(person)
                total_contacts += 1
                results.append({
                    **company,
                    **person_data
                })
        elif not skip_no_contacts:
            # Include company row even without contacts
            results.append({
                **company,
                'first_name': '',
                'last_name': '',
                'title': '',
                'seniority': '',
                'department': '',
                'email': '',
                'phone': '',
                'linkedin_url': '',
            })

        # Rate limiting
        sleep(RATE_LIMIT_DELAY)

    # Generate output filename
    if not output_csv:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(input_csv))[0]
        output_csv = f"{base_name}_enriched_{timestamp}.csv"

    # Write output
    write_enriched_csv(output_csv, results)

    # Summary
    print()
    print("=" * 60)
    print("✅ ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"   Companies processed: {len(companies)}")
    print(f"   Companies with contacts: {companies_with_contacts}")
    print(f"   Total contacts found: {total_contacts}")
    print(f"   Output rows: {len(results)}")
    print(f"   Output file: {output_csv}")
    print("=" * 60)

    return output_csv


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Enrich lookalike CSV with decision-maker contacts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python enrich_contacts.py exports/foreverfierce/2026-02-04_v1.csv
    python enrich_contacts.py input.csv --output enriched.csv --limit 50
    python enrich_contacts.py input.csv --skip-no-contacts

Environment Variables:
    AIARK_API_KEY    Your AI Ark API key (required)
        """
    )

    parser.add_argument('input_csv', help='Input CSV file from /lookalike skill')
    parser.add_argument('--output', '-o', help='Output CSV file path')
    parser.add_argument('--limit', '-l', type=int, help='Max companies to process')
    parser.add_argument('--skip-no-contacts', action='store_true',
                        help='Skip companies where no contacts found')

    args = parser.parse_args()

    if not os.path.exists(args.input_csv):
        print(f"❌ File not found: {args.input_csv}")
        sys.exit(1)

    enrich_companies(
        input_csv=args.input_csv,
        output_csv=args.output,
        limit=args.limit,
        skip_no_contacts=args.skip_no_contacts
    )


if __name__ == "__main__":
    main()
