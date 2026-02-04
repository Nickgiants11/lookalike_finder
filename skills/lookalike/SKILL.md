---
name: lookalike
description: Run complete lookalike discovery workflow - give it a domain and it handles everything
---

# Lookalike Finder Skill

You are running an interactive lookalike company discovery workflow. This is a complete, self-running process.

## STEP 1: GET SEED DOMAIN

If the user provided a domain as an argument, use it. Otherwise ask:
"What domain would you like to find lookalikes for?"

## STEP 2: PROFILE THE SEED

Use `mcp__discolike__business-profile` with fields: domain, name, description, score, industry_groups, keywords, employees, address

Show the user:
- Company name and description
- Primary industry and confidence
- Digital footprint score
- Key keywords

Then say: "I'll use this profile to find similar companies."

## STEP 3: ASK FOR PREFERENCES

Use AskUserQuestion to ask:

1. "How many results do you want?" - Options: 50, 100, 200, 500
2. "Which country?" - Options: US only, Global, Let me specify
3. "Company size preference?" - Options: Small (1-50), Medium (11-200), Large (50-500), Any size

## STEP 4: CHECK FOR EXCLUSIONS

Ask: "Do you have any exclusions to apply?"
- Options: No exclusions, Exclude specific domains, Exclude from CSV file, Exclude industries

If they choose CSV exclusion:
- Ask for the CSV file path
- Read the CSV and extract the domain column
- Store domains in the session's excluded_domains list

If they choose domain exclusions:
- Ask them to list domains to exclude (comma-separated)

If they choose industry exclusions:
- Show available categories: SAAS, SOFTWARE, E-COMMERCE, IT_SERVICES, CONSULTING, etc.
- Let them select which to exclude

## STEP 5: RUN INITIAL DISCOVERY

Build filters based on user preferences:
```json
{
  "domain": ["<seed_domain>"],
  "max_records": <user_choice>,
  "country": <if specified>,
  "employee_range": <based on size choice>,
  "min_digital_footprint": 25,
  "max_digital_footprint": 500,
  "negate_category": <excluded industries>,
  "negate_domain": <excluded domains from CSV or list>
}
```

Use `mcp__discolike__discover-similar-companies` with fields:
domain, name, similarity, employees, score, address, industry_groups, description, public_emails, phones, social_urls

## STEP 6: SHOW RESULTS SUMMARY

Display:
- Total records found
- Similarity range (min-max)
- Industry breakdown with percentages
- Top 10 matches with: domain, name, similarity, location, employees

Calculate target industry match %: (matches in seed's primary industry / total) * 100

## STEP 7: REFINEMENT LOOP

Ask: "What would you like to do next?"

Options:
1. **Export to CSV** - Run export, show file location
2. **Refine results** - Add filters to improve targeting
3. **Get more results** - Increase count with pagination
4. **Exclude companies** - Remove specific domains from future results
5. **Start over** - New search with different seed
6. **Done** - End session

### If REFINE:
Ask what to adjust:
- Add negative phrases (exclude companies with specific text on website)
- Add negative ICP text (natural language description of what to exclude)
- Exclude more industries
- Narrow employee range
- Adjust digital footprint range

Re-run discovery and show updated stats.

### If GET MORE:
Use pagination with offset to get additional batches.
Merge with existing results, dedupe by domain.

### If EXCLUDE COMPANIES:
Ask for domains to exclude (comma-separated or CSV path).
Add to session's excluded_domains.
Re-run discovery with negate_domain filter.

### If EXPORT:
Save results to `exports/` directory as CSV with all fields.
Show: file path, record count, columns included.
Auto-archive any previous export with timestamp.

## STEP 8: SAVE SESSION

After each iteration, save to `.sessions/<seed_domain>_session.json` with:
- Seed profile
- All iterations (filters, results count, industry breakdown)
- Excluded domains list
- Current filters

## REPEAT

After completing any action, return to Step 7 (refinement loop) until user chooses "Done".

## KEY BEHAVIORS

1. Always show industry breakdown percentages after discovery
2. Track and display iteration number
3. Warn if target industry match drops below 80%
4. Auto-archive previous exports
5. Support CSV exclusion lists (look for domain/website/url columns)
6. Persist everything to session file
7. Be conversational but efficient
8. Create directories (.sessions/, exports/, exports/archive/) if they don't exist

## EXCLUSION LIST FROM CSV

To exclude domains from a CSV:
1. Read the CSV file
2. Look for columns named: domain, website, url, company_domain, Domain, Website
3. Extract all domain values
4. Clean domains (remove http://, https://, www., trailing slashes)
5. Add to negate_domain filter array (max 10 per API call, batch if needed)
