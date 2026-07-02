# config.py
DB_DIR = "src/database/"
SQL_DIR = DB_DIR + "sql/"

# Comments below name the function where the sql command is used.

# initialize_db
DB_FILE = "src/database/plaid_finances.db"
SCHEMA_FILE = SQL_DIR + "schema.sql"

# update_transactions_in_database
SYNCADDSQL = SQL_DIR + "transactions/syncadded.sql"
SYNCMODSQL = SQL_DIR + "transactions/syncmodified.sql"
SYNCRMVSQL = SQL_DIR + "transactions/syncremoved.sql"

# add_new_plaid_item
NEWITEMSQL = SQL_DIR + "items/additem.sql"
SETCURSORSQL = SQL_DIR + "cursors/setupcursor.sql"

# get_item_cursor_from_db
GETCURSORSQL = SQL_DIR + "cursors/getcursor.sql"

# get_access_token_from_db
GETTOKENSQL = SQL_DIR + "accesstokens/getacctoken.sql"

# get_item_from_db
GETITEMSQL = SQL_DIR + "items/getitem.sql"

# add_new_plaid_account
ADDACCOUNTSQL = SQL_DIR + "accounts/addaccount.sql"

# update_item_cursor_in_db
UPDATECURSORSQL = SQL_DIR + "cursors/updatecursor.sql"

# update_account_balances_in__db
UPDATEBALSQL = SQL_DIR + "balances/updatebalances.sql"

# get_balance_from_db
GETBALANCESQL  = SQL_DIR + "balances/getbalances.sql"

# add_new_plaid_balance
ADDBALANCESQL= SQL_DIR + "balances/addbalances.sql"