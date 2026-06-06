INSERT INTO balances (
    account_id,
    current,
    available,
    credlimit
) VALUES (
    :account_id,
    :current,
    :available,
    :limit
);