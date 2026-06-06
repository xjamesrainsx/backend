INSERT INTO items (
    item_id, 
    access_token, 
    institution_id, 
    institution_name, 
    products, 
    webhook, 
    last_webhook, 
    consent_exp,
    last_trans_update, 
    created_at
) VALUES (
    :item_id, 
    :access_token, 
    :institution_id, 
    :institution_name, 
    :products, 
    :webhook, 
    :last_webhook, 
    :consent_exp,
    :last_trans_update, 
    :created_at
)