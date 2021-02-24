CREATE TABLE transactions (transaction_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, amount INTEGER,
	stock TEXT NOT NULL, price INTEGER NOT NULL, timestamp TIMESTAMP, transaction_type TEXT NOT NULL
	FOREIGN KEY(user_id) REFERENCES users (id));
	

CREATE TABLE stock_owners (id INTEGER PRIMARY KEY, stock TEXT NOT NULL, amount INTEGER,
	user_id INTEGER NOT NULL, 
	FOREIGN KEY(user_id) REFERENCES users (id));
CREATE UNIQUE INDEX id ON stock_owners(id);
