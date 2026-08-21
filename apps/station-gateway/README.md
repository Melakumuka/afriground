# AfriGround Station Gateway

The local edge agent for AfriGround, responsible for caching profiles, pulling job assignments, interfacing with the local ground station hardware (Zodiac PFM730, ACU, HDR), and providing an operator UI for readiness checks.

## Setup

1. Configure `.env` in this directory:
```env
STATION_ID=your-station-uuid
AGENT_ID=gateway-01
CLOUD_API_URL=http://localhost:8000
CLOUD_API_KEY=your-api-key
ADAPTER_TYPE=mock_zodiac_mcs
```

2. Run the Gateway:
```bash
./run.sh
```
Or with python directly:
```bash
uvicorn main:app --reload --port 8080
```

3. Open the Dashboard:
Navigate to `http://localhost:8080/` to view the local Station Gateway UI.
