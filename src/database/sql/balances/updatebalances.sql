UPDATE balances
SET current= ?,
    available = ?,
    credlimit = ?
WHERE account_id = ?