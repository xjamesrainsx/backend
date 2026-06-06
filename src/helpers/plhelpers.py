from plaid.api import plaid_api
import json
import plaid
import os

def create_client_plaid():

    """ Creates a plaid api client with .env configured id, 
    secret and environment. You can also set the environment 
    when calling the function. Production or Sandbox """

    print("Attempting to create plaid client.")

    # Get client id and key from .env file. 
    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")

    # Get environment selection from .env file.
    if os.getenv("PLAID_ENV") == "Production":
        host_selection = plaid.Environment.Production
    else:
        host_selection = plaid.Environment.Sandbox

    # Set up the client configured variables.
    configuration = plaid.Configuration(
        host = host_selection,
        api_key = {
            'clientId': client_id,
            'secret': secret,
        }
    )

    #Create and initialize the client.
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    
    print("   ✅ Plaid client successfully created.")

    #Send client back.
    return client

def get_item_from_plaid(access_token):

    client = create_client_plaid()

    print("Attempting to get item from Plaid")

    req = {"access_token": access_token}
    res = client.item_get(req)

    print("   ✅ Successfully retrieved item data")

    return {
        "item_id": res.item.item_id,
        "access_token": access_token,
        "institution_id": res.item.institution_id,
        "institution_name": res.item.institution_name,
        "products": json.dumps([str(p) for p in res.item.products]),
        "webhook": res.item.webhook if res.item.webhook else None,
        "last_webhook": to_iso(res.status.last_webhook),
        "consent_exp": to_iso(res.item.consent_expiration_time),
        "last_trans_update": to_iso(res.status.transactions.last_successful_update),
        "created_at": to_iso(res.item.created_at)
    }

def get_accounts_from_plaid(access_token):

    client = create_client_plaid()

    print("Attempting to get accounts from Plaid")

    req = {"access_token": access_token}
    res = client.accounts_get(req)

    accounts = []
    for acc in res.accounts:
       accounts.append((
            acc['account_id'],
            res.item['item_id'],
            acc['name'], 
            acc['mask'],
            to_str(acc['type']),
            to_str(acc['subtype'])
        ))
       
    print("   ✅ Successfully retrieved account data")

    return accounts

def get_balances_from_plaid(access_token):

    client = create_client_plaid()

    print("Attempting to get balances from Plaid")

    req = {"access_token": access_token}
    res = client.accounts_balance_get(req)

    balances = []
    for acc in res.accounts:
        balances.append((
            acc['account_id'],
            acc['balances']['current'],
            acc['balances']['available'],
            acc['balances']['limit']    
        ))

    print("   ✅ Successfully retrieved balances data")

    return balances

def sync_transactions_from_plaid(access_token,next_cursor=None):

    client = create_client_plaid()
    print("Attempting to get transactions from Plaid")
    has_more = True
    added = []
    modified = []
    removed = []

    while has_more:

        req = {"access_token": access_token,
               "count": 100,
               "cursor": next_cursor}
        res = client.transactions_sync(req)

        if res.added:
            for txn in res.added:
                added.append((
                    txn['transaction_id'], 
                    txn['account_id'], 
                    txn['amount'],
                    to_iso(txn['date']),
                    txn['name'],
                    to_str(txn.personal_finance_category['detailed']),
                    booltoint(txn['pending']),
                    txn['pending_transaction_id'],
                ))
            
        if res.modified:
            for txn in res.modified:
                modified.append((
                    txn['transaction_id'], 
                    txn['account_id'], 
                    txn['amount'],
                    to_iso(txn['date']),
                    txn['name'],
                    to_str(txn.personal_finance_category['detailed']),
                    booltoint(txn['pending']),
                    txn['pending_transaction_id'],
                ))

        if res.removed:
            for txn in res.removed:
                removed.append(to_str(txn))
        next_cursor = res['next_cursor']
        has_more = res['has_more']
        if has_more:
            print("      Retrieving additional transactions")
    print(f"   ✅ Successfully retrieved transaction data. ")
    print(f"      Added Transactions:     {len(added)} ")
    print(f"      Modified Transactions:  {len(modified)}")
    print(f"      Removed Transactions:   {len(removed)}")

    return next_cursor, added, modified, removed

def to_iso(dt):
    return dt.isoformat() if dt else None

def to_str(v):
    return str(v) if v else None

def booltoint(bl):
    if bl:
        return 1
    else: 
        return 0