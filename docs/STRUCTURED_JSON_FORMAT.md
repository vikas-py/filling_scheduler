# Structured JSON Export Format

## Overview

The Filling Scheduler API now provides a structured JSON export endpoint that returns schedule data in a clean, standardized format suitable for external API integration, data archival, and third-party system consumption.

## Endpoint

```
GET /api/v1/schedule/{schedule_id}/structured
```

**Authentication Required:** Yes (Bearer token)

**Status Requirements:** Schedule must be in `completed` status

## Response Format

### Top-Level Structure

```json
{
  "schedule": { /* Schedule metadata */ },
  "results": { /* Results and activities */ },
  "metadata": { /* Generation metadata */ }
}
```

### Complete Example

```json
{
  "schedule": {
    "id": 123,
    "name": "Production Week 42",
    "strategy": "smart-pack",
    "status": "completed",
    "created_at": "2025-10-15T10:00:00Z",
    "completed_at": "2025-10-15T10:05:23Z"
  },
  "results": {
    "makespan": 232.7,
    "utilization": 86.1,
    "changeovers": 20.0,
    "lots_scheduled": 15,
    "kpis": {
      "Makespan (h)": "232.70",
      "Total Clean (h)": "48.00",
      "Total Changeover (h)": "20.00",
      "Total Fill (h)": "164.70",
      "Lots Scheduled": "15",
      "Clean Blocks": "2"
    },
    "activities": [
      {
        "id": "act-1",
        "start": "2025-10-15T08:00:00Z",
        "end": "2025-10-16T08:00:00Z",
        "duration": 24.0,
        "kind": "CLEAN",
        "filler_id": 1,
        "lot_id": null,
        "lot_type": null,
        "note": "Block reset",
        "num_units": null
      },
      {
        "id": "act-2",
        "start": "2025-10-16T08:00:00Z",
        "end": "2025-10-17T00:00:00Z",
        "duration": 16.0,
        "kind": "FILL",
        "filler_id": 1,
        "lot_id": "LOT-2025-001",
        "lot_type": "VialA",
        "note": "318,720 vials",
        "num_units": 318720
      },
      {
        "id": "act-3",
        "start": "2025-10-17T00:00:00Z",
        "end": "2025-10-17T12:00:00Z",
        "duration": 12.0,
        "kind": "IDLE",
        "filler_id": 2,
        "lot_id": null,
        "lot_type": null,
        "note": null,
        "num_units": null
      }
    ]
  },
  "metadata": {
    "generated_at": "2025-10-15T10:30:00Z",
    "api_version": "1.0",
    "format_version": "1.0"
  }
}
```

## Schema Reference

### Schedule Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique schedule identifier |
| `name` | string \| null | Schedule name (if provided) |
| `strategy` | string | Scheduling algorithm used (e.g., "smart-pack", "lpt-pack") |
| `status` | string | Current status (always "completed" for this endpoint) |
| `created_at` | datetime | ISO 8601 timestamp when schedule was created |
| `completed_at` | datetime \| null | ISO 8601 timestamp when schedule completed |

### Results Object

| Field | Type | Description |
|-------|------|-------------|
| `makespan` | float | Total schedule duration in hours |
| `utilization` | float | Overall filler utilization percentage (0-100) |
| `changeovers` | float | Total changeover time in hours |
| `lots_scheduled` | integer | Number of lots successfully scheduled |
| `kpis` | object | Key performance indicators as string key-value pairs |
| `activities` | array | List of scheduled activities (see Activity schema) |

### Activity Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique activity identifier (e.g., "act-1", "act-2") |
| `start` | datetime | ISO 8601 start timestamp (actual calendar time) |
| `end` | datetime | ISO 8601 end timestamp (actual calendar time) |
| `duration` | float | Duration in hours |
| `kind` | string | Activity type: "FILL", "CLEAN", or "IDLE" |
| `filler_id` | integer | Filler machine ID (1-indexed) |
| `lot_id` | string \| null | Lot identifier (for FILL activities) |
| `lot_type` | string \| null | Product/lot type (for FILL activities) |
| `note` | string \| null | Human-readable note (e.g., "318,720 vials", "Block reset") |
| `num_units` | integer \| null | Number of units produced (for FILL activities) |

### Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `generated_at` | datetime | ISO 8601 timestamp when export was generated |
| `api_version` | string | API version (currently "1.0") |
| `format_version` | string | Export format version (currently "1.0") |

## Activity Types

### FILL
Represents actual lot production on a filler.
- **Includes:** `lot_id`, `lot_type`, `num_units`, formatted note
- **Example:** Production of LOT-2025-001 producing 318,720 vials

### CLEAN
Represents cleaning/changeover periods between incompatible products.
- **Includes:** `note` (typically "Block reset")
- **Excludes:** lot-specific fields

### IDLE
Represents idle time when a filler is waiting.
- **All lot fields are null**
- Used for gaps in scheduling

## Time Handling

### Actual Calendar Times
All activity timestamps (`start`, `end`) use actual calendar datetime values:

- **If schedule has `start_time`:** Activities are calculated from that base time
- **If no `start_time`:** Activities are calculated from schedule `created_at` time

### Timezone
All timestamps are returned in UTC (ISO 8601 format with 'Z' suffix).

## Usage Examples

### cURL

```bash
curl -X GET "https://api.example.com/api/v1/schedule/123/structured" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Accept: application/json"
```

### Python

```python
import requests

token = "YOUR_TOKEN_HERE"
schedule_id = 123

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

response = requests.get(
    f"https://api.example.com/api/v1/schedule/{schedule_id}/structured",
    headers=headers
)

data = response.json()
print(f"Schedule: {data['schedule']['name']}")
print(f"Makespan: {data['results']['makespan']} hours")
print(f"Activities: {len(data['results']['activities'])}")
```

### JavaScript/TypeScript

```typescript
const token = "YOUR_TOKEN_HERE";
const scheduleId = 123;

const response = await fetch(
  `https://api.example.com/api/v1/schedule/${scheduleId}/structured`,
  {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/json"
    }
  }
);

const data = await response.json();
console.log(`Schedule: ${data.schedule.name}`);
console.log(`Makespan: ${data.results.makespan} hours`);
console.log(`Activities: ${data.results.activities.length}`);
```

## Comparison with Standard Endpoint

| Feature | Standard (`/schedule/{id}`) | Structured (`/schedule/{id}/structured`) |
|---------|----------------------------|------------------------------------------|
| Activity timestamps | Relative hours from start | Actual ISO 8601 datetimes |
| Filler IDs | 0-indexed | 1-indexed |
| Activity IDs | Internal/numeric | Clean string format ("act-1") |
| KPI values | Mixed types | Consistent strings |
| Metadata | Limited | Full generation metadata |
| Purpose | UI consumption | API integration, archival |

## Error Responses

### 404 Not Found
```json
{
  "detail": "Schedule not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Schedule not completed yet"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

## Use Cases

### 1. External System Integration
Export schedule data to external MES, ERP, or warehouse management systems.

### 2. Data Archival
Store schedule results in a standardized format for long-term archival and compliance.

### 3. Business Intelligence
Feed schedule data into BI tools for analysis and reporting.

### 4. Audit Trail
Maintain immutable records of scheduling decisions with full timestamp information.

### 5. Cross-Platform Integration
Share schedule data with third-party systems that don't use the web UI.

## Best Practices

### 1. Caching
The structured export is expensive to generate. Cache the result if you need to access it multiple times.

### 2. Pagination (Future)
For very large schedules with thousands of activities, consider implementing pagination or streaming.

### 3. Versioning
Always check the `format_version` field to ensure compatibility with your consumer code.

### 4. Timezone Handling
All timestamps are UTC. Convert to local timezone in your application if needed.

### 5. Error Handling
Always check response status codes and handle errors appropriately.

## Future Enhancements

Potential future additions to the structured format:

- **Pagination:** Support for large activity lists
- **Filtering:** Query parameters to filter activities by type, filler, or time range
- **Compression:** Gzip support for large exports
- **Webhook:** Push notifications when schedules complete with structured data
- **Batch Export:** Export multiple schedules in one request

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-15 | Initial release with structured JSON format |

## Support

For questions or issues with the structured JSON export:

1. Check API documentation at `/docs` endpoint
2. Review this document for format specification
3. Contact API support with schedule ID and error details

---

**Last Updated:** October 15, 2025
**API Version:** 1.0
**Format Version:** 1.0
