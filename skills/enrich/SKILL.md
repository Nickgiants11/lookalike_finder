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
- Show the most recent 3-5 files

## STEP 2: VALIDATE INPUT

Read the CSV and validate:
1. Check the file exists
2. Count total rows
3. Verify it has a `domain` column (or `company_domain`, `website`)

Show the user:
- File name
- Total companies
- Sample of first 3 domains

## STEP 3: ASK FOR PREFERENCES

Ask the user:

1. "How many companies to enrich?"
   - Options: All, First 25, First 50, First 100, Custom number
   - Note: Each company = 1 API call to AI Ark

2. "What types of decision-makers?"
   - Default: C-Level, VP, Director, Owner, Founder
   - Allow customization

3. "Max contacts per company?"
   - Options: 1, 3, 5, 10
   - Default: 5

## STEP 4: CHECK API KEY

Verify AIARK_API_KEY environment variable is set:

```bash
echo $AIARK_API_KEY
```

If not set, tell user:
```
export AIARK_API_KEY='your-api-key'
```

## STEP 5: RUN ENRICHMENT

Run the enrichment script:

```bash
cd ~/lookalike_finder
python scripts/enrich_contacts.py "<input_csv>" --limit <N> --output "<output_path>"
```

Or call AI Ark API directly using `requests` via Python if script not available.

### AI Ark People Search API

**Endpoint:** `POST https://api.ai-ark.com/api/developer-portal/v1/people`

**Headers:**
```
Content-Type: application/json
x-api-key: <AIARK_API_KEY>
```

**Request Body:**
```json
{
  "page": 0,
  "size": 10,
  "account_filter": {
    "domain": {
      "include": ["example.com"]
    }
  },
  "contact_filter": {
    "seniority": {
      "include": ["C-Level", "VP", "Director", "Owner", "Founder"]
    },
    "department": {
      "include": ["Executive", "Sales", "Marketing", "Management"]
    }
  }
}
```

**Rate Limits:**
- 5 requests/second
- 300 requests/minute
- 18,000 requests/hour

**Response:**
```json
{
  "content": [
    {
      "name": "John Smith",
      "first_name": "John",
      "last_name": "Smith",
      "title": "VP of Sales",
      "email": "john@example.com",
      "linkedin_url": "https://linkedin.com/in/johnsmith",
      "seniority": "VP",
      "department": "Sales"
    }
  ],
  "totalElements": 15,
  "totalPages": 2
}
```

## STEP 6: SHOW PROGRESS

Display progress as enrichment runs:
- Current company being processed
- Running count of contacts found
- Estimated time remaining

## STEP 7: SHOW RESULTS

Display:
- Total companies processed
- Companies with contacts found
- Total contacts found
- Contact rate (% of companies with contacts)
- Output file location

Show sample of enriched data:
| Company | Contact | Title | Email |
|---------|---------|-------|-------|
| Acme Co | John Smith | VP Sales | john@acme.com |

## STEP 8: NEXT STEPS

Ask: "What would you like to do next?"

Options:
1. **Export for Clay** - Format CSV for Clay import
2. **Filter contacts** - Remove contacts missing email/phone
3. **View statistics** - Detailed breakdown by title/department
4. **Enrich more** - Process additional companies
5. **Done** - End session

### If EXPORT FOR CLAY:
Ensure CSV has Clay-compatible columns:
- first_name, last_name, email, phone, linkedin_url
- company_name, domain, company_linkedin

### If FILTER:
Remove rows where:
- email is empty AND phone is empty
- Or apply custom filters

## OUTPUT FORMAT

Final CSV columns (Clay-ready):
```
company_name, domain, company_linkedin, employees, city, state, country,
first_name, last_name, title, seniority, department, email, phone, linkedin_url
```

## KEY BEHAVIORS

1. Always show progress during enrichment
2. Handle rate limits gracefully (auto-retry with backoff)
3. Save output to `exports/[client]/` folder
4. Warn if API key not set
5. Show contact rate statistics
6. Support resuming if interrupted (save progress)

## ERROR HANDLING

- **401 Unauthorized**: Check AIARK_API_KEY
- **429 Rate Limited**: Wait and retry
- **Timeout**: Skip company, continue with next
- **No contacts found**: Keep company row with empty contact fields
