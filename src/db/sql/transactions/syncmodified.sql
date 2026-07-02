UPDATE transactions 
SET account_id = ?, 
    txndate = ?, 
    amount = ?, 
    mername = ?, 
    category = ?,
    pending = ?, 
    pending_transactionid = ?
WHERE transaction_id = ?