import urwid
import os
from config import Config
from debug import clear_debug_log, debug
from chat_logic import ChatManager
from chat_screen import ChatScreen
from menu import Menu
from ui_elements import CustomEdit
import json
from datetime import datetime


class HistoryMenu:
    def __init__(self, on_select_chat, on_back):
        self.on_select_chat = on_select_chat
        self.on_back = on_back
        self.files = []
        self.view = None

    def populate(self, files):
        self.files = files

        # If no files, show a message
        if not files:
            text = urwid.Text("No saved chats found.\nPress 'esc' to go back.")
            self.view = urwid.LineBox(urwid.Filler(text), title="History")
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

        # Create list of buttons with displayed info
        buttons = []
        for f, chat_name, chat_model_name, ctime_str, mtime_str, _ in entries:
            display_text = f"{f} ({chat_model_name})\nName: {chat_name}\nCreated: {ctime_str}\nModified: {mtime_str}"
            btn = urwid.Button(display_text)
            urwid.connect_signal(btn, 'click', self._on_chat_selected, f)
            buttons.append(btn)

        # Add a Back button
        back_btn = urwid.Button("Back", on_press=lambda x: self.on_back())
        buttons.append(back_btn)

        list_walker = urwid.SimpleFocusListWalker(buttons)
        list_box = urwid.ListBox(list_walker)
        self.view = urwid.LineBox(list_box, title="Select a Chat")

    def _on_chat_selected(self, button, filename):
        self.on_select_chat(filename)

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()

class HelpMenu:
    def __init__(self, on_back):
        self.on_back = on_back
        help_text = urwid.Text(
            "Keyboard Shortcuts:\n\n"
            "While in Chat:\n"
            "  ctrl+w : Toggle focus between Chat History and Input Box\n"
            "  ctrl+o : Quit the application\n"
            "  esc : Back to main menu\n\n"
            "Inside the Input Box:\n"
            "  enter   : Send message\n"
            "  ctrl+l  : Insert a newline\n\n"
            "Press 'esc' to return to the main menu."
        )
        filler = urwid.Filler(help_text, 'top')
        self.view = urwid.LineBox(filler, title="Help")

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()

class ModelMenu:
    def __init__(self, models, on_select_model, on_back, config_model):
        self.on_select_model = on_select_model
        self.on_back = on_back

        if not models:
            text = urwid.Text("No models found.\nPress 'esc' to go back.")
            self.view = urwid.LineBox(urwid.Filler(text), title="Models")
        else:
            # Create a button for each model name
            buttons = []

            # Add a "Use Default Model" option
            default_btn = urwid.Button(f"Use Default Model ({config_model})")
            urwid.connect_signal(default_btn, 'click', self._on_model_selected, config_model)
            buttons.append(default_btn)

            for m in models:
                btn = urwid.Button(m)
                urwid.connect_signal(btn, 'click', self._on_model_selected, m)
                buttons.append(btn)
            
            # Add a Back button
            back_btn = urwid.Button("Back")
            urwid.connect_signal(back_btn, 'click', lambda button: self.on_back())
            buttons.append(back_btn)

            # Create a ListBox to display these buttons
            list_walker = urwid.SimpleFocusListWalker(buttons)
            list_box = urwid.ListBox(list_walker)
            self.view = urwid.LineBox(list_box, title="Select a Model")

    def _on_model_selected(self, button, model_name):
        self.on_select_model(model_name)

    def widget(self):
        return self.view

    def handle_input(self, key):
        # Allow pressing 'b' to go back as well
        if key == 'esc':
            self.on_back()

class ChatSettingsMenu:
    def __init__(self, current_name, on_save_name, on_delete_chat, on_back):
        self.on_save_name = on_save_name
        self.on_delete_chat = on_delete_chat
        self.on_back = on_back

        # Editable text for the chat name
        self.name_edit = urwid.Edit("Chat Name: ", current_name)

        # Buttons
        save_btn = urwid.Button("Save Name")
        urwid.connect_signal(save_btn, 'click', self._save_name_clicked)

        delete_btn = urwid.Button("Delete Chat")
        urwid.connect_signal(delete_btn, 'click', self._delete_chat_clicked)

        back_btn = urwid.Button("Back")
        urwid.connect_signal(back_btn, 'click', lambda button: self.on_back())

        items = [
            self.name_edit,
            urwid.Text(""),
            save_btn,
            urwid.Text(""),
            delete_btn,
            urwid.Text(""),
            back_btn
        ]
        list_walker = urwid.SimpleFocusListWalker([urwid.AttrMap(w, None) for w in items])
        list_box = urwid.ListBox(list_walker)
        self.view = urwid.LineBox(list_box, title="Chat Settings")

    def _save_name_clicked(self, button):
        new_name = self.name_edit.get_edit_text().strip()
        self.on_save_name(new_name)

    def _delete_chat_clicked(self, button):
        self.on_delete_chat()

    def widget(self):
        return self.view

    def handle_input(self, key):
        # Press 'b' to go back as well
        if key == 'esc':
            self.on_back()

class Application:
    def __init__(self):
        clear_debug_log()
        self.config = Config()
        self.loop = None
        self.chat_manager = None
        self.chat_screen = None

        self.menu = Menu(
            config=self.config,
            on_start_chat=None,  #on_start_chat=self.start_chat,
            on_quit=self.quit_app,
            on_show_history=self.show_history_menu,
            on_show_help=self.show_help_menu,
            on_show_model_menu=self.show_model_menu
        )

        self.history_menu = HistoryMenu(
            on_select_chat=self.resume_chat,
            on_back=self.back_to_main_menu
        )

        self.help_menu = HelpMenu(
            on_back=self.back_to_main_menu
        )


        self.view = self.menu.widget()
        # Define palette for focus styling
        self.palette = [
            ('normal_linebox_border', 'white', 'black'),
            ('focus_linebox_border', 'light cyan', 'black'),
            ('normal_content', 'white', 'black'),
            ("divider", "dark cyan", "black")
        ]

    def start_chat_with_model(self, model_name=None):
        if model_name is None:
            # Use default model from config
            model_name = self.config.model_name
        # Start a new empty conversation
        self.chat_manager = ChatManager(host=self.config.ollama_host, model_name=model_name)
        self.chat_screen = ChatScreen(self.loop, self.chat_manager, self.config)
        self.view = self.chat_screen.widget()
        self.loop.widget = self.view
        self.chat_screen.update_focus_style()
        debug(f"Chat started with model: {model_name}")

    def resume_chat(self, filename):
        # Load a saved conversation and resume chat
        self.chat_manager = ChatManager(host=self.config.ollama_host, model_name=self.config.model_name)
        self.chat_manager.load_conversation(filename)
        self.chat_screen = ChatScreen(self.loop, self.chat_manager, self.config)
        self.view = self.chat_screen.widget()
        self.loop.widget = self.view
        self.chat_screen.update_focus_style()
        debug(f"Resumed chat from {filename}.")

    def resume_chat(self, filename):
        self.chat_manager = ChatManager(host=self.config.ollama_host, model_name=self.config.model_name)
        self.chat_manager.load_conversation(filename)
        self.chat_manager.load_conversation_details(filename)  # Load model and other details
        # Now self.chat_manager.model_name should reflect the model previously used
        # Recreate the ChatScreen with the updated model name
        self.chat_screen = ChatScreen(self.loop, self.chat_manager, self.config)
        self.view = self.chat_screen.widget()
        self.loop.widget = self.view
        self.chat_screen.update_focus_style()
        debug(f"Resumed chat from {filename} with model: {self.chat_manager.model_name}")

    def show_history_menu(self):
        files = self.chat_manager.list_saved_chats() if self.chat_manager else ChatManager.list_saved_chats()
        self.history_menu.populate(files)
        self.view = self.history_menu.widget()
        self.loop.widget = self.view

    def show_help_menu(self):
        # Show the help screen
        self.view = self.help_menu.widget()
        self.loop.widget = self.view

    def show_model_menu(self):
        # Create a temporary ChatManager just to list models if self.chat_manager is None
        temp_manager = ChatManager(host=self.config.ollama_host, model_name=self.config.model_name)
        models = temp_manager.list_available_models()
        self.model_menu = ModelMenu(
            models=models,
            on_select_model=self.start_chat_with_model,
            on_back=self.back_to_main_menu,
            config_model=self.config.model_name
        )
        self.view = self.model_menu.widget()
        self.loop.widget = self.view

    def show_chat_settings(self):
        # This assumes we are currently in a chat
        # We can access self.chat_manager.chat_name for current name
        current_name = self.chat_manager.chat_name
        self.chat_settings_menu = ChatSettingsMenu(
            current_name=current_name,
            on_save_name=self.save_chat_name,
            on_delete_chat=self.delete_current_chat,
            on_back=self.back_to_chat
        )
        self.view = self.chat_settings_menu.widget()
        self.loop.widget = self.view

    def save_chat_name(self, new_name):
        self.chat_manager.chat_name = new_name
        self.chat_manager.save_conversation_details()  # Update details with new name
        self.back_to_chat()

    def delete_current_chat(self):
        self.chat_manager.delete_chat_files()
        # After deleting the chat, return to main menu
        self.back_to_main_menu()

    def back_to_chat(self):
        # Return to the chat screen
        self.view = self.chat_screen.widget()
        self.loop.widget = self.view

    def back_to_main_menu(self):
        self.view = self.menu.widget()
        self.loop.widget = self.view

    def quit_app(self):
        raise urwid.ExitMainLoop()

    def handle_input(self, key):
        debug(f"Key pressed: {key}")
        # Determine which screen we are on and handle keys
        if self.view == self.menu.widget():
            # In the menu
            self.menu.handle_input(key)
        elif self.view == self.history_menu.widget():
            # In the history menu
            self.history_menu.handle_input(key)
        else:
            # In chat screen
            if key == "ctrl w":
                if self.view.focus_part == "footer":
                    self.view.set_focus("body")
                else:
                    self.view.set_focus("footer")
                self.chat_screen.update_focus_style()
            elif key == "ctrl o":
                # User pressed ctrl+q to quit
                self.quit_app()
            elif key == "esc":
                # User pressed ctrl+m to go back to menu
                self.back_to_main_menu()
            elif key == "ctrl e":
                # Show chat settings menu
                self.show_chat_settings()
            elif key == "meta h":
                # Show chat settings menu
                self.show_help_menu()


    def run(self):
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.handle_input)
        self.loop.run()

if __name__ == "__main__":
    app = Application()
    app.run()
