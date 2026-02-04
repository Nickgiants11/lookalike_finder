---
name: enrich
description: Enrich a CSV of companies with decision-maker contacts using AI Ark
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
x-api-key: <AIARK_API_KEY from environment>
```

**Request Body:**
```json
{
  "page": 0,
  "size": <contacts_per_company>,
  "account_filter": {
    "domain": {
      "include": ["<company_domain>"]
    }
  },
  "contact_filter": {
    "seniority": {
      "include": ["C-Level", "VP", "Director", "Owner", "Founder"]
    },
    "department": {
      "include": ["Executive", "Sales", "Marketing", "Business Development", "Management"]
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

## STEP 6: REFINEMENT DECISION

Ask: "Based on these sample results, what would you like to do?"

Options:
1. **Proceed with all companies** - Run enrichment on remaining companies with current settings
2. **Adjust contact types** - Change seniority/department filters
3. **Change contacts per company** - Get more or fewer contacts
4. **Filter companies first** - Only enrich companies with similarity > X
5. **Cancel** - Stop enrichment

### If ADJUST CONTACT TYPES:

Show available options:

**Seniority Levels:**
- C-Level (CEO, CFO, CTO, COO, CMO, etc.)
- VP (Vice President)
- Director
- Manager
- Owner
- Founder
- Partner

**Departments:**
- Executive
- Sales
- Marketing
- Business Development
- Operations
- Finance
- Engineering/IT
- HR

Let user select which to include, then re-run sample with new filters.

### If CHANGE CONTACTS PER COMPANY:

Ask: "How many contacts per company?"
- 1 (just the top match)
- 3 (small team)
- 5 (key decision-makers)
- 10 (broad coverage)
- Custom number

Re-run sample if significantly different.

### If FILTER COMPANIES:

Ask: "What's the minimum similarity score to include?"
- Default from lookalike is usually 70+
- Filter the input CSV before enrichment

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

## OUTPUT FORMAT

Final CSV columns (Clay-ready):
```
company_name,domain,company_linkedin,employees,city,state,country,similarity,
first_name,last_name,title,seniority,department,email,phone,linkedin_url
```

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
