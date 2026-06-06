from src import *
import os

initialize_db()
accessToken = os.getenv("PLAID_ACCESSTOKEN")

# System start up test
item_data = get_item_from_plaid(accessToken)
add_new_plaid_item_to_db(item_data)
account_data = get_accounts_from_plaid(accessToken)
add_new_plaid_account_to_db(account_data)
balance_data = get_balances_from_plaid(accessToken)
add_new_plaid_balances_to_db(balance_data)


itemid = get_item_from_db(accessToken)
accessToken = get_access_token_from_db(itemid)
next_curs, added, modified, removed = sync_transactions_from_plaid(accessToken)
update_item_cursor_in_db(itemid, next_curs)
update_transactions_in_db(added,modified,removed)
balances = get_balances_from_plaid(accessToken)
update_balances_in_db(balances)

