
        
def conn_execute_script(connection, script, data):
    try:
        with connection as conn:
            cur = conn.cursor()
        with open(script, 'r') as f:
            sql = f.read()
            cur.execute(sql, data)
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Database connection error: {e}")
    finally:
        cur.close()
        conn.close()

def update_item_webhook(item_id,webhook):
    return