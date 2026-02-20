"""SQLite application — in-memory SQLite database MCP server with dummy data."""

from __future__ import annotations

import sqlite3

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Schema and seed data
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    email     TEXT    NOT NULL UNIQUE,
    role      TEXT    NOT NULL DEFAULT 'user',
    team      TEXT,
    joined_at TEXT    NOT NULL,
    active    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       REAL    NOT NULL,
    stock       INTEGER NOT NULL DEFAULT 0,
    sku         TEXT    NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL DEFAULT 1,
    total       REAL    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    created_at  TEXT    NOT NULL
);

CREATE TABLE events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name  TEXT NOT NULL,
    action      TEXT NOT NULL,
    row_id      INTEGER,
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_SEED = """
-- Users
INSERT INTO users (name, email, role, team, joined_at) VALUES
    ('Alice Chen',   'alice@example.com',   'admin',    'Platform',  '2022-03-15'),
    ('Bob Smith',    'bob@example.com',     'engineer', 'Backend',   '2023-01-09'),
    ('Carol Jones',  'carol@example.com',   'engineer', 'Frontend',  '2023-06-20'),
    ('Dave Park',    'dave@example.com',    'engineer', 'Backend',   '2023-11-01'),
    ('Eve Kumar',    'eve@example.com',     'manager',  'Product',   '2021-08-14'),
    ('Frank Diaz',   'frank@example.com',   'user',     NULL,        '2024-01-30'),
    ('Grace Lee',    'grace@example.com',   'user',     NULL,        '2024-05-12'),
    ('Hiro Yamamoto','hiro@example.com',    'engineer', 'Platform',  '2024-09-03');

-- Products
INSERT INTO products (name, category, price, stock, sku, description) VALUES
    ('Wireless Headphones',    'Electronics',  89.99,  142, 'ELEC-001', 'Over-ear noise-cancelling headphones'),
    ('Mechanical Keyboard',    'Electronics', 149.99,   58, 'ELEC-002', 'TKL layout, Cherry MX switches'),
    ('4K Webcam',              'Electronics',  79.99,   33, 'ELEC-003', '4K resolution, auto-focus, ring light'),
    ('Standing Desk',          'Furniture',   499.99,   12, 'FURN-001', 'Electric height-adjustable, 60x30 inch'),
    ('Ergonomic Chair',        'Furniture',   389.99,   19, 'FURN-002', 'Lumbar support, adjustable armrests'),
    ('Monitor Arm',            'Furniture',    59.99,   87, 'FURN-003', 'Single monitor, VESA compatible'),
    ('Python Crash Course',    'Books',        35.99,  201, 'BOOK-001', 'Third edition, beginner programming book'),
    ('Designing Data-Intensive Applications', 'Books', 55.99, 78, 'BOOK-002', 'Distributed systems and databases'),
    ('The Pragmatic Programmer','Books',       44.99,   95, 'BOOK-003', '20th anniversary edition'),
    ('USB-C Hub 10-in-1',      'Electronics',  49.99,  215, 'ELEC-004', 'HDMI 4K, SD card, USB-A/C ports'),
    ('Laptop Sleeve 15"',      'Accessories',  29.99,  310, 'ACC-001',  'Neoprene, water-resistant'),
    ('Blue Light Glasses',     'Accessories',  24.99,  188, 'ACC-002',  'Anti-glare, UV400 protection');

-- Orders
INSERT INTO orders (user_id, product_id, quantity, total, status, created_at) VALUES
    (1, 4,  1, 499.99, 'delivered',  '2026-01-05'),
    (1, 5,  1, 389.99, 'delivered',  '2026-01-05'),
    (2, 1,  1,  89.99, 'delivered',  '2026-01-12'),
    (2, 2,  1, 149.99, 'delivered',  '2026-01-12'),
    (3, 3,  1,  79.99, 'shipped',    '2026-02-01'),
    (3, 10, 1,  49.99, 'shipped',    '2026-02-01'),
    (4, 7,  1,  35.99, 'delivered',  '2026-01-20'),
    (4, 8,  1,  55.99, 'delivered',  '2026-01-20'),
    (5, 9,  2,  89.98, 'delivered',  '2026-01-08'),
    (6, 11, 1,  29.99, 'pending',    '2026-02-18'),
    (7, 12, 2,  49.98, 'processing', '2026-02-19'),
    (8, 1,  1,  89.99, 'processing', '2026-02-20'),
    (8, 10, 1,  49.99, 'processing', '2026-02-20'),
    (2, 6,  2, 119.98, 'pending',    '2026-02-20'),
    (1, 8,  1,  55.99, 'pending',    '2026-02-20');
"""


def _create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.executescript(_SEED)
    conn.commit()
    return conn


# Module-level shared in-memory connection (single instance per server lifecycle)
_CONN: sqlite3.Connection = _create_connection()

# Whitelist of allowed tables for DML operations
_ALLOWED_TABLES = {"users", "products", "orders"}

# Read-only query keywords (SELECT and CTEs only)
_WRITE_KEYWORDS = {"insert", "update", "delete", "drop", "create", "alter", "truncate", "replace"}


def _is_read_only(sql: str) -> bool:
    first_word = sql.strip().split()[0].lower() if sql.strip() else ""
    return first_word not in _WRITE_KEYWORDS


class SQLiteApp:
    """In-memory SQLite database with users, products, and orders tables."""

    def __init__(self) -> None:
        self.name = "sqlite"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def query(self, sql: str, params: list | None = None) -> dict:
        """Execute a read-only SQL SELECT query and return the results.

        The database contains three tables:
        - **users** (id, name, email, role, team, joined_at, active)
        - **products** (id, name, category, price, stock, sku, description)
        - **orders** (id, user_id, product_id, quantity, total, status, created_at)

        Args:
            sql: A SQL SELECT statement to execute. JOINs, WHERE, GROUP BY, ORDER BY,
                 subqueries, and CTEs are all supported. Write statements (INSERT, UPDATE,
                 DELETE, etc.) are rejected.
            params: Optional list of positional parameters for prepared statements
                    (e.g. ['alice@example.com'] for 'WHERE email = ?').

        Returns:
            dict: Contains 'rows' (list of row dicts) and 'row_count'. Returns error
                  dict on SQL error or if a write statement is attempted.

        Tags:
            sqlite, sql, query, select, database, read
        """
        if not _is_read_only(sql):
            return {"error": "Only SELECT queries are allowed via query(). Use insert/update/delete tools."}
        try:
            cursor = _CONN.execute(sql, params or [])
            rows = [dict(row) for row in cursor.fetchall()]
            return {"rows": rows, "row_count": len(rows)}
        except sqlite3.Error as exc:
            return {"error": f"SQL error: {exc}"}

    def describe_table(self, table_name: str) -> dict:
        """Get the schema (column names and types) for a specific table.

        Args:
            table_name: One of: users, products, orders.

        Returns:
            dict: Contains 'table', 'columns' (list of name/type/nullable dicts),
                  and 'row_count'. Returns error if table not found.

        Tags:
            sqlite, schema, table, columns, describe, database
        """
        if table_name not in _ALLOWED_TABLES:
            return {"error": f"Unknown table '{table_name}'. Available: {', '.join(sorted(_ALLOWED_TABLES))}"}
        try:
            cursor = _CONN.execute(f"PRAGMA table_info({table_name})")  # noqa: S608
            columns = [
                {"name": row["name"], "type": row["type"], "nullable": not row["notnull"]} for row in cursor.fetchall()
            ]
            count_row = _CONN.execute(f"SELECT COUNT(*) AS cnt FROM {table_name}").fetchone()  # noqa: S608
            return {"table": table_name, "columns": columns, "row_count": count_row["cnt"]}
        except sqlite3.Error as exc:
            return {"error": f"SQL error: {exc}"}

    def list_tables(self) -> list[dict]:
        """List all tables in the database with their row counts.

        Returns:
            list[dict]: Each entry has 'table' name and 'row_count'.

        Tags:
            sqlite, tables, list, schema, database
        """
        result = []
        for table in sorted(_ALLOWED_TABLES):
            row = _CONN.execute(f"SELECT COUNT(*) AS cnt FROM {table}").fetchone()  # noqa: S608
            result.append({"table": table, "row_count": row["cnt"]})
        return result

    def insert(self, table_name: str, row: dict) -> dict:
        """Insert a new row into a table.

        Args:
            table_name: One of: users, products, orders.
            row: Dict of column name → value to insert. The 'id' column is
                 auto-assigned; do not include it.

        Returns:
            dict: Contains 'table', 'inserted_id', and 'status'. Returns error on failure.

        Tags:
            sqlite, insert, write, database, create, row
        """
        if table_name not in _ALLOWED_TABLES:
            return {"error": f"Unknown table '{table_name}'."}
        if not row:
            return {"error": "Row dict is empty."}
        cols = ", ".join(row.keys())
        placeholders = ", ".join("?" * len(row))
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"  # noqa: S608
        try:
            cursor = _CONN.execute(sql, list(row.values()))
            _CONN.commit()
            return {"table": table_name, "inserted_id": cursor.lastrowid, "status": "inserted"}
        except sqlite3.Error as exc:
            return {"error": f"SQL error: {exc}"}

    def update(self, table_name: str, row_id: int, updates: dict) -> dict:
        """Update specific columns of a row identified by its id.

        Args:
            table_name: One of: users, products, orders.
            row_id: The integer primary key of the row to update.
            updates: Dict of column name → new value.

        Returns:
            dict: Contains 'table', 'row_id', 'rows_affected', and 'status'. Returns error on failure.

        Tags:
            sqlite, update, write, database, modify, row
        """
        if table_name not in _ALLOWED_TABLES:
            return {"error": f"Unknown table '{table_name}'."}
        if not updates:
            return {"error": "Updates dict is empty."}
        set_clause = ", ".join(f"{col} = ?" for col in updates.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"  # noqa: S608
        try:
            cursor = _CONN.execute(sql, [*updates.values(), row_id])
            _CONN.commit()
            return {"table": table_name, "row_id": row_id, "rows_affected": cursor.rowcount, "status": "updated"}
        except sqlite3.Error as exc:
            return {"error": f"SQL error: {exc}"}

    def delete(self, table_name: str, row_id: int) -> dict:
        """Delete a row from a table by its id.

        Args:
            table_name: One of: users, products, orders.
            row_id: The integer primary key of the row to delete.

        Returns:
            dict: Contains 'table', 'row_id', 'rows_affected', and 'status'. Returns error on failure.

        Tags:
            sqlite, delete, remove, database, row
        """
        if table_name not in _ALLOWED_TABLES:
            return {"error": f"Unknown table '{table_name}'."}
        sql = f"DELETE FROM {table_name} WHERE id = ?"  # noqa: S608
        try:
            cursor = _CONN.execute(sql, [row_id])
            _CONN.commit()
            affected = cursor.rowcount
            return {
                "table": table_name,
                "row_id": row_id,
                "rows_affected": affected,
                "status": "deleted" if affected else "not_found",
            }
        except sqlite3.Error as exc:
            return {"error": f"SQL error: {exc}"}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [
            self.query,
            self.describe_table,
            self.list_tables,
            self.insert,
            self.update,
            self.delete,
        ]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = SQLiteApp()
    server = app.create_mcp_server()
    server.run()
