# AI Ark API Documentation

Reference documentation for AI Ark B2B data enrichment API.

**Official Docs:** https://docs.ai-ark.com/

## Authentication

All API requests require an API key in the header:

```
x-api-key: your-api-key
```

Get your API key from: https://ai-ark.com/

## Base URL

```
https://api.ai-ark.com/api/developer-portal/v1
```

## Rate Limits

| Limit | Value |
|-------|-------|
| Per second | 5 requests |
| Per minute | 300 requests |
| Per hour | 18,000 requests |

## Endpoints

### People Search

Search for people by company, title, seniority, or other criteria.

**Endpoint:** `POST /people`

**Request:**
```json
{
  "page": 0,
  "size": 10,
  "account_filter": {
    "domain": {
      "include": ["acme.com"]
    }
  },
  "contact_filter": {
    "seniority": {
      "include": ["C-Level", "VP", "Director"]
    },
    "department": {
      "include": ["Sales", "Marketing", "Executive"]
    }
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "id": "abc123",
      "name": "John Smith",
      "first_name": "John",
      "last_name": "Smith",
      "title": "VP of Sales",
      "seniority": "VP",
      "department": "Sales",
      "email": "john@acme.com",
      "phone": "+1-555-123-4567",
      "linkedin_url": "https://linkedin.com/in/johnsmith",
      "company": {
        "name": "Acme Corp",
        "domain": "acme.com"
      }
    }
  ],
  "pageable": {
    "pageNumber": 0,
    "pageSize": 10
  },
  "totalElements": 45,
  "totalPages": 5
}
```

### Account Filters

Filter by company attributes:

| Field | Type | Description |
|-------|------|-------------|
| `domain` | object | Company domain(s) |
| `name` | object | Company name |
| `industry` | object | Industry classification |
| `employee_size` | object | Employee count range |
| `revenue` | object | Revenue range |
| `location` | object | HQ location |
| `technologies` | object | Tech stack |

**Filter Structure:**
```json
{
  "domain": {
    "include": ["acme.com", "example.com"],
    "exclude": ["competitor.com"]
  }
}
```

### Contact Filters

Filter by person attributes:

| Field | Type | Description |
|-------|------|-------------|
| `seniority` | object | Seniority level |
| `department` | object | Department/function |
| `title` | object | Job title keywords |
| `location` | object | Person location |
| `skills` | object | Skills/expertise |

**Seniority Values:**
- `C-Level`
- `VP`
- `Director`
- `Manager`
- `Owner`
- `Founder`
- `Partner`

**Department Values:**
- `Executive`
- `Sales`
- `Marketing`
- `Business Development`
- `Operations`
- `Finance`
- `Engineering`
- `HR`
- `Legal`
- `IT`

### Reverse People Lookup

Look up a person by email or LinkedIn URL.

**Endpoint:** `POST /people/reverse-lookup`

**Request:**
```json
{
  "email": "john@acme.com"
}
```

Or:
```json
{
  "linkedin_url": "https://linkedin.com/in/johnsmith"
}
```

### Mobile Phone Finder

Find direct phone numbers for a contact.

**Endpoint:** `POST /people/mobile-phone-finder`

**Request:**
```json
{
  "person_id": "abc123"
}
```

Or:
```json
{
  "linkedin_url": "https://linkedin.com/in/johnsmith"
}
```

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request - check payload |
| 401 | Unauthorized - check API key |
| 403 | Forbidden - insufficient permissions |
| 429 | Rate limited - slow down |
| 500 | Server error - retry later |

**Error Response Format:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Please wait before making more requests",
  "retry_after": 60
}
```

## Python Example

```python
import requests

AIARK_API_KEY = "your-api-key"
BASE_URL = "https://api.ai-ark.com/api/developer-portal/v1"

def search_people(domain: str, seniorities: list = None):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": AIARK_API_KEY
    }

    payload = {
        "page": 0,
        "size": 10,
        "account_filter": {
            "domain": {"include": [domain]}
        }
    }

    if seniorities:
        payload["contact_filter"] = {
            "seniority": {"include": seniorities}
        }

    response = requests.post(
        f"{BASE_URL}/people",
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code == 200:
        return response.json().get("content", [])
    return []

# Example usage
people = search_people("acme.com", ["C-Level", "VP", "Director"])
for person in people:
    print(f"{person['name']} - {person['title']}")
```

## cURL Example

```bash
curl -X POST "https://api.ai-ark.com/api/developer-portal/v1/people" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "page": 0,
    "size": 10,
    "account_filter": {
      "domain": {"include": ["acme.com"]}
    },
    "contact_filter": {
      "seniority": {"include": ["C-Level", "VP"]}
    }
  }'
```

## Best Practices

1. **Batch requests** - Process companies in batches with delays
2. **Handle rate limits** - Implement exponential backoff on 429
3. **Cache results** - Store lookups to avoid duplicate API calls
4. **Filter early** - Use specific filters to reduce result sets
5. **Paginate large results** - Use page/size for >100 results
