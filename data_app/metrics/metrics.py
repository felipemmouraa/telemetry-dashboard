from prometheus_client import Counter, Histogram

# Counter for successful raw data uploads
RAW_DATA_UPLOAD_SUCCESS = Counter(
    'raw_data_upload_success_total',
    'Total number of successful raw data uploads'
)

# Counter for failed raw data uploads
RAW_DATA_UPLOAD_FAILURE = Counter(
    'raw_data_upload_failure_total',
    'Total number of failed raw data uploads'
)

# Histogram to measure the duration of raw data uploads (in seconds)
RAW_DATA_UPLOAD_DURATION = Histogram(
    'raw_data_upload_duration_seconds',
    'Time taken for raw data uploads'
)
