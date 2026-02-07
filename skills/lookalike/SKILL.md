---
name: lookalike
description: Run complete lookalike discovery workflow with thorough QA review
---

# Lookalike Finder Skill

Interactive lookalike company discovery with **thorough quality review**.

## CRITICAL: QA PROCESS

Every batch MUST go through this review process. Do NOT skip steps.

---

## STEP 1: GET SEED DOMAIN

If user provided a domain, use it. Otherwise ask:
"What domain would you like to find lookalikes for?"

## STEP 2: PROFILE THE SEED

Call DiscoLike BizData API to get:
- Company name, description
- Primary industries
- Keywords
- Location, score

**Show the user:**
```
📊 Seed Analysis: [Company Name]
- Domain: [domain]
- Location: [city, state]
- Industries: [list]
- Description: [summary]
- Top Keywords: [list]
```

Identify **what the company DOES** and **who they serve** (important for QA later).

## STEP 3: ASK FOR PREFERENCES (Every Time!)

**Always ask these 4 questions:**

1. "How many companies for this batch?" (50 / 100 / 200 / 500)
2. "Which location?" (US only / specific states / global)
3. "Company size (employees)?" (1-10 / 11-50 / 51-200 / any)
4. "Any CSV exclusion list to apply?" (path or "none")

## STEP 4: RUN INITIAL BATCH

Build filters and call DiscoLike Discover API:
```
domain=[seed]
country=[preference]
employee_range=[preference]
max_records=[preference]
min_similarity=60
negate_category=[any from previous iterations]
negate_domain=[any from previous iterations]
```

Cache raw results to `/tmp/discolike_batch.json` for analysis.

## STEP 5: SHOW INDUSTRY BREAKDOWN

```
📊 INDUSTRY BREAKDOWN:
| Industry | Count | % | Notes |
|----------|-------|---|-------|
| BUSINESS_PRODUCTS_AND_SERVICES | 21 | 42% | ✓ Target |
| SPORTS_AND_RECREATION | 10 | 20% | ⚠️ Review |
```

Calculate target industry match percentage.

**⚠️ WARN if target match < 80%**

## STEP 6: THOROUGH QA REVIEW (CRITICAL!)

**Do NOT skip this step. Review ALL companies.**

### 6a. Show Full List
Display ALL companies with:
- Domain, Name
- Primary Industry
- Description snippet (first 150 chars)
- Location

Save to CSV for user to review: `exports/[client]/batch_full_review.csv`

### 6b. Identify Non-Fits
For each company, check if it matches the seed's business model:
- Is it the same TYPE of business?
- Or is it a CUSTOMER of the seed?

**Common issues to flag:**
- Gyms/fitness centers (if seed sells TO gyms)
- Web agencies (if seed is product company)
- Software companies (if seed is services)
- Restaurants, real estate, healthcare (usually wrong)

### 6c. Analyze Descriptions
Look for phrases that distinguish BAD fits from GOOD fits:
- What phrases appear in non-fits but NOT in good fits?
- These become phrase exclusions

**Example analysis:**
```
Phrase              | In Bad | In Good | Recommend
"fitness gym"       | 6      | 0       | ✅ EXCLUDE
"personal training" | 5      | 0       | ✅ EXCLUDE
"screen printing"   | 0      | 15      | ✅ KEEP (target phrase)
```

### 6d. Present Findings

Show:
1. **Red Flags** - Companies to exclude with reasoning
2. **Questionable** - Need user input
3. **Good Fits** - Count of clean companies

**Recommendations format:**
```
📋 EXCLUSION RECOMMENDATIONS:

DOMAINS TO EXCLUDE:
- domain1.com (reason)
- domain2.com (reason)

PHRASE EXCLUSIONS (for future batches):
- "fitness gym"
- "personal training"
- "web design"

INDUSTRY EXCLUSIONS:
- SPORTS_AND_RECREATION
```

## STEP 7: ASK FOR CONFIRMATION

```
Do you confirm these exclusions?
1. ✅ Yes, apply all
2. ⚠️ Modify (tell me which)
3. 🔍 Review something else first
```

**Wait for user confirmation before proceeding.**

## STEP 8: APPLY EXCLUSIONS & EXPORT

After confirmation:
1. Remove excluded domains
2. Remove companies in excluded industries
3. Save clean CSV: `exports/[client]/[client]_companies_clean.csv`
4. Show final count

```
✅ BATCH COMPLETE
   Total found: 50
   Excluded: 11
   Clean companies: 39
   Saved to: exports/[client]/[client]_companies_clean.csv
```

## STEP 9: SAVE SESSION STATE

Save to `.sessions/[seed]_session.json`:
```json
{
  "seed_domain": "example.com",
  "iterations": [{
    "number": 1,
    "filters": {...},
    "results_count": 50,
    "clean_count": 39,
    "exclusions_applied": {...}
  }],
  "phrase_exclusions": ["fitness gym", ...],
  "industry_exclusions": ["SPORTS_AND_RECREATION"],
  "domain_exclusions": ["bad-domain.com"]
}
```

## STEP 10: ASK FOR NEXT BATCH

```
How many companies for the next batch? (50 / 100 / 200 / 500 / done)
```

If user wants more:
- Apply accumulated exclusions (phrases, industries, domains)
- Run new batch with offset
- Repeat QA process (Steps 5-9)

---

## KEY BEHAVIORS (MUST FOLLOW)

1. **Always show industry breakdown** after discovery
2. **Always review ALL companies** - not just a sample
3. **Always analyze descriptions** for exclusion phrases
4. **Always ask for confirmation** before applying exclusions
5. **Always track iteration number**
6. **Always save session state**
7. **Warn if target industry match < 80%**
8. **Be thorough** - catch non-fits BEFORE user has to point them out

---

## EXCLUSION TYPES

### Industry Exclusions (negate_category)
Broad categories to exclude entirely:
- `SPORTS_AND_RECREATION` - gyms, fitness centers
- `RESTAURANTS` - food service
- `REAL_ESTATE` - property companies
- `HEALTHCARE` - medical (unless relevant)

### Phrase Exclusions (negate_keyword / ICP text)
Specific phrases that indicate non-fits:
- "fitness gym", "crossfit gym", "fitness facility"
- "personal training", "group fitness"
- "web design", "digital marketing"

### Domain Exclusions (negate_domain)
Specific domains to exclude (max 10 per API call).

### If EXPORT:
Save results to `exports/` directory as CSV with all fields.

**File naming:** `<seed_domain>_lookalike_companies.csv`
- Replace dots in domain with underscores: `productevo.io` → `productevo_io_lookalike_companies.csv`
- Example: `exports/productevo_io_lookalike_companies.csv`

**Auto-archive:** Before writing, check if a file with the same name already exists. If so, move the old file to `exports/archive/` with a timestamp suffix:
- `exports/archive/productevo_io_lookalike_companies_20260207_120000.csv`
- Create `exports/archive/` if it doesn't exist.

Show: file path, record count, columns included.

---

## COMMON MISTAKES TO AVOID

❌ Skipping the QA review
❌ Only showing a sample instead of all results
❌ Not analyzing descriptions for patterns
❌ Excluding too broadly (hitting good fits)
❌ Not asking for confirmation
❌ Forgetting to save session state
❌ Not tracking iteration number

---

## EXAMPLE SESSION

```
User: /lookalike foreverfierce.com

Claude: 📊 Seed Analysis: Forever Fierce
- Domain: foreverfierce.com
- Location: Cary, NC
- Industries: Business Products & Services, E-Commerce
- Description: Custom gym apparel and screen printing for gyms

Forever Fierce SELLS apparel TO gyms. So we want other apparel/merch 
companies, NOT the gyms themselves.

Before I pull results:
1. How many companies? (50/100/200/500)
2. Location? (US only / specific / global)
3. Company size? (1-10 / 11-50 / 51-200 / any)
4. Exclusion CSV? (path or "none")

User: 50, US only, 11-50, none

Claude: 🔄 /lookalike foreverfierce.com — Iteration #1

📊 INDUSTRY BREAKDOWN:
[shows breakdown]

Now reviewing ALL 50 companies...

[shows full list with descriptions]

🔍 QA FINDINGS:

🏋️ RED FLAGS - Found 10 GYMS (customers, not competitors):
- cfcoordinate.com (CrossFit gym in Cary)
- [etc...]

📋 RECOMMENDATIONS:
- Exclude SPORTS_AND_RECREATION industry
- Add phrase exclusions: "fitness gym", "personal training"

Do you confirm? (Y/N)

User: Y

Claude: ✅ BATCH COMPLETE
Clean companies: 39
Saved to: exports/foreverfierce/foreverfierce_companies_clean.csv

How many for next batch?
```
