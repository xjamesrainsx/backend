from src import *
from flask import Flask, request, jsonify
from waitress import serve
import threading

app = Flask(__name__)

# --- Flask Plaid Webhook Handler ---

def process_webhook(data):
        
    webhook_type = data['webhook_type']
    webhook_code = data['webhook_code']
    item_id = data['item_id']

    print(f"\n [Plaid Webhook Received]")
    print(f"   ├─ Type: {webhook_type}")
    print(f"   ├─ Code: {webhook_code}")
    print(f"   └─ Item ID: {item_id}")
    print(f"   └─ Payload: {data}")

    if webhook_type == "TRANSACTIONS" and webhook_code == "SYNC_UPDATES_AVAILABLE":
        print(f"   ⚡ Initializing database sync...")
        access_token = get_access_token_from_db(item_id)
        lastcur = get_item_cursor_from_db(item_id)
        if access_token:
            next_cursor, added, modified, removed = sync_transactions_from_plaid(access_token, lastcur if lastcur else '')
            update_item_cursor_in_db(next_cursor,item_id)
            update_transactions_in_db(added,modified,removed)
        else:
            print(f"   ⚠️ Sync Aborted: No access token found for Item ID {item_id}")

@app.route('/webhook', methods=['POST'])
def webhooks():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    
    threading.Thread(target=process_webhook, args=(data,)).start()

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8001)
    print("Server has started.")
