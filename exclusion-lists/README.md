# Exclusion Lists

Store reusable domain exclusion lists here. These can be referenced when running the `/lookalike` skill.

## Format

CSV files with a `domain` column:

```csv
domain
competitor1.com
competitor2.com
existingclient.com
```

## Supported Column Names

The skill auto-detects these column names:
- `domain`
- `website`
- `url`
- `company_domain`
- `Domain`
- `Website`

## Example Lists

| File | Purpose |
|------|---------|
| `existing-clients.csv` | Domains of current clients to exclude |
| `competitors.csv` | Known competitors to exclude |
| `do-not-contact.csv` | Blacklisted domains |

## Usage

When running `/lookalike`, choose "Exclude from CSV file" and provide the path:
```
~/lookalike_finder/exclusion-lists/existing-clients.csv
```
