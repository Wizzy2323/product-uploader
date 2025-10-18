# Product CSV Upload & Search API

A FastAPI backend to **upload products via CSV**, **list products**, and **search/filter products**. Uses **SQLite** as the database.

---

## Features

1. **CSV Upload**
   - Upload a CSV file with product data.
   - Validates rows:
     - `price ≤ mrp`
     - `quantity ≥ 0`
     - Required fields: `sku`, `name`, `brand`, `mrp`, `price`
   - Stores valid rows in SQLite; reports invalid rows.

2. **List Products**
   - Paginated listing of all products.
   - Query parameters: `page`, `limit`.

3. **Search Products**
   - Filter by:
     - `brand` (case-insensitive substring)
     - `color` (case-insensitive substring)
     - `minPrice` / `maxPrice`
   - Supports pagination (`page`, `limit`).

---

## Setup

1. Clone the repository:

```bash
git clone <repo_url>
cd product-uploader
Install dependencies (pip install fastapi uvicorn)

Run command (uvicorn main:app --reload)

API endpoints (/upload-csv, /products, /search) with sample requests/responses

Optional: mention /docs for testing
