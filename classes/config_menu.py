import urwid
import re

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
                btn = urwid.Button(m)
                urwid.connect_signal(btn, 'click', self._model_chosen, m)
                buttons.append(btn)

            back_btn = urwid.Button("Back")
            urwid.connect_signal(back_btn, 'click', lambda button: self.on_back())
            buttons.append(back_btn)

            list_walker = urwid.SimpleFocusListWalker(buttons)
            list_box = urwid.ListBox(list_walker)
            self.view = urwid.LineBox(list_box, title="Select a Model")

    def _model_chosen(self, button, model_name):
        self.on_select(model_name)

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()


class ConfigMenu:
    def __init__(self, config, models, on_save, on_back, on_select_model):
        self.config = config
        self.models = models
        self.on_save = on_save
        self.on_back = on_back
        self.on_select_model = on_select_model  # callback to open model selection

        current_host = self.config.ollama_host or ""
        current_model = self.config.model_name or ""
        current_speed = str(self.config.typewriter_speed or "1")

        self.host_edit = urwid.Edit("Ollama API url: ", current_host)
        self.model_edit = urwid.Edit("Default Model: ", current_model)

        select_model_btn = urwid.Button("Select Model")
        urwid.connect_signal(select_model_btn, 'click', self._select_model_clicked)

        self.speed_edit = urwid.Edit("Typewriter Speed (0-10): ", current_speed)

        save_btn = urwid.Button("Save")
        urwid.connect_signal(save_btn, 'click', self._on_save_clicked)

        back_btn = urwid.Button("Back")
        urwid.connect_signal(back_btn, 'click', lambda button: self.on_back())

        items = [
            urwid.Text("Edit\n", align="center"),
            self.host_edit,
            urwid.Text(""),
            self.model_edit,
            select_model_btn,
            urwid.Text(""),
            self.speed_edit,
            urwid.Text(""),
            save_btn,
            urwid.Text(""),
            back_btn
        ]

        list_walker = urwid.SimpleFocusListWalker(items)
        list_box = urwid.ListBox(list_walker)
        self.view = urwid.LineBox(list_box, title="Configuration")

    def _select_model_clicked(self, button):
        # Open model selection menu
        self.on_select_model()

    def _on_save_clicked(self, button):
        new_host = self.host_edit.get_edit_text().strip()
        new_model = self.model_edit.get_edit_text().strip()
        new_speed_str = self.speed_edit.get_edit_text().strip()

        # Validate host
        if not (new_host.startswith("http://") or new_host.startswith("https://")):
            self.host_edit.set_caption("Ollama API url (Invalid, must start with http:// or https://): ")
            self.host_edit.set_edit_text("")
            return

        # Validate speed
        if not new_speed_str.isdigit():
            self.speed_edit.set_caption("Typewriter Speed (Invalid, must be number 0-10): ")
            self.speed_edit.set_edit_text("")
            return
        new_speed = int(new_speed_str)
        if new_speed < 0 or new_speed > 10:
            self.speed_edit.set_caption("Typewriter Speed (Invalid, must be 0-10): ")
            self.speed_edit.set_edit_text("")
            return

        self.on_save(new_host, new_model, new_speed)

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()