import urwid

class CustomEdit(urwid.Edit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_handler = None

    def keypress(self, size, key):
        # "ctrl l" to insert newline, enter to send message
        if key == "enter":
            if self.message_handler:
                self.message_handler()
            return None
        elif key == "ctrl l":
            self.insert_text("\n")
            return None
        return super().keypress(size, key)

    def set_message_handler(self, handler):
        self.message_handler = handler
