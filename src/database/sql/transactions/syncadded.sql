INSERT INTO transactions (
    transaction_id, 
    account_id, 
    amount, 
    txndate, 
    mername, 
    category,
    pending, 
    pending_transaction_id
) VALUES (
    :transaction_id, 
    :account_id, 
    :amount, 
    :date, 
    :name, 
    :detailed, 
    :pending, 
    :pending_transaction_id
);