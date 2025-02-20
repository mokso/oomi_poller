# Oomi-poller

Python app to periodically fetch consumption data from oomi website, and insert it to Postgres database. Also gets SPOT prices from https://spot-hinta.fi API

## configuration

Configuration is done via environment variables

| Variable | Description |
|---|----|
|OOMI_USERNAME|Username to oomi webservice |
|OOMI_PASSWORD|Password to oomi webservice |
|OOMI_METERINGPOINT_CONSUMPTION| meteringpoint code for consumption|
|OOMI_METERINGPOINT_PRODUCTION|meteringpoint code for production|
|POSTGRES_SERVER|Database server|
|POSTGRES_USER|database user|
|POSTGRES_PASSWORD|database password|
|POSTGRES_DB|database name|
