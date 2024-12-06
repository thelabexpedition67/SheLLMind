import urwid

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
        # Press 'esc' to go back as well
        if key == 'esc':
            self.on_back()