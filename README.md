# Lookalike Finder

Buzzlead lookalike company discovery workflow powered by Claude Code and DiscoLike.

## Quick Start

### 1. Install the Skill

Copy the skill to your Claude Code skills folder:

```bash
mkdir -p ~/.claude/skills
cp -r skills/lookalike ~/.claude/skills/
```

### 2. Run the Skill

In Claude Code, type:
```
/lookalike
```

Or with a domain:
```
/lookalike foreverfierce.com
```

## Requirements

- [Claude Code CLI](https://claude.ai/claude-code)
- DiscoLike MCP server configured in Claude Code
- Active DiscoLike account (PRO plan or higher recommended)

## Project Structure

```
lookalike_finder/
├── skills/
│   └── lookalike/
│       └── SKILL.md           # The Claude Code skill definition
├── exports/                   # Lookalike search results
│   └── [client-name]/
│       ├── YYYY-MM-DD_v1.csv  # Raw exports (versioned)
│       └── search_notes.md    # Search criteria & exclusions
├── exclusion-lists/           # Reusable exclusion lists
│   ├── README.md
│   └── example-exclusions.csv
├── .sessions/                 # Auto-saved session state
└── README.md
```

## Workflow

1. **Run `/lookalike`** - Start the discovery workflow
2. **Profile seed** - Analyze the target company
3. **Set preferences** - Results count, country, company size
4. **Apply exclusions** - Industries, domains, or CSV lists
5. **Review results** - Industry breakdown, top matches
6. **Refine or export** - Iterate until satisfied
7. **Save to GitHub** - Version control your research

## Features

- **Interactive discovery** - Guided workflow with refinement loop
- **Smart exclusions** - Exclude industries, domains, or import CSV lists
- **Industry analysis** - Breakdown with target match percentage
- **Session persistence** - Resume where you left off
- **Export to CSV** - Full data with all fields
- **Version control** - Track iterations with `_v1`, `_v2`, etc.

## Exclusion Lists

Store reusable exclusion lists in `exclusion-lists/`:

```csv
domain,reason
competitor.com,Direct competitor
existing-client.com,Already a customer
```

Reference them during the workflow when prompted for exclusions.

## Current Exports

| Client | Date | Records | Notes |
|--------|------|---------|-------|
| foreverfierce | 2026-02-04 | 50 | Custom gym apparel lookalikes |

## Versioning Convention

- `_v1.csv` - Raw export from DiscoLike
- `_v2.csv` - After manual cleaning/review
- `_v3.csv` - After additional filtering
- `_cleaned.csv` - Final version ready for outreach

## Contributing

This is part of the Buzzlead intelligence workflow. To add new components:

1. Create a new skill in `skills/`
2. Document in README
3. Test the workflow end-to-end
4. Commit and push
