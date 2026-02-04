# Lookalike Finder

Buzzlead company discovery and contact enrichment workflow powered by Claude Code, DiscoLike, and AI Ark.

## Workflow

```
/lookalike → Company CSV → /enrich → Contacts CSV → Clay
```

1. **Discover** - Find similar companies with `/lookalike`
2. **Enrich** - Add decision-maker contacts with `/enrich`
3. **Export** - Send to Clay for outreach

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
export DISCOLIKE_API_KEY='your-discolike-key'
export AIARK_API_KEY='your-aiark-key'
```

### 3. Run the Workflow

In Claude Code:

```bash
# Step 1: Find lookalike companies
/lookalike acme.com

# Step 2: Enrich with contacts
/enrich exports/acme/2026-02-04_v1.csv
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
│   └── enrich/
│       └── SKILL.md           # Contact enrichment skill
├── scripts/
│   └── enrich_contacts.py     # Standalone enrichment script
├── docs/
│   ├── AI_ARK_API.md          # AI Ark API reference
│   └── DISCOLIKE_API.md       # DiscoLike API reference
├── exports/                   # Output CSVs
│   └── [client]/
│       ├── YYYY-MM-DD_v1.csv
│       ├── *_enriched_*.csv
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

## Standalone Script

Run enrichment without Claude Code:

```bash
# Basic usage
python scripts/enrich_contacts.py input.csv

# With options
python scripts/enrich_contacts.py input.csv \
  --output enriched.csv \
  --limit 50 \
  --skip-no-contacts
```

**Options:**
| Flag | Description |
|------|-------------|
| `--output, -o` | Output file path |
| `--limit, -l` | Max companies to process |
| `--skip-no-contacts` | Exclude companies with no contacts |

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
