# Lookalike Finder

Buzzlead company discovery and contact enrichment workflow powered by Claude Code, DiscoLike, and AI Ark.

## Workflow

```
/lookalike → Company CSV → /enrich → Contacts CSV → /waterfall → Final CSV → Clay
```

1. **Discover** - Find similar companies with `/lookalike`
2. **Enrich** - Add decision-maker contacts with `/enrich`
3. **Waterfall** - Find & validate emails with `/waterfall`
4. **Export** - Send to Clay for outreach

## Quick Start

### 1. Install Skills

```bash
# Clone the repo
git clone https://github.com/Nickgiants11/lookalike_finder.git
cd lookalike_finder

# Copy skills to Claude Code
cp -r skills/lookalike ~/.claude/skills/
cp -r skills/enrich ~/.claude/skills/
```

### 2. Set API Keys

```bash
# Discovery & Contacts
export DISCOLIKE_API_KEY='your-discolike-key'
export AIARK_API_KEY='your-aiark-key'

# Email Waterfall (store in ~/.clawdbot/secrets/buzzlead-api-keys.env)
TRYKIT_API_KEY=xxx
LEADMAGIC_API_KEY=xxx
ICYPEAS_API_KEY=xxx
MILLIONVERIFIER_API_KEY=xxx
BOUNCEBAN_API_KEY=xxx
EMAILGUARD_API_KEY=xxx
```

### 3. Run the Workflow

In Claude Code:

```bash
# Step 1: Find lookalike companies
/lookalike acme.com

# Step 2: Enrich with contacts
/enrich exports/acme/2026-02-04_v1.csv

# Step 3: Find & validate emails
/waterfall exports/acme/2026-02-04_v1_enriched.csv
```

## Requirements

- [Claude Code CLI](https://claude.ai/claude-code)
- DiscoLike MCP server configured (for `/lookalike`)
- AI Ark API key (for `/enrich`)
- Python 3.8+ (for standalone scripts)

### Python Dependencies

```bash
pip install requests
```

## Project Structure

```
lookalike_finder/
├── skills/
│   ├── lookalike/
│   │   └── SKILL.md           # Company discovery skill
│   ├── enrich/
│   │   └── SKILL.md           # Contact enrichment skill
│   └── waterfall/
│       └── SKILL.md           # Email waterfall skill
├── scripts/
│   ├── enrich_contacts.py     # Standalone contact enrichment
│   └── waterfall_enrich.py    # Standalone email waterfall
├── tools/
│   ├── clean_first_name.py    # First name cleaner (Python)
│   ├── clean_first_name.js    # First name cleaner (Clay/JS)
│   ├── clean_company_name.py  # Company name cleaner (Python)
│   └── clean_company_name.js  # Company name cleaner (Clay/JS)
├── docs/
│   ├── AI_ARK_API.md          # AI Ark API reference
│   └── DISCOLIKE_API.md       # DiscoLike API reference
├── exports/                   # Output CSVs
│   └── [client]/
│       ├── YYYY-MM-DD_v1.csv
│       ├── *_enriched_*.csv
│       ├── *_waterfall.csv
│       └── search_notes.md
├── exclusion-lists/           # Reusable domain exclusions
├── .sessions/                 # Session state
└── README.md
```

## Skills

### /lookalike

Discover similar companies based on a seed domain.

**Usage:**
```
/lookalike              # Interactive mode
/lookalike acme.com     # With seed domain
```

**Features:**
- Profile seed company
- Set filters (country, size, industry)
- Apply exclusions (domains, industries, CSV lists)
- View industry breakdown
- Export to CSV

**Outputs:** `exports/[client]/YYYY-MM-DD_v1.csv`

### /enrich

Enrich a company CSV with decision-maker contacts.

**Usage:**
```
/enrich                           # Interactive mode
/enrich exports/client/file.csv   # With input file
```

**Features:**
- Read lookalike CSV
- Find decision-makers via AI Ark
- Filter by seniority/department
- Export Clay-ready CSV

**Outputs:** `exports/[client]/*_enriched_*.csv`

### /waterfall

Find and validate emails for contacts using cascading providers.

**Usage:**
```
/waterfall                           # Interactive mode
/waterfall exports/client/file.csv   # With input file
```

**Waterfall Sequence:**
1. Million Verifier (validate existing)
2. TryKit (find email)
3. LeadMagic (find email)
4. Icypeas (find email)
5. Million Verifier (validate found)
6. TryKit Validation (risky check)
7. BounceBan (final validation)
8. ESP Lookup (identify provider)

**Features:**
- Cascading email finders (stops when found)
- Multi-layer validation
- Risky email handling
- ESP identification (Outlook, Google, etc.)
- Auto-applies name cleaning (First Name, Company Name)

**Outputs:** `exports/[client]/*_waterfall.csv`

## Tools

### Name Cleaners

Automatically applied during waterfall enrichment. Also available as standalone Clay/JS formulas.

**clean_first_name:**
- Parenthetical names: `John (Johnny)` → `Johnny`
- Quoted names: `"Nick" John` → `Nick`
- Dr. prefix: `Dr. John Smith` → `Dr. John`
- Emojis/special chars removed
- Accented chars preserved: `José` → `José`
- ALL CAPS: `JOHN` → `John`
- Hyphenated: `mary-jane` → `Mary-Jane`
- Apostrophes: `o'connor` → `O'Connor`

**clean_company_name:**
- 50+ legal suffixes: `Inc`, `LLC`, `GmbH`, `Pte. Ltd.`, etc.
- ALL CAPS: `ACME INC` → `Acme`
- "The" prefix: `The Home Depot` → `Home Depot`
- Preserves acronyms: `IBM`, `AT&T`, `BMW`, `3M`
- DBA handling: `Legal Name LLC DBA Brand` → `Legal Name`

## Standalone Scripts

Run without Claude Code:

### Contact Enrichment

```bash
python scripts/enrich_contacts.py input.csv
python scripts/enrich_contacts.py input.csv --output enriched.csv --limit 50
```

| Flag | Description |
|------|-------------|
| `--output, -o` | Output file path |
| `--limit, -l` | Max companies to process |
| `--skip-no-contacts` | Exclude companies with no contacts |

### Email Waterfall

```bash
python scripts/waterfall_enrich.py input.csv
python scripts/waterfall_enrich.py input.csv -o output.csv -s /path/to/secrets.env
```

| Flag | Description |
|------|-------------|
| `--output, -o` | Output file path |
| `--delay, -d` | Delay between contacts (default: 0.5s) |
| `--secrets, -s` | Path to API keys file |

## API Documentation

- [DiscoLike API](docs/DISCOLIKE_API.md) - Company discovery
- [AI Ark API](docs/AI_ARK_API.md) - Contact enrichment

## Output Format

### Lookalike CSV
```csv
domain,name,similarity,employees,score,city,state,country,primary_industry,description
```

### Enriched CSV (Clay-ready)
```csv
company_name,domain,company_linkedin,employees,city,state,country,
first_name,last_name,title,seniority,department,email,phone,linkedin_url
```

## Versioning Convention

| Suffix | Meaning |
|--------|---------|
| `_v1.csv` | Raw export from DiscoLike |
| `_v2.csv` | After manual review |
| `_enriched_*.csv` | With contacts added |
| `_cleaned.csv` | Final for outreach |

## Current Exports

| Client | Date | Companies | Contacts | Status |
|--------|------|-----------|----------|--------|
| foreverfierce | 2026-02-04 | 50 | - | Needs enrichment |

## Environment Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `DISCOLIKE_API_KEY` | /lookalike | DiscoLike API key |
| `AIARK_API_KEY` | /enrich | AI Ark API key |

## Contributing

To add new components:

1. Create skill in `skills/[name]/SKILL.md`
2. Add scripts to `scripts/`
3. Document APIs in `docs/`
4. Update this README
5. Test end-to-end
6. Commit and push
