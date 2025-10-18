# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import csv, io
from typing import Optional
from database import init_db, get_connection

init_db()

app = FastAPI(title="Product CSV Upload + Search (SQLite)")

REQUIRED_FIELDS = ["sku", "name", "brand", "mrp", "price"]

def validate_row(row: dict) -> (bool, str):
    """Return (True, "") if row is valid."""
    for f in REQUIRED_FIELDS:
        if f not in row or row[f] == "":
            return False, f"Missing required field: {f}"
    try:
        mrp = float(row["mrp"])
        price = float(row["price"])
        quantity = int(row.get("quantity", "0") or 0)
    except ValueError:
        return False, "mrp and price must be numbers; quantity must be integer if present"
    if price > mrp:
        return False, "price cannot be greater than mrp"
    if quantity < 0:
        return False, "quantity cannot be negative"
    return True, ""

def row_to_dict(row, columns):
    return {col: row[idx] for idx, col in enumerate(columns)}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV has no header row")

    valid = []
    invalid = []

    with get_connection() as conn:
        cur = conn.cursor()
        for i, raw_row in enumerate(reader, start=2):
            # normalize keys
            cleaned = {k.strip().lower(): (v.strip() if v else "") for k,v in raw_row.items() if k}

            is_valid, err = validate_row(cleaned)
            if is_valid:
                mrp = float(cleaned["mrp"])
                price = float(cleaned["price"])
                quantity = int(cleaned.get("quantity", "0") or 0)

                cur.execute('''
                    INSERT OR REPLACE INTO products
                    (sku, name, brand, color, size, mrp, price, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cleaned.get("sku"),
                    cleaned.get("name"),
                    cleaned.get("brand"),
                    cleaned.get("color") or None,
                    cleaned.get("size") or None,
                    mrp,
                    price,
                    quantity
                ))
                valid.append(cleaned)
            else:
                invalid.append({"row": i, "error": err})

        conn.commit()

    return JSONResponse({
        "stored_count": len(valid),
        "valid": valid,
        "invalid": invalid
    })

@app.get("/products")
def list_products(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=200)):
    offset = (page - 1) * limit
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT sku, name, brand, color, size, mrp, price, quantity
            FROM products
            ORDER BY id
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]

    items = [row_to_dict(r, cols) for r in rows]
    return {"page": page, "limit": limit, "items": items}

@app.get("/products/search")
def search_products(
    brand: Optional[str] = None,
    color: Optional[str] = None,
    minPrice: Optional[float] = Query(None, ge=0),
    maxPrice: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200)
):
    where_clauses = []
    params = []

    if brand:
        where_clauses.append("UPPER(brand) LIKE UPPER(?)")
        params.append(f"%{brand}%")
    if color:
        where_clauses.append("UPPER(color) LIKE UPPER(?)")
        params.append(f"%{color}%")
    if minPrice is not None:
        where_clauses.append("price >= ?")
        params.append(minPrice)
    if maxPrice is not None:
        where_clauses.append("price <= ?")
        params.append(maxPrice)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    offset = (page - 1) * limit

    sql = f'''
        SELECT sku, name, brand, color, size, mrp, price, quantity
        FROM products
        {where_sql}
        ORDER BY id
        LIMIT ? OFFSET ?
    '''
    params.extend([limit, offset])

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]

    items = [row_to_dict(r, cols) for r in rows]
    return {
        "page": page,
        "limit": limit,
        "filters": {
            "brand": brand,
            "color": color,
            "minPrice": minPrice,
            "maxPrice": maxPrice
        },
        "items": items
    }
