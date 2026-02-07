---
name: enrich
description: Enrich a CSV of companies with decision-maker contacts using AI Ark, then run email waterfall enrichment + data cleaning
---

# Contact Enrichment Skill

You are running an interactive contact enrichment workflow. This takes a CSV from the `/lookalike` skill and enriches it with decision-maker contacts using AI Ark.

## STEP 1: GET INPUT CSV

If the user provided a CSV path as an argument, use it. Otherwise ask:
"What CSV file would you like to enrich with contacts?"

Suggest recent exports:
- Check `exports/` folder for recent lookalike CSVs
- Show the most recent 3-5 files with company counts

## STEP 2: VALIDATE INPUT

Read the CSV and validate:
1. Check the file exists
2. Count total rows
3. Verify it has a `domain` column (or `company_domain`, `website`)

Show the user:
- File name
- Total companies
- Sample of first 3 domains

## STEP 3: ASK FOR INITIAL PREFERENCES

Use AskUserQuestion to ask:

1. "What types of decision-makers are you looking for?"
   - Options:
     - C-Suite & Founders (C-Level, Owner, Founder, Partner)
     - Sales & BD Leaders (VP Sales, Director BD, Sales Manager)
     - Marketing Leaders (CMO, VP Marketing, Director Marketing)
     - All Decision-Makers (default - C-Level, VP, Director, Owner, Founder)
     - Custom (let me specify)

2. "How many contacts per company?"
   - Options: 1, 3, 5, 10
   - Default: 3

## STEP 4: RUN SAMPLE ENRICHMENT

**Before processing all companies, run a sample of 5-10 to preview results.**

Say: "Running sample enrichment on first 10 companies to preview results..."

For each of the first 10 companies, call AI Ark People Search API:

**Endpoint:** `POST https://api.ai-ark.com/api/developer-portal/v1/people`

**Headers:**
```
Content-Type: application/json
X-TOKEN: <AIARK_API_KEY from environment>
```

**Request Body:**
```json
{
  "page": 0,
  "size": <contacts_per_company>,
  "account": {
    "domain": {
      "any": {
        "include": ["<company_domain>"]
      }
    }
  },
  "contact": {
    "seniority": {
      "any": {
        "include": ["C-Level", "VP", "Director", "Owner", "Founder"]
      }
    },
    "department": {
      "any": {
        "include": ["Executive", "Sales", "Marketing", "Business Development", "Management"]
      }
    }
  }
}
```

**Rate Limits:** 5 requests/second, 300/minute - add 0.25s delay between calls

## STEP 5: SHOW SAMPLE RESULTS

Display sample enrichment summary:

| Metric | Value |
|--------|-------|
| Companies sampled | 10 |
| Companies with contacts | X |
| Contact rate | X% |
| Total contacts found | X |
| Avg contacts per company | X.X |

**Top Titles Found:**
| Title | Count |
|-------|-------|
| VP of Sales | 5 |
| CEO | 4 |
| Director of Marketing | 3 |

**Sample Contacts:**
| Company | Name | Title | Email |
|---------|------|-------|-------|
| Acme Corp | John Smith | VP Sales | john@acme.com |
| Beta Inc | Jane Doe | CEO | jane@beta.com |
| ... | ... | ... | ... |

## STEP 6: REFINEMENT LOOP

**This step repeats until the user chooses to proceed or cancel.** After every adjustment, re-run the sample and return to this prompt.

Track and display the iteration number each time (Iteration 1, Iteration 2, etc.).

Ask: "Based on these sample results, what would you like to do?"

Options:
1. **Proceed with all companies** - Run enrichment on remaining companies with current settings → go to Step 7
2. **Adjust seniority filter** - Change which seniority levels to include
3. **Adjust department filter** - Change which departments to include
4. **Change contacts per company** - Get more or fewer contacts per company
5. **Filter companies first** - Only enrich companies with similarity > X or other criteria
6. **Change sample size** - Re-run sample on more/fewer companies
7. **Cancel** - Stop enrichment

### If ADJUST SENIORITY FILTER:

Show available options (let user multi-select):

**Seniority Levels:**
- C-Level (CEO, CFO, CTO, COO, CMO, etc.)
- VP (Vice President)
- Director
- Manager
- Owner
- Founder
- Partner

Apply new filter, re-run sample, show updated results, then **return to this step**.

### If ADJUST DEPARTMENT FILTER:

Show available options (let user multi-select):

**Departments:**
- Executive
- Sales
- Marketing
- Business Development
- Operations
- Finance
- Engineering/IT
- HR

Apply new filter, re-run sample, show updated results, then **return to this step**.

### If CHANGE CONTACTS PER COMPANY:

Ask: "How many contacts per company?"
- 1 (just the top match)
- 3 (small team)
- 5 (key decision-makers)
- 10 (broad coverage)
- Custom number

Re-run sample, show updated results, then **return to this step**.

### If FILTER COMPANIES:

Ask: "What's the minimum similarity score to include?"
- Default from lookalike is usually 70+
- Filter the input CSV before enrichment

Re-run sample with filtered company list, show updated results, then **return to this step**.

### If CHANGE SAMPLE SIZE:

Ask: "How many companies to sample?"
- 5 (quick preview)
- 10 (default)
- 20 (broader preview)

Re-run sample with new size, show updated results, then **return to this step**.

## STEP 7: RUN FULL ENRICHMENT

Once user confirms, process remaining companies:

Show progress:
```
🔍 Enriching companies...
[████████░░░░░░░░░░░░] 40/100 (40%)
Companies with contacts: 32
Total contacts: 87
```

Update every 10 companies or 30 seconds.

## STEP 8: SHOW FINAL RESULTS

Display:
- Total companies processed
- Companies with contacts found (and %)
- Total contacts found
- Average contacts per company
- Output file location

**Results Summary:**
| Metric | Value |
|--------|-------|
| Companies processed | 50 |
| Companies with contacts | 42 (84%) |
| Total contacts | 156 |
| Avg per company | 3.1 |

**Contact Breakdown by Seniority:**
| Seniority | Count | % |
|-----------|-------|---|
| C-Level | 28 | 18% |
| VP | 45 | 29% |
| Director | 52 | 33% |
| Manager | 31 | 20% |

**Contact Breakdown by Department:**
| Department | Count | % |
|------------|-------|---|
| Sales | 48 | 31% |
| Executive | 35 | 22% |
| Marketing | 42 | 27% |
| Business Dev | 31 | 20% |

## STEP 9: POST-ENRICHMENT OPTIONS

Ask: "What would you like to do with the results?"

Options:
1. **Export as-is** - Save the full enriched CSV
2. **Filter to email-only** - Remove contacts without email
3. **Filter to phone-only** - Remove contacts without phone
4. **Dedupe by person** - Remove duplicate people across companies
5. **View sample** - Show 10 random enriched rows
6. **Done** - End session

### If EXPORT:
Save to: `exports/[client]/[original_name]_enriched_[timestamp].csv`

### If FILTER:
Apply filter and show new counts, then export.

## OUTPUT FORMAT (PHASE 1 INTERMEDIATE)

Phase 1 intermediate CSV (AI Ark enrichment only, used as input to Phase 2):
```
company_name,domain,company_linkedin,employees,city,state,country,similarity,
first_name,last_name,title,seniority,department,email,phone,linkedin_url
```

The final output format is defined in Phase 2, Step 13.

## KEY BEHAVIORS

1. **Always sample first** - Never process all companies without showing preview
2. **Show contact rate** - Help user understand data quality
3. **Iterate before committing** - Let user refine before full run
4. **Handle rate limits** - Auto-retry with backoff on 429
5. **Save progress** - If interrupted, save what's done
6. **Show breakdowns** - Seniority and department stats help user understand results

## ERROR HANDLING

- **401 Unauthorized**:
  ```
  ❌ AI Ark authentication failed.
  Set your API key: export AIARK_API_KEY='your-key'
  Get a key at: https://ai-ark.com/
  ```

- **429 Rate Limited**: Wait 5 seconds and retry automatically

- **Timeout**: Skip company, log it, continue with next

- **No contacts found**: Keep company row with empty contact fields (don't lose company data)

## EXAMPLE SESSION

```
User: /enrich exports/foreverfierce/2026-02-04_v1.csv

Claude: 📂 Reading: exports/foreverfierce/2026-02-04_v1.csv
        Found 50 companies

        What types of decision-makers are you looking for?
        > All Decision-Makers

        How many contacts per company?
        > 3

        🔍 Running sample on first 10 companies...

        Sample Results:
        - Companies with contacts: 8/10 (80%)
        - Total contacts found: 22
        - Top titles: VP Sales (5), CEO (4), Director Marketing (3)

        Based on these results, what would you like to do?
        > Proceed with all companies

        🔍 Enriching remaining 40 companies...
        [████████████████████] 50/50 (100%)

        ✅ Enrichment Complete!
        - Companies: 50
        - With contacts: 42 (84%)
        - Total contacts: 126
        - Saved to: exports/foreverfierce/2026-02-04_v1_enriched_20260204_120000.csv
```

---

# PHASE 2: EMAIL WATERFALL ENRICHMENT + DATA CLEANING

After completing the AI Ark enrichment (Steps 1-9), automatically proceed to the email waterfall and data cleaning pipeline. This phase takes the enriched contacts and:
1. Runs the email waterfall on ALL contacts (not just those with existing emails)
2. Cleans first names and company names
3. Outputs a final CSV containing ONLY contacts with valid emails

---

## STEP 10: TRANSITION TO WATERFALL

After the user finishes Step 9 (post-enrichment options), ask:

"Ready to run the email waterfall enrichment + data cleaning pipeline?"

Options:
1. **Yes, run full pipeline** - Waterfall email finding/validation + name cleaning
2. **Skip waterfall, just clean names** - Only run data cleaning, no email enrichment
3. **Skip everything** - Keep the AI Ark export as-is

If user chooses option 1 or 2, proceed to the relevant steps.

---

## STEP 11: EMAIL WATERFALL ENRICHMENT

**Process ALL contact rows** (every row where first_name is not empty), regardless of whether they already have an email or not.

**Load API keys from .env file at:**
`/Users/nicholaskonstantinidis/Desktop/Buzzlead App Intelligence/lookalike-finder/.env`

### Waterfall Sequence

For each contact, determine which path to follow:

**PATH A — Contact HAS an existing email:**
1. Validate with Million Verifier (Sub-step 11a)
2. If good → ESP Lookup (Sub-step 11f) → done
3. If bad → go to PATH B (find a new email)
4. If risky → validate risky (Sub-step 11e)

**PATH B — Contact has NO email (or existing email was bad):**
Skip Million Verifier validation entirely. Go straight to email finders:
1. TryKit Finder (Sub-step 11b)
2. If not found → LeadMagic (Sub-step 11c)
3. If not found → Icypeas (Sub-step 11d)
4. If email found → validate it (Sub-step 11e)
5. If validated → ESP Lookup (Sub-step 11f)

Stop the finder sequence as soon as a work email is found, then proceed to validation.

#### Sub-step 11a: Validate Existing Email (PATH A only)

```
GET https://api.millionverifier.com/api/v3/?api=<MILLIONVERIFIER_API_KEY>&email=<email>&timeout=10
```

- Response field: `quality` → "good", "bad", or "risky"
- If quality = "good" → skip to Sub-step 11f (ESP Lookup). Done.
- If quality = "bad" → proceed to Sub-step 11b (find a new email via PATH B)
- If quality = "risky" → proceed to Sub-step 11e (re-validate risky)

#### Sub-step 11b: TryKit Email Finder

```
POST https://api.trykitt.ai/job/find_email?src=Clay
Headers: x-api-key: <TRYKIT_API_KEY>, Content-Type: application/json
Body: {"fullName": "<first_name> <last_name>", "domain": "<domain>", "realtime": true}
```

- If email found → proceed to Sub-step 11e (validate found email)
- If not found / error → proceed to Sub-step 11c

#### Sub-step 11c: LeadMagic Email Finder

```
POST https://api.leadmagic.io/business-email
Headers: X-API-Key: <LEADMAGIC_API_KEY>, Content-Type: application/json
Body: {"name": "<first_name> <last_name>", "domain": "<domain>"}
```

- If email found → proceed to Sub-step 11e (validate found email)
- If not found / error → proceed to Sub-step 11d

#### Sub-step 11d: Icypeas Email Finder

```
POST https://api.icypeas.com/single-search/email
Headers: Authorization: Bearer <ICYPEAS_API_KEY>, Content-Type: application/json
Body: {"full_name": "<first_name> <last_name>", "company_domain": "<domain>"}
```

- If email found → proceed to Sub-step 11e (validate found email)
- If not found → mark as no email found, skip to next contact

#### Sub-step 11e: Validate Found/Risky Email

**First: Million Verifier**
```
GET https://api.millionverifier.com/api/v3/?api=<MILLIONVERIFIER_API_KEY>&email=<email>&timeout=10
```

- If quality = "good" → proceed to Sub-step 11f (ESP Lookup)
- If quality = "bad" → discard email, mark as no valid email
- If quality = "risky" → continue to TryKit validation below

**Second: TryKit Email Validator (risky emails only)**
```
POST https://api.trykitt.ai/job/verify_email?src=Clay
Headers: x-api-key: <TRYKIT_API_KEY>, Content-Type: application/json
Body: {"email": "<email>", "realtime": true}
```

- If result = "valid" or "valid-risky" → proceed to Sub-step 11f (ESP Lookup)
- If result = "invalid" or "unknown" → continue to BounceBan below

**Third: BounceBan (final validation for risky)**
```
GET https://api.bounceban.com/v1/verify/single?email=<email>
Headers: Authorization: <BOUNCEBAN_API_KEY>
```

- If result = "deliverable" → proceed to Sub-step 11f (ESP Lookup)
- If result = "undeliverable" or "risky" → discard email

#### Sub-step 11f: ESP Lookup

```
POST https://app.emailguard.io/api/v1/email-host-lookup
Headers: Authorization: <EMAILGUARD_API_KEY>, Content-Type: application/json
Body: {"email": "<email>"}
```

- Extract the email host/provider (outlook, google, other, etc.)
- Store as `email_host` field

### Email Quality Assignment

Based on the waterfall results, assign a final quality:

| Scenario | Email Quality |
|----------|--------------|
| Million Verifier = "good" | good |
| Million Verifier = "risky" + TryKit = "valid" | good |
| Million Verifier = "risky" + TryKit = "valid-risky" | risky |
| Million Verifier = "risky" + BounceBan = "deliverable" | risky |
| All validators failed or "bad" | bad (discard email) |
| No email found by any finder | empty |

### Rate Limiting & Progress

- Add 0.2s delay between API calls
- On 429 responses, wait 5 seconds and retry (max 3 retries)
- On timeout, skip that sub-step and move to next provider
- Show progress every 5 contacts:

```
Email Waterfall Progress:
[████████░░░░░░░░░░░░] 8/15 contacts (53%)
Emails found: 5 | Validated: 4 | Failed: 1
```

### Waterfall Results Summary

After processing all contacts, display:

| Metric | Value |
|--------|-------|
| Contacts processed | X |
| Emails found | X (X%) |
| Email quality: good | X |
| Email quality: risky | X |
| No email found | X |

**Email Source Breakdown:**
| Source | Count |
|--------|-------|
| Original (validated) | X |
| TryKit | X |
| LeadMagic | X |
| Icypeas | X |

**ESP Breakdown:**
| Provider | Count |
|----------|-------|
| Outlook | X |
| Google | X |
| Other | X |

---

## STEP 12: DATA CLEANING

Apply cleaning to contact rows that will be included in the final export.

### 12a: First Name Cleaning

Apply these rules in order to the `first_name` field:

1. **Parenthetical preferred name:** `John (Johnny)` → `Johnny` — extract name inside parentheses
2. **Quoted preferred name:** `"Nick" John` → `Nick` — extract name inside quotes
3. **Remove emojis:** Strip all emoji characters
4. **Dr. prefix:** Preserve `Dr.` prefix if present
5. **ALL CAPS → Title Case:** `JOHN` → `John`
6. **Single-letter initials:** `J. Robert` → `Robert` — drop leading single-letter initial + period
7. **Hyphenated names:** `mary-jane` → `Mary-Jane` — capitalize each part
8. **Apostrophe names:** `o'connor` → `O'Connor` — capitalize after apostrophe
9. **Accented characters:** Preserve as-is (`José` stays `José`)
10. **Trim whitespace:** Remove leading/trailing spaces

### 12b: Company Name Cleaning

Apply these rules in order to the `company_name` field to produce `Company Name Clean`:

1. **Remove legal suffixes:** Strip these (case-insensitive, with optional preceding comma/space):
   `Inc`, `Inc.`, `Incorporated`, `LLC`, `L.L.C.`, `Corp`, `Corp.`, `Corporation`, `GmbH`, `Pte Ltd`, `Pte. Ltd.`, `Ltd`, `Ltd.`, `Limited`, `LLP`, `L.L.P.`, `LP`, `L.P.`, `Co`, `Co.`, `Company`, `AG`, `SA`, `S.A.`, `SL`, `S.L.`, `BV`, `B.V.`, `NV`, `N.V.`, `Pty`, `Pty.`, `Pty Ltd`, `AB`, `AS`, `OÜ`, `PLC`, `P.L.C.`
2. **DBA handling:** `Legal Name LLC DBA Cool Brand` → `Legal Name` — remove `DBA` and everything after
3. **Remove "The" prefix:** `The Home Depot` → `Home Depot` (only if more than 2 words after removal)
4. **ALL CAPS → Title Case:** `ACME CORPORATION` → `Acme` (after suffix removal)
5. **Preserve acronyms:** Keep these uppercase: `IBM`, `AT&T`, `BMW`, `3M`, `SAP`, `HP`, `GE`, and any all-caps word that is 2-4 characters
6. **Preserve ampersand:** `Johnson & Johnson` stays as-is
7. **Trim whitespace:** Remove leading/trailing spaces, collapse multiple spaces
8. **Clean dangling conjunctions:** If name ends with "and" (from "and Co" removal), strip it

### Cleaning Summary

After cleaning, display:

```
Data Cleaning Summary:
- First names cleaned: X of Y modified
- Company names cleaned: X of Y modified
- Sample changes:
  "JOHN (Johnny) SMITH" → "Johnny"
  "Acme Corporation, Inc." → "Acme"
```

---

## STEP 13: FINAL CSV EXPORT

### Row Filtering

**Only include rows where a valid email was found.** Contacts without valid emails and company-only rows are excluded from the final export.

### Output Format

Produce the final CSV with these exact 38 columns in this order:

```
Person LinkedIn,Full Name,First Name,Last Name,Job Title,Company Name Clean,Company Website,Domain,Headline,Summary,Company LinkedIn,Employee Count,Location,City,State,Country,Seniority,Department,Industry,Company Description,Company Product and Services,Technologies Used,Estimated Annual Revenue,Company City,Company State,Company Country,Company X (Twitter),Company Facebook,Company Number Of Locations,Company Postal Code,Company Total Funding,Company Last Funding Type,Company Last Funding Amount,Company Last Funding Date,Company Type,Company Founding Year,Valid Email,Email Host
```

### Column Mapping

| Output Column | Source |
|---------------|--------|
| Person LinkedIn | Person LinkedIn URL from AI Ark |
| Full Name | Cleaned first name + last name |
| First Name | Cleaned first name (Step 12a) |
| Last Name | `last_name` from AI Ark |
| Job Title | `title` from AI Ark |
| Company Name Clean | Cleaned company name (Step 12b) |
| Company Website | Company website URL from AI Ark |
| Domain | `domain` from enrichment |
| Headline | Person headline from AI Ark |
| Summary | Person summary from AI Ark |
| Company LinkedIn | Company LinkedIn URL from AI Ark |
| Employee Count | Employee range from AI Ark |
| Location | Person full location string |
| City | Person city |
| State | Person state |
| Country | Person country |
| Seniority | Seniority level from AI Ark |
| Department | Department/functions from AI Ark |
| Industry | Industries list from AI Ark |
| Company Description | Company description from AI Ark |
| Company Product and Services | Keywords/products from AI Ark |
| Technologies Used | Tech stack from AI Ark |
| Estimated Annual Revenue | Revenue range from AI Ark |
| Company City | HQ city from AI Ark |
| Company State | HQ state from AI Ark |
| Company Country | HQ country from AI Ark |
| Company X (Twitter) | Company Twitter/X URL |
| Company Facebook | Company Facebook URL |
| Company Number Of Locations | Location count from AI Ark |
| Company Postal Code | HQ postal code from AI Ark |
| Company Total Funding | Total funding from AI Ark |
| Company Last Funding Type | Last funding type from AI Ark |
| Company Last Funding Amount | Last funding amount from AI Ark |
| Company Last Funding Date | Last funding date from AI Ark |
| Company Type | Company type from AI Ark |
| Company Founding Year | Founded year from AI Ark |
| Valid Email | Final validated email from waterfall (Step 11) |
| Email Host | ESP provider from EmailGuard (Step 11f) |

### File Naming & Archiving

**Lookalike companies list (from /lookalike skill):**
`exports/<seed_domain>_lookalike_companies.csv`
Example: `exports/productevo_io_lookalike_companies.csv`

**Final contacts list (from /enrich skill):**
`exports/<seed_domain>_lookalike_contacts.csv`
Example: `exports/productevo_io_lookalike_contacts.csv`

Replace dots in domain with underscores: `productevo.io` → `productevo_io`

**Auto-archiving:** Before writing any export file, check if a file with the same name already exists in `exports/`. If so:
1. Create `exports/archive/` if it doesn't exist
2. Move the old file to `exports/archive/` with a timestamp suffix:
   `exports/archive/productevo_io_lookalike_contacts_20260207_120000.csv`
3. Then write the new file

### Final Summary

Display:

```
FINAL EXPORT COMPLETE
=====================
File: exports/productevo_io_lookalike_contacts.csv
Total rows: 9 (valid-email contacts only)
Contacts with good email: 8
Contacts with risky email: 1

Column count: 38
Ready for import.
```

---

## STEP 14: POST-PIPELINE OPTIONS

Ask: "Pipeline complete. What would you like to do?"

Options:
1. **Done** - End session
2. **View sample rows** - Show 5 random rows from final CSV
3. **Re-run waterfall on failures** - Retry email finding for contacts that came up empty

### If VIEW SAMPLE:
Show 5 random rows in table format with key columns.

### If RE-RUN:
Re-process only the contacts with empty Valid Email field through the waterfall again.

---

## API KEY REFERENCE

All keys are loaded from:
`/Users/nicholaskonstantinidis/Desktop/Buzzlead App Intelligence/lookalike-finder/.env`

| Variable | Service | Used In |
|----------|---------|---------|
| AIARK_API_KEY | AI Ark People Search | Steps 4-8 |
| MILLIONVERIFIER_API_KEY | Million Verifier | Steps 11a, 11e |
| TRYKIT_API_KEY | TryKit Finder + Validator | Steps 11b, 11e |
| LEADMAGIC_API_KEY | LeadMagic Email Finder | Step 11c |
| ICYPEAS_API_KEY | Icypeas Email Finder | Step 11d |
| BOUNCEBAN_API_KEY | BounceBan Validation | Step 11e |
| EMAILGUARD_API_KEY | EmailGuard ESP Lookup | Step 11f |
