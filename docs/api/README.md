# Currency Offers API Endpoint

This document describes the new currency offers endpoint that allows filtering currency offers by currency ID, transaction type, and pagination.

## Endpoint

```
GET /api/currency/offers
```

## Parameters

| Parameter | Type | Description | Default | Required |
|-----------|------|-------------|---------|----------|
| `currency_id` | integer | The ID of the currency to filter offers by | - | ✅ Required |
| `transaction` | string | The type of transaction to filter offers by (BUY or SELL) | - | ❌ Optional |
| `page` | integer | The page number for pagination | 1 | ❌ Optional |

## Example Requests

### Basic request (currency_id only)
```bash
curl "http://localhost:5000/api/currency/offers?currency_id=1"
```

### With transaction filter
```bash
curl "http://localhost:5000/api/currency/offers?currency_id=1&transaction=BUY"
```

### With pagination
```bash
curl "http://localhost:5000/api/currency/offers?currency_id=1&page=2"
```

### Combined filters
```bash
curl "http://localhost:5000/api/currency/offers?currency_id=1&transaction=SELL&page=3"
```

## Response Format

### Success Response (200)
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

### Error Responses

#### Missing Required Parameter (400)
```json
{
    "code": 400,
    "description": "Missing required parameter: currency_id"
}
```

#### Invalid Parameter (400)
```json
{
    "code": 400,
    "description": "Invalid currency_id: must be an integer"
}
```

#### Server Error (500)
```json
{
    "code": 500,
    "description": "Internal server error: [error details]"
}
```

## Running the API Server

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python web_api.py
```

The server will start on `http://localhost:5000`

## Testing

Run the test script to verify the endpoint works correctly:
```bash
python test_currency_endpoint.py
```

## Implementation Details

- The endpoint uses the existing `fetch_currency_offers()` function from `economy.py`
- Data validation ensures all parameters are properly formatted
- The response format matches the API specification exactly
- Error handling provides clear feedback for invalid requests
- The endpoint integrates with the existing Eclesiar API client infrastructure
