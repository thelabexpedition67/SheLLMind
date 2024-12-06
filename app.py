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

from classes.about_menu import AboutMenu
from classes.history_menu import HistoryMenu
from classes.help_menu import HelpMenu
from classes.model_menu import ModelMenu
from classes.chat_settings_menu import ChatSettingsMenu

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
            on_show_model_menu=self.show_model_menu,
            on_show_about=self.show_about_menu
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

    def show_about_menu(self):
        self.about_menu = AboutMenu(on_back=self.back_to_main_menu)
        self.view = self.about_menu.widget()
        self.loop.widget = self.view

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
        elif self.view == self.about_menu.widget():
            self.about_menu.handle_input(key)
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
