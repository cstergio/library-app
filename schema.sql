CREATE TABLE IF NOT EXISTS books (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    title   TEXT NOT NULL,
    author  TEXT NOT NULL,
    year    INTEGER,
    isbn    TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS members (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    email   TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS loans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL,
    member_id   INTEGER NOT NULL,
    loan_date   TEXT NOT NULL,
    due_date    TEXT NOT NULL,
    return_date TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (member_id) REFERENCES members(id)
);