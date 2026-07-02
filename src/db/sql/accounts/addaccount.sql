INSERT INTO accounts (
    account_id, 
    item_id, 
    name,
    mask, 
    acctype, 
    subtype
) VALUES (
    :account_id, 
    :item_id, 
    :name,
    :mask, 
    :type, 
    :subtype
);