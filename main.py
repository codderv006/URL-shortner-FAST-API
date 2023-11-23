from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from databases import Database
import secrets

from pydantic import BaseModel

app = FastAPI()

# SQLite database URL
DATABASE_URL = "sqlite:///./url_shortener.db"

# Database connection setup
database = Database(DATABASE_URL)

# Table schema
CREATE_URLS_TABLE = """
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT NOT NULL,
    short_url TEXT NOT NULL
);
"""


# Execute table creation
@app.on_event("startup")
async def startup_db_client():
    await database.connect()
    await database.execute(CREATE_URLS_TABLE)


# Execute table deletion on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    await database.disconnect()


# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Endpoint to serve the index.html file
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse("static/index.html")


# Pydantic model for URL input
class URLItem(BaseModel):
    original_url: str


# Endpoint to create a shortened URL
@app.post("/shorten", response_model=dict)
async def shorten_url(url_item: URLItem):
    # Generate a unique short URL token
    short_url_token = secrets.token_urlsafe(5)

    # Insert the URL mapping into the database
    query = "INSERT INTO urls (original_url, short_url) VALUES (:original_url, :short_url)"
    values = {"original_url": url_item.original_url, "short_url": short_url_token}
    await database.execute(query, values)

    return {"short_url": f"http://127.0.0.1:8000/{short_url_token}"}


# Endpoint to redirect to the original URL
@app.get("/{short_url}")
async def redirect_url(short_url: str):
    # Retrieve the original URL from the database
    query = "SELECT original_url FROM urls WHERE short_url = :short_url"
    values = {"short_url": short_url}
    result = await database.fetch_one(query, values)

    if result is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    original_url = result["original_url"]
    return RedirectResponse(url=original_url)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
