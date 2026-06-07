from .config import *
import sqlite3


def exe_script(script: str, data: str | list | dict | None, multi: bool, cur: sqlite3.Cursor):
    
    try:
        with open(script, 'r') as f:
            sql = f.read()
            if multi:
                cur.executemany(sql, data if data else None)
            else:
                cur.execute(sql, data if data else None)
        return True
    except Exception as e:
        return e

def initialize_db():
        print("Attempting database initialization.")
        exe_script(SCHEMA_FILE)
        print("   ✅ Database tables and performance indexes created successfully.")

def add_new_plaid_item_to_db(item_data):
    ''' Connect to SQLite and execute the parameterized INSERT statement.
    Call GetItemFromPlaid first to load item_data. '''
    try:
        print("Attempting to add item to database and create cursor tracker")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(NEWITEMSQL, 'r') as f:
                additesql = f.read()
            cur.execute(additesql, item_data)
            with open(SETCURSORSQL, 'r') as f:
                setcursql = f.read()            
            cur.execute(setcursql, item_data)
            print("   💾 Item successfully added to database.")
            conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"   ❌ Duplicate or constraint violation: {e}")
    finally:
        cur.close()
        conn.close()

def add_new_plaid_account_to_db(account_data):
    try:
        print("Attempting to add accounts to database")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(ADDACCOUNTSQL, 'r') as f:
                addaccsql = f.read()
            cur.executemany(addaccsql, account_data)
            print("   💾 Accounts successfully added to database.")
            conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"   ❌ Duplicate or constraint violation: {e}")
    finally:
        cur.close()
        conn.close() 

def add_new_plaid_balances_to_db(balance_data):
    try:
        print("Attempting to add balances to database")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(ADDBALANCESQL, 'r') as f:
                addbalsql = f.read()
            cur.executemany(addbalsql, balance_data)
            print("   💾 Balances successfully added to database.")
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Database loading error: {e}")
    finally:
        cur.close()
        conn.close() 

def get_access_token_from_db(item_id):
    """Retrieves the access token linked to the webhook's item_id."""
    try:
        print("Attempting to retrieve access token from database.")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(GETTOKENSQL, 'r') as f:
                getacctknsql = f.read()
            cur.execute(getacctknsql, (item_id,))
            row = cur.fetchone()
        if row:
            print("   ✅ Successfully retrieved access_token from database.")
            return row[0]
        else: 
            print("   ❌ No matches returned from database.")
            return None
    except Exception as e:
            print(f"   ❌ Database Query Error: {e}")
    finally:
        cur.close()
        conn.close()

def get_item_from_db(access_token):
    try:
        print("Attempting to get item from database.")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(GETITEMSQL, 'r') as f:
                getitemsql = f.read()
            cur.execute(getitemsql, (access_token,))
            row = cur.fetchone()
        if row:
            print("   ✅ Successfully retrieved item")
            return row[0]
        else: 
            print("   ❌ No matches returned from database.")
            return None
    except Exception as e:
            print(f"   ❌ Database Query Error: {e}")
    finally:
        cur.close()
        conn.close()

def get_item_cursor_from_db(item_id):
    try:
        print("Attempting to get next cursor from database.")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(GETCURSORSQL, 'r') as f:
                getcursql = f.read()                
            cur.execute(getcursql, (item_id,))
            row = cur.fetchone()
        if row:
            print("   ✅ Successfully retrieved cursor")
            return row[0]
        else: 
            print("   ❌ No matches returned from database.")
            return None
    except Exception as e:
            print(f"   ❌ Database Query Error: {e}")
    finally:
        cur.close()
        conn.close()

def get_balance_from_db(account_id):
    try:
        print("Attempting to get balance from database")
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(GETBALANCESQL, 'r') as f:
                getbalsql = f.read()                
            cur.execute(getbalsql, (account_id,))
            row = cur.fetchone()
        if row:
            print("   ✅ Successfully retrieved balances")
            return row[0]
        else: 
            print("   ❌ No matches returned from database.")
            return None
    except Exception as e:
            print(f"   ❌ Database Query Error: {e}")
    finally:
        cur.close()
        conn.close()

def update_item_cursor_in_db(item_id, next_cursor):
    try:
        print("Attempting to update next_cursor in database.")
        cursordata = next_cursor, item_id
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            with open(UPDATECURSORSQL, 'r') as f:
                    updcursorsql = f.read()
            cur.execute(updcursorsql, cursordata)
            print("   💾 Successfully updated next cursor.")
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Database Sync Error: {e}")
    finally:
        cur.close()
        conn.close()

def update_balances_in_db(balances=[]):
        try: 
            with sqlite3.connect(DB_FILE) as conn:
                cur = conn.cursor()
                if balances:
                    print("Attempting to update balances in database.")  
                    with open(UPDATEBALSQL, 'r') as f:
                        balupdsql = f.read()
                    cur.executemany(balupdsql, balances)
                    print("   💾 Successfully updated balances.")
                    conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Database Sync Error: {e}")
        finally:
            cur.close()
            conn.close()

def update_transactions_in_db(added=[], modified=[], removed=[]):

    """Updates database after a call to transactions/sync"""

    try: 
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            if added:
                print("Attempting to update added transactions")
                with open(SYNCADDSQL, 'r') as f:
                    syncaddsql = f.read()
                cur.executemany(syncaddsql, added)
                print(f"   💾 Added {len(added)} new transactions.")
            if modified:
                print("Attempting to update modified transactions")
                with open(SYNCMODSQL, 'r') as f:
                    syncmodsql = f.read()
                cur.executemany(syncmodsql, modified)
                print(f"   🔄 Modified {len(modified)} existing transactions.")
            if removed:
                print("Attempting to update removed transactions")
                with open(SYNCRMVSQL, 'r') as f:
                    syncrmvsql = f.read()
                cur.executemany(syncrmvsql, removed)
                print(f"   🗑️ Removed {len(removed)} transactions.")
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Database Sync Error: {e}")
    finally:
        cur.close()
        conn.close()