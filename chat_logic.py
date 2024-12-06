import threading
import json
import os
import time
from ollama import Client
from debug import debug
from datetime import datetime

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "history")
HISTORY_DETAILS_DIR = os.path.join(os.path.dirname(__file__), "history_details")
os.makedirs(HISTORY_DIR, exist_ok=True)  # Ensure history folder exists
os.makedirs(HISTORY_DETAILS_DIR, exist_ok=True) # Ensure history_details folder exists

class ChatManager:
    def __init__(self, host, model_name):
        self.client = Client(host=host)
        self.model_name = model_name
        self.typing_in_progress = False
        self.conversation_history = []
        # Initialize these attributes so they're always defined
        self.current_placeholder = None
        self.current_reply = None
        self.current_index = 0
        self.current_history_file = None
        self.chat_name = ""  # Add this line to track the chat name

    def list_available_models(self):
        # Fetch available models from the client. 
        # Handles cases where models are listed under 'name' or 'model'.
        try:
            # Fetch the result from the client
            result = self.client.list()
            models_info = result.get("models", [])
            # Attempt to extract names using 'name'
            model_names = [m.get("name") for m in models_info if "name" in m]
            # If no models are found using 'name', fallback to 'model'
            if not model_names:
                model_names = [m.get("model") for m in models_info if "model" in m]
            return model_names
        except Exception as e:
            # In case of error, return an empty list
            return []

    def send_user_message(self, user_input, on_reply_ready, on_error):
        self.typing_in_progress = True
        # Append user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        # Save conversation after user message
        self.save_conversation()
        threading.Thread(
            target=self._process_response, 
            args=(user_input, on_reply_ready, on_error)
        ).start()

    def _process_response(self, user_input, on_reply_ready, on_error):
        try:
            response = self.client.chat(
                model=self.model_name, 
                messages=self.conversation_history
            )
            reply = response["message"]["content"]
            debug(f"AI response received: {reply}")
            # Append assistant response to history
            self.conversation_history.append({"role": "assistant", "content": reply})
            # Save conversation after assistant message
            self.save_conversation()
            on_reply_ready(reply)
        except Exception as e:
            debug(f"AI error: {e}")
            on_error(str(e))
            self.typing_in_progress = False

    def start_typing_effect(self, placeholder, reply):
        self.current_placeholder = placeholder
        self.current_reply = reply
        self.current_index = 0
        self.typing_in_progress = True

    def stop_typing_effect(self):
        self.typing_in_progress = False
        self.current_placeholder = None
        self.current_reply = None
        self.current_index = 0

    def save_conversation(self):
        # If no current_history_file is set, create a new one with a timestamp
        if not self.current_history_file:
            timestamp = int(time.time())
            self.current_history_file = os.path.join(HISTORY_DIR, f"chat_{timestamp}.json")
            self.save_conversation_details()
        with open(self.current_history_file, "w") as f:
            json.dump(self.conversation_history, f, indent=4)
            #self.save_conversation_details()

    def load_conversation(self, filename):
        # Load conversation from a file
        with open(os.path.join(HISTORY_DIR, filename), "r") as f:
            self.conversation_history = json.load(f)
        self.current_history_file = os.path.join(HISTORY_DIR, filename)

    def save_conversation_details(self):
        if not self.current_history_file:
            return  # No history file yet, nothing to save
        # details filename matches the main history filename but in history_details
        base_name = os.path.basename(self.current_history_file)
        details_file = os.path.join(HISTORY_DETAILS_DIR, base_name)

        timestamp = int(time.time())
        ctime_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

        details_data = {
            "model_name": self.model_name,
            "name": self.chat_name,
            "create_date": ctime_str
        }

        with open(details_file, "w") as f:
            json.dump(details_data, f, indent=4)

    def load_conversation_details(self, filename):
        details_file = os.path.join(HISTORY_DETAILS_DIR, filename)
        if os.path.exists(details_file):
            with open(details_file, "r") as f:
                details_data = json.load(f)
                self.model_name = details_data.get("model_name", self.model_name)
                self.chat_name = details_data.get("name", self.chat_name)
        else:
            # If no details file, model_name remains whatever was set or default
            pass

    def delete_chat_files(self):
        # Delete the main history file and its details file
        if self.current_history_file and os.path.exists(self.current_history_file):
            os.remove(self.current_history_file)

        if self.current_history_file:
            base_name = os.path.basename(self.current_history_file)
            details_file = os.path.join(HISTORY_DETAILS_DIR, base_name)
            if os.path.exists(details_file):
                os.remove(details_file)

    @staticmethod
    def list_saved_chats():
        # List all .json files in history directory
        files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
        return files