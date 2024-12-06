import urwid

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
        # Allow pressing 'esc' to go back as well
        if key == 'esc':
            self.on_back()