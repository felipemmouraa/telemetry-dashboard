import io
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from supabase import create_client
from data_app.config import settings
from data_app.utils.logger import get_logger
from data_app.metrics.metrics import RAW_DATA_UPLOAD_SUCCESS, RAW_DATA_UPLOAD_FAILURE, RAW_DATA_UPLOAD_DURATION

logger = get_logger(__name__)

supabase = create_client(settings.supabase_url, settings.supabase_key)

def save_raw_data(data: dict) -> None:
    """
    Saves raw data into a parquet file and uploads it to Supabase Storage.
    Inserts metadata into the parquet_metadata table.
    """
    with RAW_DATA_UPLOAD_DURATION.time():
        try:
            source = data.get("source", "default")
            df = pd.DataFrame([data.get("data", {})])
            table = pa.Table.from_pandas(df)

            buffer = io.BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)

            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            file_path = f"{source}/raw_{timestamp}.parquet"
            bucket_name = settings.supabase_bucket  

            response = supabase.storage.from_(bucket_name).upload(
                file_path,
                buffer.getvalue(), 
                file_options={"content-type": "application/octet-stream"}
            )

            classification_id = get_classification_for_source(source)

            try:
                logger.info("Attempting to insert metadata into parquet_metadata table")
                response = supabase.table("logs_raw_data").insert({
                    "bucket": bucket_name,
                    "file_path": file_path,
                    "classification_id": classification_id,
                }).execute()
                logger.info(f"Supabase insert response: {response}")
            except Exception as e:
                logger.info(f"Error inserting metadata: {str(e)}")

            # Increment the success counter if all operations pass
            RAW_DATA_UPLOAD_SUCCESS.inc()
            logger.info(f"Raw data uploaded to bucket {bucket_name} as {file_path}")

        except Exception as e:
            # Increment the failure counter in case of errors
            RAW_DATA_UPLOAD_FAILURE.inc()
            logger.error(f"Error saving raw data: {str(e)}")
            raise e

def get_classification_for_source(source: str) -> int:
    """
    Returns classification ID based on the data source.
    """
    classifications = {
        "vehicles": 1,  
        "status": 1,  
        "results": 1,  
        "fails": 1   
    }
    return classifications.get(source, 1)  

