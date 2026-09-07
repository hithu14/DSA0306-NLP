import sqlite3


DATABASE_NAME = "complaints.db"


def create_table():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL,
            priority TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_complaint(
    complaint,
    category,
    confidence,
    priority,
    department
):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints
        (
            complaint,
            category,
            confidence,
            priority,
            department,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        complaint,
        category,
        confidence,
        priority,
        department,
        "Pending"
    ))

    conn.commit()
    conn.close()


def get_complaints():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            complaint,
            category,
            confidence,
            priority,
            department,
            status,
            created_at
        FROM complaints
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def update_complaint_status(
    complaint_id,
    new_status
):

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """, (
        new_status,
        complaint_id
    ))

    conn.commit()
    conn.close()