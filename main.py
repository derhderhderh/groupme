404: Not Foundimport os
import sys
import time
import requests
from flask import Flask, request, jsonify

# GroupMe API Token and Bot Information
BOT_ID = "89ec50d32a058e6c8b188c561d"
API_TOKEN = "SpLll46L1nhYWLcdoM2w68pmpYNZBPx0HRrePXGK"
ALLOWED_USERS = ["112716085", "73921668"]  # Allowed users' GroupMe IDs
TOPIC_NAME = "Statistics"  # Name of the group where stats will be posted

app = Flask(__name__)

# Function to send a DM to a user
def send_dm(text, user_id):
    url = f"https://api.groupme.com/v3/direct_messages"
    payload = {
        "direct_message": {
            "source_guid": str(time.time()),
            "recipient_id": user_id,
            "text": text
        }
    }
    headers = {"X-Access-Token": API_TOKEN}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 202:  # Check if the DM was successfully sent
        print(f"DM sent to {user_id}: {text}")  # Log success
    else:
        print(f"Failed to send DM to {user_id}. Status code: {response.status_code}")

# Function to get the topic ID by topic name
def get_topic_id_by_name(topic_name):
    url = f"https://api.groupme.com/v3/groups?access_token={API_TOKEN}"
    response = requests.get(url)
    groups = response.json().get('response', [])
    for group in groups:
        if group['name'] == topic_name:
            print(f"Topic '{topic_name}' found with ID {group['group_id']}")  # Log success
            return group['group_id']
    print(f"Topic '{topic_name}' not found.")  # Log failure
    return None

# Get the topic ID based on the topic name
TOPIC_ID = get_topic_id_by_name(TOPIC_NAME)

if TOPIC_ID is None:
    print(f"Topic '{TOPIC_NAME}' not found. Bot cannot start.")

@app.route("/start-bot", methods=["POST"])
def start_bot():
    if TOPIC_ID is not None:
        # Notify users that the bot is online
        for user in ALLOWED_USERS:
            send_dm("The bot is online - ready to do normal functions", user)
        return "Bot started and notifications sent to users.", 200
    else:
        return "Topic not found, cannot start the bot.", 500

# Flask route to handle messages from GroupMe
@app.route("/groupme", methods=["POST"])
def groupme_webhook():
    data = request.get_json()
    sender_id = str(data["sender_id"])
    message_text = data["text"].strip()

    if sender_id in ALLOWED_USERS:
        if message_text.lower() == "!stats":
            stats_format = """
Please provide the game statistics in this format:

Player Name(s):
Points Scored:
Fouls:
Assists:
Other Information:
"""
            send_dm(stats_format, sender_id)
            print(f"Sent stats format to {sender_id}")  # Log success
        elif "Player Name(s):" in message_text and TOPIC_ID:
            send_message(f"Game Stats Received:\n{message_text}", TOPIC_ID)
            send_dm("Stats submitted successfully!", sender_id)
            print(f"Stats submitted successfully by {sender_id}")  # Log success

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Bot is starting...")
    
    # Wait for 30 seconds to give time to get the URL
    time.sleep(30)
    
    # Restart the bot
    print("Bot is restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)
