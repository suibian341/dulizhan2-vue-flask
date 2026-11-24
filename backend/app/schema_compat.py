from sqlalchemy import text

from .extensions import db


PRODUCT_COMPAT_COLUMNS = {
    "vendor_id": "VARCHAR(40) NULL",
    "submitted_at": "DATETIME NULL",
    "reviewed_at": "DATETIME NULL",
    "reviewed_by_id": "VARCHAR(40) NULL",
    "rejection_reason": "TEXT NULL",
    "trade_info": "JSON NULL",
}

INQUIRY_COMPAT_COLUMNS = {
    "user_id": "VARCHAR(40) NULL",
}

INQUIRY_MESSAGE_COMPAT_COLUMNS = {
    "sender_id": "VARCHAR(40) NULL",
}

QUOTE_ITEM_COMPAT_COLUMNS = {
    "options": "JSON NULL",
}


def table_columns(table_name):
    rows = db.session.execute(
        text(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
            """
        ),
        {"table_name": table_name},
    ).fetchall()
    return {row[0] for row in rows}


def ensure_columns(table_name, columns):
    existing = table_columns(table_name)
    for column, ddl in columns.items():
        if column not in existing:
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column} {ddl}"))


def ensure_index(table_name, index_name, ddl):
    rows = db.session.execute(
        text(
            """
            SELECT INDEX_NAME
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND INDEX_NAME = :index_name
            """
        ),
        {"table_name": table_name, "index_name": index_name},
    ).fetchall()
    if not rows:
        db.session.execute(text(ddl))


def ensure_quote_tables():
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS quotes (
              id VARCHAR(40) NOT NULL PRIMARY KEY,
              inquiry_id VARCHAR(40) NOT NULL,
              total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
              valid_until DATETIME NOT NULL,
              notes TEXT NULL,
              created_at DATETIME NOT NULL,
              updated_at DATETIME NOT NULL,
              INDEX ix_quotes_inquiry_id (inquiry_id),
              CONSTRAINT fk_quotes_inquiry_id
                FOREIGN KEY (inquiry_id) REFERENCES inquiries(id)
                ON DELETE CASCADE
            )
            """
        )
    )
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS quote_items (
              id VARCHAR(40) NOT NULL PRIMARY KEY,
              quote_id VARCHAR(40) NOT NULL,
              product_id VARCHAR(40) NULL,
              variant_id VARCHAR(40) NULL,
              name VARCHAR(255) NOT NULL,
              quantity INT NOT NULL DEFAULT 1,
              unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
              total_price DECIMAL(10,2) NOT NULL DEFAULT 0,
              options JSON NULL,
              INDEX ix_quote_items_quote_id (quote_id),
              CONSTRAINT fk_quote_items_quote_id
                FOREIGN KEY (quote_id) REFERENCES quotes(id)
                ON DELETE CASCADE
            )
            """
        )
    )


def ensure_compatible_schema():
    """Add columns introduced after the initial scaffold when using db.create_all()."""
    dialect = db.engine.dialect.name
    if dialect not in {"mysql", "mariadb"}:
        return

    ensure_columns("products", PRODUCT_COMPAT_COLUMNS)
    ensure_columns("inquiries", INQUIRY_COMPAT_COLUMNS)
    ensure_columns("inquiry_messages", INQUIRY_MESSAGE_COMPAT_COLUMNS)
    ensure_quote_tables()
    ensure_columns("quote_items", QUOTE_ITEM_COMPAT_COLUMNS)
    ensure_index("inquiries", "ix_inquiries_user_id", "CREATE INDEX ix_inquiries_user_id ON inquiries (user_id)")
    ensure_index("inquiry_messages", "ix_inquiry_messages_sender_id", "CREATE INDEX ix_inquiry_messages_sender_id ON inquiry_messages (sender_id)")
    db.session.commit()
