import logging
import sqlite3
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class BookStorage:
    def __init__(self, db_path="data/books.db"):
        self.db_path = db_path

    def add_book(self, title, price):
        connection = sqlite3.connect(self.db_path)
        try:
            sql_statement = "INSERT INTO books (title, price) VALUES (?, ?)"
            cursor = connection.execute(sql_statement, (title, price))
            book_id = cursor.lastrowid
            connection.commit()
            logger.debug(f"Added book: id={book_id}")
            return book_id
        except sqlite3.Error:
            # For a failed write, rollback() cancels uncommitted changes
            # and raise passes the error to the caller.
            connection.rollback()
            raise
        finally:
            # Always close the connection, whether the operation succeeds or fails.
            connection.close()

    def get_book(self, book_id):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            sql_statement = "SELECT id, title, price FROM books WHERE id = ?"
            row = connection.execute(sql_statement, (book_id,)).fetchone()
            logger.debug(f"Retrieved book: id={book_id}, found={row is not None}")
            if row is None:
                return None
            return dict(row)
        finally:
            connection.close()

    def list_books(self, min_price=0, limit=100):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            sql_statement = """
            SELECT id, title, price FROM books
            WHERE price >= ? ORDER BY price DESC, id ASC LIMIT ?
            """
            rows = connection.execute(sql_statement, (min_price, limit)).fetchall()
            books = [dict(row) for row in rows]
            logger.debug(f"Listed books: rows={len(books)}")
            return books
        finally:
            connection.close()


def main():
    path = Path("data") / "books.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    # Part 1: Create the database and table
    sql_statement = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price REAL NOT NULL
    )
    """
    connection.execute(sql_statement)
    connection.execute("DELETE FROM books")
    connection.commit()

    # Part 2: Insert and save
    sql_statement = "INSERT INTO books (title, price) VALUES (?, ?)"
    cursor = connection.execute(sql_statement, ("Book A", 12.5))
    book_id = cursor.lastrowid
    connection.commit()

    connection.execute(sql_statement, ("Book B", 25.0))
    connection.execute(sql_statement, ("Book C", 18.0))
    connection.commit()

    rows = [("Book D", 15.0), ("Book E", 10.0)]
    connection.executemany(sql_statement, rows)
    connection.commit()

    # Part 3: Retrieve one book
    sql_statement = "SELECT id, title, price FROM books WHERE id = ?"
    row = connection.execute(sql_statement, (book_id,)).fetchone()
    print(dict(row))

    # Preview the first n
    sql_statement = "SELECT * FROM books ORDER BY id LIMIT ?"
    rows = connection.execute(sql_statement, (5,)).fetchall()
    print([dict(row) for row in rows])

    # Filter and sort
    sql_statement = """
    SELECT title, price FROM books
    WHERE price >= ? ORDER BY price DESC LIMIT ?
    """
    rows = connection.execute(sql_statement, (15, 2)).fetchall()
    print([dict(row) for row in rows])

    # Part 4: Total count
    sql_statement = "SELECT COUNT(*) AS total FROM books"
    row = connection.execute(sql_statement).fetchone()
    print(row["total"])

    # Update
    sql_statement = "UPDATE books SET price = ? WHERE id = ?"
    connection.execute(sql_statement, (13.0, book_id))
    connection.commit()

    # Check
    sql_statement = "SELECT price FROM books WHERE id = ?"
    row = connection.execute(sql_statement, (book_id,)).fetchone()
    print(row["price"])  # 13.0

    # Delete
    sql_statement = "DELETE FROM books WHERE id = ?"
    connection.execute(sql_statement, (book_id,))
    connection.commit()

    # Check
    sql_statement = "SELECT * FROM books WHERE id = ?"
    row = connection.execute(sql_statement, (book_id,)).fetchone()
    print(row)  # None

    connection.close()

    # Try It Yourself
    storage = BookStorage()
    book_id = storage.add_book("Book A", 12.5)
    logger.info(f"Added book: id={book_id}")

    print(storage.get_book(book_id)["title"])
    print(storage.get_book(book_id)["price"])
    books = storage.list_books(min_price=15, limit=2)
    print([(book["title"], book["price"]) for book in books])


if __name__ == "__main__":
    main()
