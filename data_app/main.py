import uvicorn
import asyncio
from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from data_app.tasks.scheduler import periodic_publisher
from data_app.consumers.consumer import start_all_consumers
from data_app.utils.logger import get_logger

logger = get_logger(__name__)
app = FastAPI(title="Data Ingestion Service")

@app.get("/")
async def read_root():
    return {"message": "Data Ingestion Service is running."}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_publisher(30))
    import threading
    threading.Thread(target=start_all_consumers, daemon=True).start()
    logger.info("Application startup completed.")

if __name__ == "__main__":
    uvicorn.run("data_app.main:app", host="0.0.0.0", port=8000, reload=True)
