CREATE TABLE invoices (
  id INTEGER PRIMARY KEY,
  number TEXT NOT NULL,
  total_cents INTEGER NOT NULL
);

INSERT INTO invoices (number, total_cents) VALUES ('FV/DEMO/001', 29900);

