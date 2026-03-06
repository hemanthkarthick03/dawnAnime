from fastapi import FastAPI
from sqlalchemy import text
from db.engine import engine

app = FastAPI()

# Health check endpoint
@app.get("/health")
async def db_health():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return {"status" : "connected"}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)