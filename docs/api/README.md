# 🌐 Eclesiar API Documentation

## Overview

Comprehensive documentation for the Eclesiar API integration. This guide covers all available endpoints, authentication methods, data formats, and usage examples for the Eclesiar game data analysis application.

## 📋 Table of Contents

- [Authentication](#authentication)
- [Base Configuration](#base-configuration)
- [Available Endpoints](#available-endpoints)
- [Data Formats](#data-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🔐 Authentication

### API Token Format
```
Auth Token: eclesiar_prod_YOUR_API_KEY_HERE
```

### Request Headers
```http
Authorization: Bearer eclesiar_prod_YOUR_API_KEY_HERE
Content-Type: application/json
Accept: application/json
```

### Environment Configuration
```bash
# .env file
AUTH_TOKEN="eclesiar_prod_your_actual_key"
API_URL="https://api.eclesiar.com"
API_TIMEOUT=30
```

## ⚙️ Base Configuration

### Base URL
```
https://api.eclesiar.com
```

### Request Timeout
- **Default**: 30 seconds
- **Configurable**: via `API_TIMEOUT` environment variable

### Concurrent Workers
```bash
API_WORKERS_MARKET=6    # Market data fetching
API_WORKERS_REGIONS=8   # Region data fetching
API_WORKERS_WAR=4       # Military data fetching
API_WORKERS_HITS=4      # Battle data fetching
```

## 📡 Available Endpoints

### 1. Countries & Currencies

#### Get Countries List
```http
GET /countries
```

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 1,
      "name": "Poland",
      "currency_id": 1,
      "currency_name": "PLN",
      "is_available": true
    }
  ]
}
```

#### Get Currencies List
```http
GET /currencies
```

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 1,
      "name": "Polish Zloty",
      "code": "PLN",
      "gold_rate": 0.85
    }
  ]
}
```

### 2. Market Data

#### Get Market Items
```http
GET /market/items
```

**Query Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `country_id` | integer | Filter by country | all |
| `item_type` | string | Filter by item type | all |
| `limit` | integer | Maximum results | 100 |

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 1,
      "name": "Grain",
      "type": "FOOD",
      "country_id": 1,
      "price": 10.50,
      "currency_id": 1,
      "quantity": 1000
    }
  ]
}
```

#### Get Job Offers
```http
GET /market/jobs
```

**Query Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `country_id` | integer | Filter by country | all |
| `min_wage` | float | Minimum wage filter | 0 |
| `limit` | integer | Maximum results | 100 |

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 1,
      "title": "Factory Worker",
      "country_id": 1,
      "wage": 15.75,
      "currency_id": 1,
      "company_name": "Steel Corp",
      "available_spots": 5
    }
  ]
}
```

### 3. Currency Trading

#### Get Currency Offers
```http
GET /currency/offers
```

**Query Parameters**:
| Parameter | Type | Description | Default | Required |
|-----------|------|-------------|---------|----------|
| `currency_id` | integer | Currency ID to filter offers | - | ✅ Required |
| `transaction` | string | Transaction type (BUY/SELL) | - | ❌ Optional |
| `page` | integer | Page number for pagination | 1 | ❌ Optional |

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "rate": 0.3,
      "amount": 100,
      "owner": {
        "id": 1,
        "type": "account"
      }
    }
  ]
}
```

#### Get Currency Rates
```http
GET /currency/rates
```

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": {
    "1": 0.85,
    "2": 1.20,
    "3": 0.95
  }
}
```

### 4. Regional Data

#### Get Regions List
```http
GET /regions
```

**Query Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `country_id` | integer | Filter by country | all |
| `include_bonuses` | boolean | Include production bonuses | false |

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 1,
      "name": "Warsaw",
      "country_id": 1,
      "country_name": "Poland",
      "pollution": 15.5,
      "population": 50000,
      "bonuses": {
        "GRAIN": 10,
        "IRON": 15,
        "WEAPON": 5
      }
    }
  ]
}
```

#### Get Region Details
```http
GET /regions/{region_id}
```

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": {
    "id": 1,
    "name": "Warsaw",
    "country_id": 1,
    "pollution": 15.5,
    "population": 50000,
    "nb_npcs": 1200,
    "bonus_score": 30,
    "bonus_description": "High industrial production",
    "bonus_by_type": {
      "GRAIN": 10,
      "IRON": 15,
      "WEAPON": 5
    }
  }
}
```

### 5. Military Data

#### Get Battles/Hits
```http
GET /military/battles
```

**Query Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `country_id` | integer | Filter by country | all |
| `date_from` | string | Start date (YYYY-MM-DD) | last 24h |
| `date_to` | string | End date (YYYY-MM-DD) | now |

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 1,
      "attacker_id": 123,
      "defender_id": 456,
      "damage": 1500.75,
      "timestamp": "2025-09-18T10:30:00Z",
      "war_id": 789
    }
  ]
}
```

#### Get Wars Summary
```http
GET /military/wars
```

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 789,
      "attacker_country": "Poland",
      "defender_country": "Germany",
      "status": "active",
      "total_damage": 50000.25,
      "started_at": "2025-09-17T08:00:00Z"
    }
  ]
}
```

### 6. Warrior Rankings

#### Get Top Warriors
```http
GET /rankings/warriors
```

**Query Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `country_id` | integer | Filter by country | all |
| `limit` | integer | Maximum results | 50 |
| `ranking_type` | string | Type (damage/experience) | damage |

**Response**:
```json
{
  "code": 200,
  "description": "Success",
  "data": [
    {
      "id": 123,
      "name": "PlayerName",
      "country_id": 1,
      "damage": 15000.50,
      "experience": 25000,
      "rank": 1
    }
  ]
}
```

## 📊 Data Formats

### Standard Response Format
All API responses follow this format:
```json
{
  "code": 200,
  "description": "Success",
  "data": {}
}
```

### Date/Time Format
- **Format**: ISO 8601 with Z suffix
- **Example**: `2025-09-18T10:30:00Z`
- **Timezone**: UTC

### Currency Values
- **Base Currency**: GOLD
- **Precision**: Up to 6 decimal places
- **Format**: Floating point numbers

### Pagination
When available, pagination uses these parameters:
- `page`: Page number (starts from 1)
- `limit`: Items per page (default: 100, max: 1000)
- `total`: Total items available (in response metadata)

## ⚠️ Error Handling

### Standard Error Codes

| Code | Description | Meaning |
|------|-------------|---------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters or request format |
| 401 | Unauthorized | Invalid or missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Requested resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Temporary service outage |

### Error Response Format
```json
{
  "code": 400,
  "description": "Invalid parameter: currency_id must be an integer",
  "details": {
    "parameter": "currency_id",
    "provided": "abc",
    "expected": "integer"
  }
}
```

### Common Error Examples

#### Missing Required Parameter
```json
{
  "code": 400,
  "description": "Missing required parameter: currency_id"
}
```

#### Invalid Authentication
```json
{
  "code": 401,
  "description": "Invalid authentication token"
}
```

#### Rate Limit Exceeded
```json
{
  "code": 429,
  "description": "Rate limit exceeded. Try again in 60 seconds",
  "retry_after": 60
}
```

## 🚦 Rate Limiting

### Default Limits
- **General API**: 100 requests per minute
- **Market Data**: 200 requests per minute
- **Currency Data**: 50 requests per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1637243400
```

### Best Practices
1. **Implement backoff**: Exponential backoff on rate limit errors
2. **Cache responses**: Cache data locally when possible
3. **Batch requests**: Use bulk endpoints when available
4. **Monitor limits**: Track remaining quota

## 💡 Examples

### Complete Workflow Example

```python
import requests
import os

# Configuration
API_URL = "https://api.eclesiar.com"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# 1. Get countries
countries = requests.get(f"{API_URL}/countries", headers=headers).json()

# 2. Get market data for each country
for country in countries["data"]:
    country_id = country["id"]
    
    # Get market items
    items = requests.get(
        f"{API_URL}/market/items?country_id={country_id}",
        headers=headers
    ).json()
    
    # Get job offers
    jobs = requests.get(
        f"{API_URL}/market/jobs?country_id={country_id}",
        headers=headers
    ).json()
    
    print(f"Country: {country['name']}")
    print(f"Items: {len(items['data'])}")
    print(f"Jobs: {len(jobs['data'])}")
```

### Currency Arbitrage Example

```python
# Get currency rates
rates = requests.get(f"{API_URL}/currency/rates", headers=headers).json()

# Get currency offers for arbitrage analysis
for currency_id in rates["data"].keys():
    buy_offers = requests.get(
        f"{API_URL}/currency/offers?currency_id={currency_id}&transaction=BUY",
        headers=headers
    ).json()
    
    sell_offers = requests.get(
        f"{API_URL}/currency/offers?currency_id={currency_id}&transaction=SELL",
        headers=headers
    ).json()
    
    # Analyze arbitrage opportunities
    # ... arbitrage logic here ...
```

### Production Analysis Example

```python
# Get regions with bonuses
regions = requests.get(
    f"{API_URL}/regions?include_bonuses=true",
    headers=headers
).json()

# Analyze production efficiency
for region in regions["data"]:
    bonuses = region.get("bonuses", {})
    pollution = region.get("pollution", 0)
    
    # Calculate efficiency score
    efficiency = sum(bonuses.values()) - pollution
    
    print(f"Region: {region['name']}, Efficiency: {efficiency}")
```

## 🔧 Implementation Details

### Client Configuration
The application uses a centralized API client in `src/data/api/client.py`:

```python
class EclesiarAPIClient:
    def __init__(self, base_url, auth_token, timeout=30):
        self.base_url = base_url
        self.auth_token = auth_token
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint, params=None):
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = self.session.get(
            f"{self.base_url}/{endpoint}",
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
```

### Error Handling Strategy
```python
try:
    response = client.get("countries")
    return response["data"]
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Rate limit exceeded - implement backoff
        time.sleep(60)
        return fetch_with_retry()
    elif e.response.status_code == 401:
        # Authentication failed
        raise AuthenticationError("Invalid API token")
    else:
        raise APIError(f"HTTP {e.response.status_code}: {e.response.text}")
except requests.exceptions.RequestException as e:
    # Network error
    raise NetworkError(f"Network error: {e}")
```

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API token format: `eclesiar_prod_YOUR_KEY`
   - Check token expiration
   - Ensure correct header format

2. **Rate Limiting**
   - Implement exponential backoff
   - Reduce concurrent requests
   - Cache responses locally

3. **Network Issues**
   - Check internet connectivity
   - Verify firewall settings
   - Test with different endpoints

4. **Data Format Issues**
   - Validate response JSON structure
   - Handle missing fields gracefully
   - Check API version compatibility

### Debug Tools

```bash
# Test API connectivity
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     https://api.eclesiar.com/countries

# Check response format
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     https://api.eclesiar.com/countries | jq .

# Monitor API calls
export DEBUG=1
python3 main.py daily-report
```

### Logging

Enable detailed API logging:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('eclesiar.api')

# Log all API requests and responses
logger.debug(f"API Request: {method} {url}")
logger.debug(f"API Response: {response.status_code} {response.text}")
```

---

**API Documentation Version**: 3.3  
**Last Updated**: 2025-09-18  
**Language**: English  

**Copyright (c) 2025 Teo693**  
**Licensed under the MIT License**

For more information, see:
- [Main Documentation](../README.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Development Guide](../development/)