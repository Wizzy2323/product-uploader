# Product CSV Upload & Search API

A **FastAPI** backend to upload products via CSV, list products, and search/filter products. Uses **SQLite** as the database.

---

## Features

### CSV Upload
- Upload a CSV file with product data.
- Validates rows:
  - `price ≤ mrp`
  - `quantity ≥ 0`
- Required fields: `sku`, `name`, `brand`, `mrp`, `price`
- Stores valid rows in SQLite; reports invalid rows.

### List Products
- Paginated listing of all products.
- Query parameters: `page`, `limit`.

### Search Products
- Filter by:
  - `brand` (case-insensitive substring)
  - `color` (case-insensitive substring)
  - `minPrice` / `maxPrice`
- Supports pagination (`page`, `limit`).

---

## Setup

1. **Clone the repository:**
```bash
git clone <repo_url>
cd product-uploader
```
2. **Install dependencies:**
```bash
pip install fastapi uvicorn
```
3. **Run the Api:**
```bash
uvicorn main:app --reload
```
4.**Access the API at: http://127.0.0.1:8000**

5.**Interactive API docs: http://127.0.0.1:8000/docs**
