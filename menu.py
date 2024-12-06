import urwid

class MenuItem(urwid.Button):
    def __init__(self, label, on_press_callback):
        super().__init__(label, on_press=on_press_callback)

def menu_button(label, on_press_callback):
    return MenuItem(label, on_press_callback)

class Menu:
    def __init__(self, config, on_start_chat, on_quit, on_show_history, on_show_help, on_show_model_menu, on_show_about, on_show_config):
        self.config = config
        self.on_start_chat = on_start_chat
        self.on_quit = on_quit
        self.on_show_history = on_show_history
        self.on_show_help = on_show_help
        self.on_show_model_menu = on_show_model_menu
        self.on_show_about = on_show_about
        self.on_show_config = on_show_config

        start_chat_btn = menu_button("Start Chat", lambda button: self.on_show_model_menu())
        history_btn = menu_button("History", lambda button: self.on_show_history())
        help_btn = menu_button("Help", lambda button: self.on_show_help())
        quit_btn = menu_button("Quit", lambda button: self.on_quit())
        about_btn = menu_button("About", lambda button: self.on_show_about())
        config_btn = menu_button("Configuration", lambda button: self.on_show_config())

        menu_items = [start_chat_btn, history_btn, config_btn, help_btn, about_btn, quit_btn]
        self.list_walker = urwid.SimpleFocusListWalker(menu_items)
        # Add a footer text to the menu
        footer_text = urwid.Text("SheLLMind - TheLabExpedition67", align='right')
        frame = urwid.Frame(urwid.ListBox(self.list_walker), footer=footer_text)
        self.view = urwid.LineBox(frame, title="Menu")
        
    def widget(self):
        return self.view

    def handle_input(self, key):
        # Menu navigates with arrow keys, enter to select.
        pass
