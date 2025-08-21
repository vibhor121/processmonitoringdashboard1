# Process Monitor API Specification

## Overview

The Process Monitor API provides RESTful endpoints for submitting process data from monitoring agents and retrieving process information for the frontend dashboard.

## Authentication

All API endpoints use API key authentication via the `X-API-Key` header.

**Default API Key**: `process-monitor-api-key-2024`

```http
X-API-Key: process-monitor-api-key-2024
```

## Base URL

```
http://localhost:8000/api/
```

## Endpoints

### 1. Submit Process Data

Submit process information from monitoring agents.

**Endpoint**: `POST /api/submit/`

**Headers**:
```
Content-Type: application/json
X-API-Key: process-monitor-api-key-2024
```

**Request Body**:
```json
{
    "hostname": "server01",
    "ip_address": "192.168.1.100",
    "os_info": "Linux 5.4.0-74-generic x86_64",
    "processes": [
        {
            "pid": 1234,
            "parent_pid": 1,
            "name": "systemd",
            "cmdline": "/sbin/init",
            "username": "root",
            "status": "sleeping",
            "cpu_percent": 0.1,
            "memory_percent": 0.5,
            "memory_rss": 8192000,
            "memory_vms": 16384000,
            "create_time": 1640995200.0
        }
    ]
}
```

**Response** (201 Created):
```json
{
    "message": "Process data received successfully",
    "host": "server01",
    "snapshot_id": 42,
    "processes_created": 150,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
    "error": "Invalid data format",
    "details": {
        "hostname": ["This field is required."]
    }
}
```

### 2. List Hosts

Retrieve all monitored hosts.

**Endpoint**: `GET /api/hosts/`

**Headers**: None required (public endpoint)

**Response** (200 OK):
```json
[
    {
        "id": 1,
        "hostname": "server01",
        "ip_address": "192.168.1.100",
        "os_info": "Linux 5.4.0-74-generic x86_64",
        "first_seen": "2024-01-15T09:00:00Z",
        "last_seen": "2024-01-15T10:30:00Z",
        "latest_snapshot": {
            "id": 42,
            "hostname": "server01",
            "timestamp": "2024-01-15T10:30:00Z",
            "total_processes": 150,
            "processes": [...]
        }
    }
]
```

### 3. Get Process Tree

Retrieve the latest process tree for a specific host.

**Endpoint**: `GET /api/hosts/{hostname}/processes/`

**Parameters**:
- `hostname` (path) - The hostname of the target system

**Response** (200 OK):
```json
{
    "hostname": "server01",
    "timestamp": "2024-01-15T10:30:00Z",
    "total_processes": 150,
    "process_tree": [
        {
            "id": 1,
            "pid": 1,
            "name": "systemd",
            "cmdline": "/sbin/init",
            "cpu_percent": 0.1,
            "memory_percent": 0.5,
            "memory_rss": 8192000,
            "memory_vms": 16384000,
            "status": "sleeping",
            "username": "root",
            "children": [
                {
                    "id": 2,
                    "pid": 123,
                    "name": "kthreadd",
                    "cmdline": "",
                    "cpu_percent": 0.0,
                    "memory_percent": 0.0,
                    "memory_rss": 0,
                    "memory_vms": 0,
                    "status": "sleeping",
                    "username": "root",
                    "children": []
                }
            ]
        }
    ]
}
```

**Error Response** (404 Not Found):
```json
{
    "error": "Host not found"
}
```

### 4. Get Host Snapshots

Retrieve historical snapshots for a specific host.

**Endpoint**: `GET /api/hosts/{hostname}/snapshots/`

**Parameters**:
- `hostname` (path) - The hostname of the target system

**Response** (200 OK):
```json
[
    {
        "id": 42,
        "hostname": "server01",
        "timestamp": "2024-01-15T10:30:00Z",
        "total_processes": 150,
        "processes": [
            {
                "id": 1,
                "pid": 1,
                "name": "systemd",
                "cmdline": "/sbin/init",
                "parent_pid": null,
                "cpu_percent": 0.1,
                "memory_percent": 0.5,
                "memory_rss": 8192000,
                "memory_vms": 16384000,
                "status": "sleeping",
                "username": "root"
            }
        ]
    }
]
```

### 5. Get Latest Processes

Retrieve the latest process snapshot for a specific host.

**Endpoint**: `GET /api/hosts/{hostname}/latest/`

**Parameters**:
- `hostname` (path) - The hostname of the target system

**Response** (200 OK):
```json
{
    "id": 42,
    "hostname": "server01",
    "timestamp": "2024-01-15T10:30:00Z",
    "total_processes": 150,
    "processes": [...]
}
```

## Data Models

### Host
- `hostname` (string) - Unique identifier for the host
- `ip_address` (string, optional) - IP address of the host
- `os_info` (string, optional) - Operating system information
- `first_seen` (datetime) - When the host was first registered
- `last_seen` (datetime) - Last time data was received

### Process Snapshot
- `host` (reference) - The host this snapshot belongs to
- `timestamp` (datetime) - When the snapshot was taken
- `total_processes` (integer) - Number of processes in the snapshot

### Process
- `snapshot` (reference) - The snapshot this process belongs to
- `pid` (integer) - Process ID
- `parent_pid` (integer, optional) - Parent process ID
- `name` (string) - Process name
- `cmdline` (string, optional) - Full command line
- `username` (string, optional) - Process owner
- `status` (string, optional) - Process status
- `cpu_percent` (float) - CPU usage percentage
- `memory_percent` (float) - Memory usage percentage
- `memory_rss` (integer) - Resident Set Size in bytes
- `memory_vms` (integer) - Virtual Memory Size in bytes
- `create_time` (float, optional) - Process creation timestamp

## Error Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Data submitted successfully |
| 400 | Bad Request - Invalid data format |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Not Found - Host or resource not found |
| 500 | Internal Server Error - Server error |

## Rate Limiting

Currently no rate limiting is implemented. In production environments, consider implementing rate limiting based on:
- Requests per minute per API key
- Data volume per submission
- Host-specific limits

## Examples

### Submit Data with cURL

```bash
curl -X POST http://localhost:8000/api/submit/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: process-monitor-api-key-2024" \
  -d '{
    "hostname": "test-server",
    "ip_address": "192.168.1.100",
    "os_info": "Linux 5.4.0 x86_64",
    "processes": [
      {
        "pid": 1,
        "parent_pid": null,
        "name": "init",
        "cmdline": "/sbin/init",
        "username": "root",
        "status": "sleeping",
        "cpu_percent": 0.1,
        "memory_percent": 0.2,
        "memory_rss": 1024000,
        "memory_vms": 2048000,
        "create_time": 1640995200.0
      }
    ]
  }'
```

### Get Process Tree with cURL

```bash
curl http://localhost:8000/api/hosts/test-server/processes/
```

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Memory sizes are in bytes
- CPU percentages are floating point values (0.0 to 100.0)
- Process trees are represented as nested JSON objects
- The API maintains backward compatibility for data format changes 