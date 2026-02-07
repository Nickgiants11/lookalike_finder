---
name: waterfall
description: Email waterfall enrichment - find and validate emails for contacts using TryKit, LeadMagic, Icypeas, Million Verifier
---

# Email Waterfall Enrichment Skill

You are running an email waterfall enrichment workflow. This takes a CSV with contacts (from `/enrich` or any source) and finds/validates email addresses.

## WATERFALL SEQUENCE

```
1. Million Verifier → Validate existing email (if present)
2. TryKit → Find email (if needed)
3. LeadMagic → Find email (if TryKit failed)
4. Icypeas → Find email (if LeadMagic failed)
5. Million Verifier → Validate found email
6. TryKit Validation → Re-check risky emails
7. BounceBan → Final validation for uncertain emails
8. ESP Lookup → Identify email provider (Outlook, Google, etc.)
```

## STEP 1: GET INPUT CSV

If the user provided a CSV path as an argument, use it. Otherwise ask:
"What CSV file would you like to enrich with emails?"

Check for recent files in `exports/` folder.

## STEP 2: VALIDATE INPUT

Read the CSV and verify it has required columns:
- `Full Name` or `first_name` + `last_name`
- `domain` or `Company Website`
- Optionally: existing `Email` column

Show:
- Total contacts
- Contacts with existing emails
- Contacts needing email lookup

## STEP 3: RUN SAMPLE (First 5)

Before processing all contacts, run a sample:

```
🔍 Running sample waterfall on first 5 contacts...
```

For each contact:
1. If has email → validate with Million Verifier
2. If no email or bad → TryKit → LeadMagic → Icypeas
3. Validate found email
4. Handle risky emails with extra validation
5. Look up ESP

Show sample results:
- Emails found: X/5
- Quality breakdown: good/risky/bad
- ESP breakdown: Outlook/Google/Other

## STEP 4: CONFIRM FULL RUN

Ask: "Sample shows X% success rate. Proceed with all contacts?"

Options:
1. **Yes, run all** - Process remaining contacts
2. **Adjust settings** - Change validation strictness
3. **Cancel** - Stop

## STEP 5: RUN FULL ENRICHMENT

Process all contacts with progress:

```
🔍 Waterfall enrichment...
[████████░░░░░░░░░░░░] 40/100 (40%)
Valid emails: 32
```

## STEP 6: DATA CLEANING

Automatically apply to all results:

### First Name Cleaning
Uses `tools/clean_first_name.py`:
- Parenthetical names: `John (Johnny)` → `Johnny`
- Quoted names: `"Nick" John` → `Nick`
- Dr. prefix preserved
- Emojis removed
- Accented chars preserved
- ALL CAPS → Title Case
- O'Brien, Mary-Jane handled

### Company Name Cleaning
Uses `tools/clean_company_name.py`:
- Legal suffixes removed (Inc, LLC, GmbH, Pte Ltd, etc.)
- ALL CAPS → Title Case
- "The" prefix removed
- Acronyms preserved (IBM, AT&T)
- DBA names handled

## STEP 7: SHOW RESULTS

Display summary:
```
📊 WATERFALL COMPLETE

Total contacts:     100
Valid emails found:  85 (85%)

Email Sources:
- TryKit:      52 (61%)
- LeadMagic:   23 (27%)
- Icypeas:      7 (8%)
- Original:     3 (4%)

Quality:
- Good:   78 (92%)
- Risky:   7 (8%)

ESP Breakdown:
- Outlook:  62 (73%)
- Google:   18 (21%)
- Other:     5 (6%)
```

## STEP 8: EXPORT

Save to: `exports/[client]/[original_name]_waterfall.csv`

Output includes all original columns plus:
- `First Name` (cleaned)
- `Company Name Clean`
- `Valid Email`
- `Email Host`
- `Email Source`
- `Email Quality`

## API KEYS REQUIRED

Set in `~/.clawdbot/secrets/buzzlead-api-keys.env`:

```
TRYKIT_API_KEY=xxx
LEADMAGIC_API_KEY=xxx
ICYPEAS_API_KEY=xxx
MILLIONVERIFIER_API_KEY=xxx
BOUNCEBAN_API_KEY=xxx
EMAILGUARD_API_KEY=xxx
```

## STANDALONE USAGE

```bash
python scripts/waterfall_enrich.py input.csv -o output.csv
python scripts/waterfall_enrich.py input.csv --secrets /path/to/keys.env
```

## KEY BEHAVIORS

1. **Always sample first** - Preview before full run
2. **Cascade on failure** - Only try next provider if previous failed
3. **Validate everything** - Never output unvalidated emails
4. **Handle risky** - Extra validation for uncertain emails
5. **Clean names** - Always apply First Name + Company Name cleaning
6. **Track sources** - Know where each email came from

## ERROR HANDLING

- **Rate limited**: Auto-retry with backoff
- **API error**: Skip contact, continue with next
- **No email found**: Keep row with empty email fields
- **Invalid existing**: Try to find new email

## EXAMPLE SESSION

```
User: /waterfall exports/acme/contacts.csv

Claude: 📂 Reading: exports/acme/contacts.csv
        Found 50 contacts (12 have existing emails)

        🔍 Running sample on first 5...
        ✓ 4/5 emails found (80%)
        - TryKit: 3, LeadMagic: 1
        - Quality: 4 good, 0 risky

        Proceed with all 50 contacts?
        > Yes

        🔍 Waterfall enrichment...
        [████████████████████] 50/50 (100%)

        📊 COMPLETE
        Valid emails: 42/50 (84%)
        Saved to: exports/acme/contacts_waterfall.csv
```
