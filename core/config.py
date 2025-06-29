# Generic configuration
# Propably best place to keep configurations for database, redis, celery etc...


# Integration Importer Settings
SWAPI_BASE_URL = "https://swapi.dev/api"
RETRYABLE_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
CHUNK_SIZE = 100
