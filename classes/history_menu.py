import urwid
import os
from config import Config
import json
from datetime import datetime

class HistoryMenu:
    def __init__(self, on_select_chat, on_back):
        self.on_select_chat = on_select_chat
        self.on_back = on_back
        self.files = []
        self.view = None


    class StyledButton(urwid.Button):
        def __init__(self, file_name, chat_name, chat_model_name, ctime_str, mtime_str, on_press, user_data=None):
            super().__init__("")
            
            # Styled portions of the button's text
            styled_text = [
                ('menu_voice', f"> {file_name} "),                # File name with menu_voice style
                ('chat_model_style', f"({chat_model_name})"),    # Chat model name with custom style
                "\n",                                            # Newline
                f" Name: {chat_name}\n",                         # Regular text
                f" Created: {ctime_str}\n",                      # Regular text
                f" Modified: {mtime_str}\n"                      # Regular text
            ]

            # Use SelectableIcon to preserve the cursor behavior
            self._w = urwid.AttrMap(urwid.SelectableIcon(styled_text, 0), None, focus_map='normal_content')
            
            # Connect the button press signal
            urwid.connect_signal(self, 'click', on_press, user_data)


    def populate(self, files):
        self.files = files

        # If no files, show a message
        if not files:
            text = urwid.Text("No saved chats found.\nPress 'esc' to go back.")
            line_box = urwid.LineBox(urwid.Filler(text), title="History")
            self.view = urwid.AttrMap(line_box, 'focus_linebox_border')
            return

        # HISTORY_DETAILS_DIR and HISTORY_DIR should match what we have in chat_logic.py
        # Assuming they are defined in chat_logic.py. If not, define them here similarly.
        from chat_logic import HISTORY_DETAILS_DIR, HISTORY_DIR

        entries = []
        for f in files:
            # Full paths
            history_path = os.path.join(HISTORY_DIR, f)
            details_path = os.path.join(HISTORY_DETAILS_DIR, f)

            # Load details if available
            chat_name = "NO NAME"
            chat_model_name = ""
            ctime_str = ""
            if os.path.exists(details_path):
                with open(details_path, "r") as df:
                    details_data = json.load(df)
                    chat_name = details_data.get("name", "NO NAME")
                    ctime_str = details_data.get("create_date", "")
                    chat_model_name = details_data.get("model_name", "")

            if chat_name=="":chat_name = "NO NAME"

            # Get timestamps
            # ctime: creation (or metadata change) time, mtime: last modification time
            #ctime = os.path.getctime(history_path)
            mtime = os.path.getmtime(history_path)

            # Convert to human-readable format
            #ctime_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M:%S")
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

            # Store a tuple with all info and use it for sorting
            # We'll sort by mtime descending later
            entries.append((f, chat_name, chat_model_name, ctime_str, mtime_str, mtime))

        # Sort entries by modified time descending
        entries.sort(key=lambda x: x[4], reverse=True)

        buttons = []
        for f, chat_name, chat_model_name, ctime_str, mtime_str, _ in entries:
            # Create the custom StyledButton
            btn = self.StyledButton(f, chat_name, chat_model_name, ctime_str, mtime_str, 
                            on_press=self._on_chat_selected, user_data=f)
            buttons.append(btn)

        # Add a Back button
        back_btn = urwid.Button(('normal_content',"Back"), on_press=lambda x: self.on_back())
        buttons.append(back_btn)

        list_walker = urwid.SimpleFocusListWalker(buttons)
        list_box = urwid.ListBox(list_walker)
        line_box = urwid.LineBox(list_box, title="Select a Chat")
        self.view = urwid.AttrMap(line_box, 'focus_linebox_border')

    def _on_chat_selected(self, button, filename):
        self.on_select_chat(filename)

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()