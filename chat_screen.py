import urwid
from debug import debug
from ui_elements import CustomEdit

class ChatScreen:
    def __init__(self, loop, chat_manager, config):
        self.loop = loop
        self.chat_manager = chat_manager
        self.config = config

        self.chat_box = urwid.SimpleFocusListWalker([])
        self.chat_list = urwid.ListBox(self.chat_box)

        chat_list_attr = urwid.AttrMap(self.chat_list, 'normal_content')

        self.input_box = CustomEdit(("I say", "You: "), multiline=True)
        input_box_attr = urwid.AttrMap(self.input_box, 'normal_content')

        chat_linebox = urwid.LineBox(chat_list_attr, title=chat_manager.model_name)
        self.chat_linebox = urwid.AttrMap(chat_linebox, 'normal_linebox_border')

        input_linebox = urwid.LineBox(input_box_attr, title="Type your message")
        self.input_linebox = urwid.AttrMap(input_linebox, 'normal_linebox_border')

        self.view = urwid.Frame(
            self.chat_linebox,
            footer=self.input_linebox
        )
        self.view.set_focus("footer")

        self.input_box.set_message_handler(self.send_message)
        self.loop.set_alarm_in(0.05, self.periodic_update)

        # If we have a pre-loaded conversation, display it
        message_count = 0  # Counter for messages
        for msg in self.chat_manager.conversation_history:
            role = "You" if msg["role"] == "user" else "AIm"
            self.update_chat(f"{role}: {msg['content']}", spacer=False)
            message_count += 1
            # Add a spacer after every two messages (user + AI)
            if message_count % 2 == 0:
                #self.update_chat("", spacer=False)  # Add an empty line as spacer
                self.chat_box.append(urwid.AttrMap(urwid.Divider("-"), "divider"))  # Add a horizontal line

    def widget(self):
        return self.view

    def update_chat(self, new_message, spacer=True):
        if spacer:
            #self.chat_box.append(urwid.Text("")) # Add an empty line
            self.chat_box.append(urwid.AttrMap(urwid.Divider("-"), "divider"))  # Add a horizontal line
        self.chat_box.append(urwid.Text(new_message))
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        if self.view.focus_part != "footer":
            debug("Skipping scroll to bottom since history is in focus.")
            return

        debug(f"Scroll Request: len(chat_box)={len(self.chat_box)}")
        if len(self.chat_box) > 0:
            self.chat_list.set_focus(len(self.chat_box) - 1)
            debug("Focus set to last widget in chat_list.")
            self.chat_list.set_focus_valign("bottom")
            debug("Viewport aligned to bottom.")

        self.loop.draw_screen()
        debug("UI redrawn after scroll adjustment.")

    def send_message(self):
        if self.chat_manager.typing_in_progress:
            return
        user_input = self.input_box.get_edit_text().strip()
        if not user_input:
            return

        self.update_chat(f"You: {user_input}")
        self.input_box.set_edit_text("")
        debug(f"User message sent: {user_input}")

        if user_input.lower() == "exit":
            self.update_chat("AIm: Goodbye!", spacer=False)
            raise urwid.ExitMainLoop()

        self.chat_manager.send_user_message(
            user_input,
            on_reply_ready=self.on_ai_reply_ready,
            on_error=self.on_ai_error
        )

    def on_ai_reply_ready(self, reply):
        placeholder = self.add_placeholder()
        self.chat_manager.start_typing_effect(placeholder, reply)

    def on_ai_error(self, error_msg):
        self.update_chat(f"AIm: Error: {error_msg}")
        self.chat_manager.typing_in_progress = False

    def add_placeholder(self):
        placeholder = urwid.Text("AIm: ")
        self.chat_box.append(placeholder)
        self.scroll_to_bottom()
        return placeholder

    def periodic_update(self, loop, _):
        if self.chat_manager.typing_in_progress:
            self.typewriter_effect(loop, None)
        loop.set_alarm_in(0.05, self.periodic_update)

    def typewriter_effect(self, loop, user_data):
        # If there's no placeholder or reply, just return
        if self.chat_manager.current_placeholder is None or self.chat_manager.current_reply is None:
            return
        if self.chat_manager.current_placeholder and self.chat_manager.current_reply:
            debug(
                f"Typewriter active: current_index={self.chat_manager.current_index}, "
                f"reply_len={len(self.chat_manager.current_reply)}"
            )

            speed = self.config.typewriter_speed
            if speed == 0:
                # Instant display
                self.chat_manager.current_placeholder.set_text(
                    self.chat_manager.current_placeholder.get_text()[0] + self.chat_manager.current_reply
                )
                debug("Typewriter skipped: full response displayed.")
                self.chat_manager.stop_typing_effect()
                self.scroll_to_bottom()
                return

            if self.chat_manager.current_index < len(self.chat_manager.current_reply):
                current_message = (
                    self.chat_manager.current_placeholder.get_text()[0]
                    + self.chat_manager.current_reply[self.chat_manager.current_index]
                )
                self.chat_manager.current_placeholder.set_text(current_message)
                self.chat_manager.current_index += 1
                self.scroll_to_bottom()
                debug(f"Scroll triggered during typewriting. Current index: {self.chat_manager.current_index}")

                delay = max(0.02, 0.15 - ((speed - 1) * 0.01))
                self.loop.set_alarm_in(delay, self.typewriter_effect)
            else:
                self.chat_manager.stop_typing_effect()
                self.scroll_to_bottom()
                debug("Typewriter effect complete.")

    def update_focus_style(self):
        if self.view.focus_part == "footer":
            self.input_linebox.set_attr_map({None: 'focus_linebox_border'})
            self.chat_linebox.set_attr_map({None: 'normal_linebox_border'})
        else:
            self.input_linebox.set_attr_map({None: 'normal_linebox_border'})
            self.chat_linebox.set_attr_map({None: 'focus_linebox_border'})
