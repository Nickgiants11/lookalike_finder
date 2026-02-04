# lookalike_finder
Buzzlead Lookalike Finder

## Structure

```
lookalike_finder/
├── exports/                    # Lookalike search results
│   └── [client-name]/
│       ├── YYYY-MM-DD_v1.csv   # Raw exports (versioned)
│       └── search_notes.md     # Search criteria & exclusions
├── exclusion-lists/            # Reusable exclusion lists
│   └── *.csv
└── README.md
```

## Current Exports

| Client | Date | Records | Notes |
|--------|------|---------|-------|
| foreverfierce | 2026-02-04 | 50 | Custom gym apparel lookalikes |

## Workflow

1. Run lookalike discovery via Claude Code `/lookalike` skill
2. Export results to `exports/[client]/YYYY-MM-DD_v1.csv`
3. Document search criteria in `search_notes.md`
4. Edit/clean data → save as `_v2.csv`, `_v3.csv`, etc.
5. Commit changes with descriptive message

## Versioning Convention

- `_v1.csv` - Raw export from DiscoLike
- `_v2.csv` - After manual cleaning/review
- `_v3.csv` - After additional filtering
- `_cleaned.csv` - Final version ready for outreach
