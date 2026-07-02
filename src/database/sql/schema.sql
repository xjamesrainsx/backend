PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    consent_exp TEXT,
    access_token TEXT NOT NULL UNIQUE,
    institution_id TEXT NOT NULL,
    institution_name TEXT NOT NULL,
    products TEXT NOT NULL,
    webhook TEXT,
    last_webhook TEXT,
    last_trans_update TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cursors (
    item_id TEXT PRIMARY KEY,
    next_cursor TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    "name" TEXT NOT NULL,
    mask TEXT,                      
    acctype TEXT NOT NULL,              
    subtype TEXT,                 
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS balances (
    account_id TEXT PRIMARY KEY,
    current REAL DEFAULT 0.00,
    available REAL DEFAULT 0.00,
    credlimit REAL DEFAULT 0.00,                                   
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    amount REAL NOT NULL,          
    txndate TEXT NOT NULL,            
    mername TEXT NOT NULL,             
    category TEXT DEFAULT 'Uncategorized',
    pending INTEGER DEFAULT 0,     
    pending_transaction_id TEXT,    
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_accounts_item_id ON accounts(item_id);
CREATE INDEX IF NOT EXISTS idx_balances_account_id ON balances(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(txndate);
