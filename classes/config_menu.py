import urwid
import re
import os
from themes_manager import Themes
from debug import debug
import json

class ThemeSelectionMenu:
    class StyledButton(urwid.Button):
        """
        Custom Styled Button for displaying theme information in multiline with selectable behavior.
        """
        def __init__(self, theme_name, theme_description, theme_author, on_press, user_data=None):
            super().__init__("")
            
            # Define styled text portions
            styled_text = [
                ('menu_voice', f"> {theme_name} "),           
                "\n",                                         
                ('normal_content', f"  Description: {theme_description}\n"),  
                ('normal_content', f"  Author: {theme_author}\n")  
            ]

            # Use SelectableIcon to preserve the cursor behavior and support focus
            self._w = urwid.AttrMap(
                urwid.SelectableIcon(styled_text, 0),
                None,  # Normal state style
                focus_map='normal_content'  # Focused style
            )
            
            # Connect the button press signal
            urwid.connect_signal(self, 'click', on_press, user_data)

    def __init__(self, themes_directory, on_select, on_back):
        """
        Initialize the Theme Selection Menu.
        :param themes_directory: Directory containing the theme JSON files.
        :param on_select: Callback when a theme is selected.
        :param on_back: Callback to return to the previous menu.
        """
        self.on_select = on_select
        self.on_back = on_back
        self.themes_directory = themes_directory
        self.themes = self._load_themes()

        buttons = []

        # Add "No Theme" option at the top
        no_theme_button = self.StyledButton(
            theme_name="No Theme",
            theme_description="All white colors",
            theme_author="System",
            on_press=self._theme_chosen,
            user_data='default'
        )
        buttons.append(no_theme_button)

        # Add buttons for available themes
        for theme in self.themes:
            btn = self.StyledButton(
                theme_name=theme['name'],
                theme_description=theme['description'],
                theme_author=theme['author'],
                on_press=self._theme_chosen,
                user_data=theme['filename']
            )
            buttons.append(btn)

        # Add a Back button
        back_btn = urwid.Button(('normal_content', "Back"), on_press=lambda x: self.on_back())
        buttons.append(urwid.AttrMap(back_btn, None, focus_map='focus_linebox_border'))

        # Construct the menu UI
        list_walker = urwid.SimpleFocusListWalker(buttons)
        list_box = urwid.ListBox(list_walker)
        line_box = urwid.LineBox(list_box, title="Select a Theme")
        self.view = urwid.AttrMap(line_box, 'focus_linebox_border')

    def _load_themes(self):
        """
        Load all valid themes from the themes directory.
        """
        themes = []
        if not os.path.exists(self.themes_directory):
            return themes

        for filename in os.listdir(self.themes_directory):
            if filename.endswith(".json"):
                debug(f"Attempting to load theme file: {filename}")
                try:
                    with open(os.path.join(self.themes_directory, filename), "r") as file:
                        theme_data = json.load(file)
                        themes.append({
                            "name": theme_data.get("name", "Unknown Theme"),
                            "description": theme_data.get("description", "No description provided."),
                            "author": theme_data.get("author", "Unknown"),
                            "filename": filename.split(".")[0]
                        })
                except Exception as e:
                    debug(f"Error loading theme {filename}: {e}")
        return themes

    def _theme_chosen(self, button, theme_filename):
        """
        Callback triggered when a theme is selected.
        """
        self.on_select(theme_filename)

    def widget(self):
        """
        Return the main widget of the theme selection menu.
        """
        return self.view

    def handle_input(self, key):
        """
        Handle user input for the theme menu.
        """
        if key == 'esc':
            self.on_back()



class ModelSelectionMenu:
    def __init__(self, models, on_select, on_back):
        self.on_select = on_select
        self.on_back = on_back

        if not models:
            text = urwid.Text("No models found.\nPress 'b' to go back.")
            self.view = urwid.LineBox(urwid.Filler(text), title="Select a Model")
        else:
            buttons = []
            for m in models:
                btn = urwid.Button(('menu_voice',m))
                urwid.connect_signal(btn, 'click', self._model_chosen, m)
                buttons.append(btn)

            back_btn = urwid.Button(('normal_content',"Back"))
            urwid.connect_signal(back_btn, 'click', lambda button: self.on_back())
            buttons.append(back_btn)

            list_walker = urwid.SimpleFocusListWalker(buttons)
            list_box = urwid.ListBox(list_walker)

            list_box = urwid.ListBox(list_walker)
            line_box = urwid.LineBox(list_box, title="Select a Model")
            self.view = urwid.AttrMap(line_box, 'focus_linebox_border')

    def _model_chosen(self, button, model_name):
        self.on_select(model_name)

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()


class ConfigMenu:
    def __init__(self, config, models, on_save, on_back, on_select_model, on_select_theme):
        self.config = config
        self.models = models
        self.on_save = on_save
        self.on_back = on_back
        self.on_select_model = on_select_model
        self.on_select_theme = on_select_theme  # callback for theme selection

        current_host = self.config.ollama_host or ""
        current_model = self.config.model_name or ""
        current_speed = str(self.config.typewriter_speed or "1")
        current_theme = self.config.theme or "default"

        self.host_edit = urwid.Edit([("menu_voice", "Ollama API url"), ": "], current_host)
        self.model_edit = urwid.Edit([("menu_voice", "Default Model"), ": "], current_model)
        self.theme_edit = urwid.Edit([("menu_voice", "Current Theme"), ": "], current_theme)
        

        select_model_btn = urwid.Button(("menu_voice", "Select Model"))
        urwid.connect_signal(select_model_btn, 'click', self._select_model_clicked)

        select_theme_btn = urwid.Button(("menu_voice", "Select Theme"))
        urwid.connect_signal(select_theme_btn, 'click', self._select_theme_clicked)

        self.speed_edit = urwid.Edit([("menu_voice", "Typewriter Speed (0-10)"), ": "], current_speed)

        save_btn = urwid.Button(("normal_content", "Save"))
        urwid.connect_signal(save_btn, 'click', self._on_save_clicked)

        back_btn = urwid.Button(("normal_content", "Back"))
        urwid.connect_signal(back_btn, 'click', lambda button: self.on_back())

        items = [
            urwid.Text("Edit\n", align="center"),
            self.host_edit,
            urwid.Text(""),
            self.model_edit,
            select_model_btn,
            urwid.Text(""),
            self.theme_edit,
            select_theme_btn,
            urwid.Text(""),
            self.speed_edit,
            urwid.Text(""),
            save_btn,
            urwid.Text(""),
            back_btn
        ]

        list_walker = urwid.SimpleFocusListWalker(items)
        list_box = urwid.ListBox(list_walker)
        line_box = urwid.LineBox(list_box, title="Configuration")
        self.view = urwid.AttrMap(line_box, 'focus_linebox_border')

    def _select_model_clicked(self, button):
        self.on_select_model()

    def _select_theme_clicked(self, button):
        self.on_select_theme()

    def _on_save_clicked(self, button):
        new_host = self.host_edit.get_edit_text().strip()
        new_model = self.model_edit.get_edit_text().strip()
        new_theme = self.theme_edit.get_edit_text().strip()
        new_speed_str = self.speed_edit.get_edit_text().strip()

        if not new_speed_str.isdigit() or not (0 <= int(new_speed_str) <= 10):
            self.speed_edit.set_caption("Typewriter Speed (Invalid, must be 0-10): ")
            self.speed_edit.set_edit_text("")
            return

        new_speed = int(new_speed_str)
        self.on_save(new_host, new_model, new_speed, new_theme)

    def update_theme(self, new_theme):
        self.theme_edit.set_text([("menu_voice", f"Current Theme: {new_theme}")])

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()