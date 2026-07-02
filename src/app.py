from src import *
from flask import Flask, request, jsonify
from waitress import serve

app = Flask(__name__)

# --- Flask Plaid Webhook Handler ---
@app.route('/webhook', methods=['POST'])
def plaid_webhook():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
        
    webhook_type = data['webhook_type']
    webhook_code = data['webhook_code']
    item_id = data['item_id']

    print(f"\n [Plaid Webhook Received]")
    print(f"   ├─ Type: {webhook_type}")
    print(f"   ├─ Code: {webhook_code}")
    print(f"   └─ Item ID: {item_id}")

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

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    print("Server has started.")
    serve(app, host="127.0.0.1", port=5000)
    