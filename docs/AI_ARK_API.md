# AI Ark API Documentation

Reference documentation for AI Ark B2B data enrichment API.

**Official Docs:** https://docs.ai-ark.com/

## Authentication

All API requests require an API key in the header:

```
X-TOKEN: your-api-key
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

Search for people by company domain, title, location, or other criteria.

**Endpoint:** `POST /people`

**Headers:**
```
Content-Type: application/json
X-TOKEN: your-api-key
accept: application/json
```

**Request Body Structure:**

```json
{
  "account": {
    "domain": {
      "any": {
        "include": ["example.com", "acme.com"]
      }
    },
    "location": {
      "any": {
        "include": ["united states"]
      }
    },
    "employeeSize": {
      "range": [
        {"start": 5, "end": 100}
      ]
    }
  },
  "contact": {
    "experience": {
      "latest": {
        "title": {
          "any": {
            "include": {
              "content": ["owner", "founder", "ceo", "president", "manager"]
            },
            "exclude": {
              "content": ["assistant", "intern", "student"]
            }
          }
        }
      }
    }
  },
  "page": 0,
  "size": 10
}
```

### Filter Parameters

#### Account Filters

| Field | Type | Description |
|-------|------|-------------|
| `domain.any.include` | string[] | Company domains to search |
| `location.any.include` | string[] | Company locations (e.g., "united states") |
| `employeeSize.range` | object[] | Employee count range `{start, end}` |

#### Contact Filters

| Field | Type | Description |
|-------|------|-------------|
| `experience.latest.title.any.include.content` | string[] | Job titles to include |
| `experience.latest.title.any.exclude.content` | string[] | Job titles to exclude |

### Response Structure

```json
{
  "content": [
    {
      "company": {
        "link": {
          "domain": "uniteemerch.com",
          "linkedin": "https://www.linkedin.com/company/unitee-tshirts-merch",
          "website": "http://uniteemerch.com"
        },
        "location": {
          "headquarter": {
            "city": "Lafayette",
            "state": "Louisiana",
            "country": "United States"
          }
        },
        "summary": {
          "name": "Unitee Fitness Apparel",
          "description": "...",
          "staff": {"total": 7, "range": {"start": 11, "end": 50}}
        }
      },
      "profile": {
        "first_name": "Joel",
        "last_name": "Hebert",
        "full_name": "Joel Hebert",
        "headline": "Co-Owner, UNITEE",
        "title": "Co-Owner, Unitee // Custom Tshirts and Merch"
      },
      "link": {
        "linkedin": "https://www.linkedin.com/in/joelbhebert"
      },
      "department": {
        "seniority": "owner",
        "departments": ["master_operations"],
        "functions": ["operations", "entrepreneurship"]
      },
      "position_groups": [
        {
          "company": {"name": "Unitee Fitness Apparel"},
          "profile_positions": [
            {
              "title": "Co-Owner, Unitee // Custom Tshirts and Merch",
              "date": {"start": "2019-02-01", "end": null}
            }
          ]
        }
      ]
    }
  ],
  "totalElements": 2,
  "totalPages": 1,
  "size": 10,
  "number": 0
}
```

### Field Extraction Guide

| Data Needed | Path |
|-------------|------|
| Company name | `company.summary.name` |
| Company domain | `company.link.domain` |
| Company LinkedIn | `company.link.linkedin` |
| Company city | `company.location.headquarter.city` |
| Company state | `company.location.headquarter.state` |
| First name | `profile.first_name` |
| Last name | `profile.last_name` |
| Job title | `profile.title` or `position_groups[0].profile_positions[0].title` |
| LinkedIn URL | `link.linkedin` |
| Seniority | `department.seniority` |

## Python Example

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "https://api.ai-ark.com/api/developer-portal/v1"

def search_decision_makers(domains: list, titles: list = None):
    headers = {
        "Content-Type": "application/json",
        "X-TOKEN": API_KEY,
        "accept": "application/json"
    }

    payload = {
        "account": {
            "domain": {
                "any": {
                    "include": domains
                }
            },
            "location": {
                "any": {
                    "include": ["united states"]
                }
            }
        },
        "contact": {
            "experience": {
                "latest": {
                    "title": {
                        "any": {
                            "include": {
                                "content": titles or [
                                    "owner", "founder", "ceo", "president",
                                    "general manager", "manager", "director"
                                ]
                            },
                            "exclude": {
                                "content": ["assistant", "intern", "student"]
                            }
                        }
                    }
                }
            }
        },
        "page": 0,
        "size": 50
    }

    response = requests.post(
        f"{BASE_URL}/people",
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("content", [])
    return []

# Example usage
contacts = search_decision_makers(
    domains=["graphicfx.com", "uniteemerch.com"],
    titles=["owner", "president", "manager", "coach"]
)

for person in contacts:
    profile = person.get("profile", {})
    company = person.get("company", {}).get("summary", {})
    print(f"{profile.get('full_name')} - {profile.get('title')} @ {company.get('name')}")
```

## cURL Example

```bash
curl --request POST \
  --url https://api.ai-ark.com/api/developer-portal/v1/people \
  --header 'X-TOKEN: YOUR_API_KEY' \
  --header 'accept: application/json' \
  --header 'content-type: application/json' \
  --data '{
    "account": {
      "domain": {
        "any": {
          "include": ["graphicfx.com"]
        }
      }
    },
    "contact": {
      "experience": {
        "latest": {
          "title": {
            "any": {
              "include": {
                "content": ["owner", "president", "manager"]
              }
            }
          }
        }
      }
    },
    "page": 0,
    "size": 10
  }'
```

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request - check payload structure |
| 401 | Unauthorized - check X-TOKEN header |
| 429 | Rate limited - slow down |
| 500 | Server error - retry later |

## Best Practices

1. **Batch domains** - Include multiple domains in one request (up to ~50)
2. **Use title filters** - Narrow results with include/exclude titles
3. **Handle pagination** - Use `page` parameter for large result sets
4. **Cache results** - Store responses to avoid duplicate API calls
5. **Rate limit** - Add 0.25s delay between requests
