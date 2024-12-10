import urwid
import os
from config import Config
from debug import clear_debug_log, debug
from chat_logic import ChatManager
from chat_screen import ChatScreen
from themes_manager import Themes
from menu import Menu
from ui_elements import CustomEdit
import json
from datetime import datetime

from classes.about_menu import AboutMenu
from classes.history_menu import HistoryMenu
from classes.help_menu import HelpMenu
from classes.model_menu import ModelMenu
from classes.chat_settings_menu import ChatSettingsMenu
from classes.config_menu import ModelSelectionMenu
from classes.config_menu import ThemeSelectionMenu
from classes.config_menu import ConfigMenu

class Application:
    def __init__(self):
        clear_debug_log()
        self.config = Config()
        self.loop = None
        self.chat_manager = None
        self.chat_screen = None

        self.menu = Menu(
            config=self.config,
            on_start_chat=None,
            on_quit=self.quit_app,
            on_show_history=self.show_history_menu,
            on_show_help=self.show_help_menu,
            on_show_model_menu=self.show_model_menu,
            on_show_about=self.show_about_menu,
            on_show_config=self.show_config_menu
        )

        self.history_menu = HistoryMenu(
            on_select_chat=self.resume_chat,
            on_back=self.back_to_main_menu
        )

        self.help_menu = HelpMenu(
            on_back=self.back_to_main_menu
        )

        self.view = self.menu.widget()

        # Default palette
        self.default_palette = [
            ('normal_linebox_border', 'white', ''),
            ('focus_linebox_border', 'white', '', ''),
            ('menu_voice', 'white', '', ''),
            ('normal_content', 'white', ''),
            ('who', 'white', '', ''),
            ('ai_message', 'white', ''),
            ('user_message', 'white', ''),
            ('divider', 'white', '', '')
        ]

        # Initialize theme manager
        self.themes = Themes(default_palette=self.default_palette)
        self.themes.load_theme(self.config.theme)  # e.g., "0" means 0.json
        self.palette = self.themes._merge_palette()  # Merge default with loaded theme

    def start_chat_with_model(self, model_name=None):
        if model_name is None:
            # Use default model from config
            model_name = self.config.model_name
        # Start a new empty conversation
        self.chat_manager = ChatManager(host=self.config.ollama_host, model_name=model_name)
        self.chat_screen = ChatScreen(self.loop, self.chat_manager, self.config, self.quit_app)
        self.view = self.chat_screen.widget()
        self.loop.widget = self.view
        self.chat_screen.update_focus_style()
        debug(f"Chat started with model: {model_name}")

    def resume_chat(self, filename):
        # Load a saved conversation and resume chat
        self.chat_manager = ChatManager(host=self.config.ollama_host, model_name=self.config.model_name)
        self.chat_manager.load_conversation(filename)
        self.chat_screen = ChatScreen(self.loop, self.chat_manager, self.config, self.quit_app)
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
        self.chat_screen = ChatScreen(self.loop, self.chat_manager, self.config, self.quit_app)
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

    def show_config_menu(self):
        temp_manager = ChatManager(host=self.config.ollama_host, model_name=self.config.model_name)
        models = temp_manager.list_available_models()

        self.config_menu = ConfigMenu(
            config=self.config,
            models=models,
            on_save=self.save_config_changes,
            on_back=self.back_to_main_menu,
            on_select_model=self.show_model_selection_menu,
            on_select_theme=self.start_theme_selection
        )
        self.view = self.config_menu.widget()
        self.loop.widget = self.view

    def show_model_selection_menu(self):
        # Show model selection menu
        temp_manager = ChatManager(host=self.config.ollama_host, model_name=self.config.model_name)
        models = temp_manager.list_available_models()

        self.model_selection_menu = ModelSelectionMenu(
            models=models,
            on_select=self.model_selected,
            on_back=self.back_to_config
        )
        self.view = self.model_selection_menu.widget()
        self.loop.widget = self.view

    def model_selected(self, model_name):
        # User selected a model
        # Update model_edit in config_menu
        self.config_menu.model_edit.set_edit_text(model_name)
        self.back_to_config()

    def start_theme_selection(self):
        self.theme_menu = ThemeSelectionMenu(
            themes_directory="./themes",
            on_select=self.apply_theme,
            on_back=self.show_config_menu
        )
        self.view = self.theme_menu.widget()
        self.loop.widget = self.view

    def apply_theme(self, theme_filename):
        self.themes.load_theme(theme_filename)
        self.palette = self.themes._merge_palette()
        self.loop.screen.register_palette(self.palette)
        self.config_menu.theme_edit.set_edit_text(theme_filename)
        self.back_to_config()       

    def back_to_config(self):
        # Return to config menu
        self.view = self.config_menu.widget()
        self.loop.widget = self.view

    def save_config_changes(self, new_host, new_model, new_speed, new_theme):
        # Update config and save
        self.config.set_config("ollama_host", new_host)
        self.config.set_config("model_name", new_model)
        self.config.set_config("typewriter_speed", new_speed)
        self.config.set_config("theme", new_theme)
        # Return to main menu
        self.back_to_main_menu()       

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
        try:
            raise urwid.ExitMainLoop()  # Exit Urwid main loop cleanly
        except urwid.ExitMainLoop:
            debug("Urwid MainLoop exited cleanly.")
        finally:
            os.system('reset')  # Ensures terminal is fully reset
            debug("Terminal reset and cleared.")
            # Force exit
            os._exit(0)

    def handle_input(self, key):
        debug(f"Key pressed: {key}")
        # Check menus with hasattr to avoid AttributeError
        if self.view == self.menu.widget():
            self.menu.handle_input(key)
        elif hasattr(self, 'history_menu') and self.view == self.history_menu.widget():
            self.history_menu.handle_input(key)
        elif hasattr(self, 'about_menu') and self.view == self.about_menu.widget():
            self.about_menu.handle_input(key)
        elif hasattr(self, 'model_menu') and self.view == self.model_menu.widget():
            self.model_menu.handle_input(key)
        elif hasattr(self, 'config_menu') and self.view == self.config_menu.widget():
            self.config_menu.handle_input(key)
        elif hasattr(self, 'model_selection_menu') and self.view == self.model_selection_menu.widget():
            self.model_selection_menu.handle_input(key)
        else:
            # In chat screen
            if key == "ctrl w":
                if self.view.focus_part == "footer":
                    self.view.set_focus("body")
                else:
                    self.view.set_focus("footer")
                self.chat_screen.update_focus_style()
            elif key == "ctrl o":
                self.quit_app()
            elif key == "esc":
                self.back_to_main_menu()
            elif key == "ctrl e":
                self.show_chat_settings()
            elif key == "meta h":
                self.show_help_menu()



    def run(self):
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.handle_input)
        self.loop.run()

if __name__ == "__main__":
    app = Application()
    app.run()