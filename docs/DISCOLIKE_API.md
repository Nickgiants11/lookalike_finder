# DiscoLike API Documentation

Reference documentation for DiscoLike company discovery API.

**Official Docs:** https://docs.discolike.com/

## Authentication

All API requests require an API key in the header:

```
x-discolike-key: your-api-key
```

Get your API key from: https://app.discolike.com/

## Base URL

```
https://api.discolike.com/v1
```

## Endpoints Used by /lookalike Skill

### Business Profile

Get company firmographic data.

**Endpoint:** `GET /bizdata`

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `domain` | string | Company domain |
| `fields` | string | Comma-separated fields to return |

**Available Fields:**
- `domain` - Company domain
- `name` - Company name
- `status` - Operating status
- `score` - Digital footprint score (1-800)
- `start_date` - Company start date
- `address` - HQ address
- `phones` - Phone numbers
- `public_emails` - Contact emails
- `social_urls` - Social media URLs
- `description` - Company description
- `keywords` - AI-generated keywords
- `industry_groups` - Industry classifications

**Example Response:**
```json
{
  "domain": "acme.com",
  "name": "Acme Corp",
  "score": 450,
  "address": {
    "city": "San Francisco",
    "state": "CA",
    "country": "US"
  },
  "industry_groups": {
    "SOFTWARE": 0.85,
    "SAAS": 0.72
  },
  "keywords": {
    "enterprise software": 0.9,
    "cloud platform": 0.85
  }
}
```

### Discover Similar Companies

Find lookalike companies using semantic search and filters.

**Endpoint:** `GET /discover`

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `domain` | string[] | Seed domain(s) for similarity |
| `icp_text` | string | Natural language ICP description |
| `country` | string[] | ISO country codes |
| `state` | string[] | State codes |
| `employee_range` | string | "min,max" format |
| `min_digital_footprint` | int | Min score (0-800) |
| `max_digital_footprint` | int | Max score (0-800) |
| `category` | string[] | Industry categories |
| `negate_category` | string[] | Industries to exclude |
| `negate_domain` | string[] | Domains to exclude |
| `tech_stack` | string[] | Required technologies |
| `max_records` | int | Results limit (max 10000) |
| `offset` | int | Pagination offset |
| `min_similarity` | int | Min similarity score (0-99) |
| `fields` | string | Output fields |

**Industry Categories:**
- `SAAS`
- `SOFTWARE`
- `E-COMMERCE`
- `IT_SERVICES`
- `HEALTHCARE`
- `FINANCIAL_SERVICES`
- `ADVERTISING_AND_MARKETING`
- `BUSINESS_PRODUCTS_AND_SERVICES`
- `SPORTS_AND_RECREATION`
- `FASHION_TEXTILE_AND_APPAREL`
- ... (50+ categories)

**Example Request:**
```
GET /discover?domain=acme.com&country=US&employee_range=10,500&max_records=100&min_similarity=70
```

**Example Response:**
```json
{
  "results": [
    {
      "domain": "similar-company.com",
      "name": "Similar Company",
      "similarity": 87,
      "score": 320,
      "employees": "51-200",
      "address": {
        "city": "Austin",
        "state": "TX",
        "country": "US"
      },
      "industry_groups": {
        "SOFTWARE": 0.78,
        "SAAS": 0.65
      }
    }
  ],
  "count": 100
}
```

### Count Matching Domains

Get count of domains matching filters (before running full discovery).

**Endpoint:** `GET /count`

**Parameters:** Same as `/discover`

**Response:**
```json
{
  "count": 15420
}
```

### Digital Footprint Score

Get score breakdown for a domain.

**Endpoint:** `GET /score`

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `domain` | string | Domain to score |

**Response:**
```json
{
  "domain": "acme.com",
  "score": 450,
  "parameters": {
    "ssl_certificates": 120,
    "subdomains": 85,
    "web_traffic": 95,
    "social_presence": 70,
    "technology_stack": 80
  }
}
```

## Filtering Best Practices

### Combining Filters

All filters are AND-ed together:
```
country=US AND employee_range=10,500 AND category=SAAS
```

### Using Exclusions

Exclude unwanted results:
```
negate_category=SPORTS_AND_RECREATION,RESTAURANTS
negate_domain=competitor1.com,competitor2.com
```

### Semantic Search

Use `icp_text` for natural language queries:
```
icp_text=B2B SaaS companies providing marketing automation for mid-market companies
```

### Hybrid Approach (Recommended)

Combine seed domains with ICP text and filters:
```
domain=hubspot.com,marketo.com
icp_text=marketing automation platform
country=US
employee_range=50,500
negate_category=CONSULTING
```

## Python Example

```python
import requests

DISCOLIKE_API_KEY = "your-api-key"
BASE_URL = "https://api.discolike.com/v1"

def discover_companies(seed_domain: str, limit: int = 100):
    headers = {"x-discolike-key": DISCOLIKE_API_KEY}

    params = {
        "domain": seed_domain,
        "country": "US",
        "min_similarity": 70,
        "max_records": limit,
        "fields": "domain,name,similarity,employees,address,industry_groups"
    }

    response = requests.get(
        f"{BASE_URL}/discover",
        headers=headers,
        params=params,
        timeout=120
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data
    return []

# Example usage
companies = discover_companies("acme.com", limit=50)
for company in companies:
    print(f"{company['domain']} - {company['similarity']}% match")
```

## MCP Integration

DiscoLike is available as an MCP server for Claude Code. When configured, you can use tools like:

- `mcp__discolike__business-profile`
- `mcp__discolike__discover-similar-companies`
- `mcp__discolike__count-matching-domains`
- `mcp__discolike__digital-footprint-score`

These are used by the `/lookalike` skill automatically.

## Plan Features

| Feature | Starter | Pro | Team | Enterprise |
|---------|---------|-----|------|------------|
| Discovery | ✓ | ✓ | ✓ | ✓ |
| Tech Stack Filter | - | - | ✓ | ✓ |
| Company Matching | - | - | ✓ | ✓ |
| Segmentation | - | ✓ | ✓ | ✓ |
| Linkage Data | - | - | - | ✓ |
