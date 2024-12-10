import urwid

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
        line_box = urwid.LineBox(filler, title="Help")
        self.view = urwid.AttrMap(line_box, 'focus_linebox_border')

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()