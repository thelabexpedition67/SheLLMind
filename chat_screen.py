import urwid
from debug import debug
from ui_elements import CustomEdit
import itertools
import time
import re

class ChatScreen:
    def __init__(self, loop, chat_manager, config, on_quit):
        self.loop = loop
        self.chat_manager = chat_manager
        self.config = config
        self.on_quit = on_quit

        self.status="idle"
        self.default_status="Type your message"

        self.chat_box = urwid.SimpleFocusListWalker([])
        self.chat_list = urwid.ListBox(self.chat_box)

        chat_list_attr = urwid.AttrMap(self.chat_list, 'normal_content')

        self.input_box = CustomEdit([("who", "You"),": "], multiline=True)
        input_box_attr = urwid.AttrMap(self.input_box, 'normal_content')

        # Regular expression to extract only the model name
        model_full_name = chat_manager.model_name
        match = re.search(r'[^/]+$', model_full_name)  # Matches the last part after "/"
        model_name = match.group(0) if match else model_full_name

        self.chat_linebox = urwid.LineBox(chat_list_attr, title=model_name)
        self.chat_linebox = urwid.AttrMap(self.chat_linebox, 'normal_linebox_border')

        input_linebox = urwid.LineBox(input_box_attr, title=self.default_status)
        self.input_linebox = urwid.AttrMap(input_linebox, 'normal_linebox_border')

        self.view = urwid.Frame(
            self.chat_linebox,
            footer=self.input_linebox
        )
        self.view.set_focus("footer")

        self.input_box.set_message_handler(self.send_message)
        self.loop.set_alarm_in(0.05, self.periodic_update)

        self.is_animating = False  # State to track animation
        self.current_animation_title = ""  # Track current title animation state

        # If we have a pre-loaded conversation, display it
        #message_count = 0
        for msg in self.chat_manager.conversation_history:
            if msg["role"] == "user":
                text = [('who', 'You'),": ", ('user_message', msg['content'])]
            else:
                text = [('who', 'AIm'),": ", ('ai_message', msg['content'])]
            self.update_chat(text)
            #message_count += 1
            #if message_count % 2 == 0:
            #    self.chat_box.append(urwid.AttrMap(urwid.Divider("-"), "divider"))
            #self.chat_box.append(urwid.AttrMap(urwid.Divider("-"), "divider"))

        self.update_focus_style()

    def widget(self):
        return self.view

    def update_chat(self, new_message, spacer=True):
        """Safely update the chat and scroll to bottom."""
        def safe_update(loop, _):
            if spacer:
                self.chat_box.append(urwid.AttrMap(urwid.Divider("-"), "divider"))
            self.chat_box.append(urwid.AttrMap(urwid.Text(new_message), "normal_text"))
            self.scroll_to_bottom()

        self.loop.set_alarm_in(0, safe_update)

    def update_status(self, new_status):
        """Update the LineBox title only if it has changed."""
        # Check if the new title is different
        if getattr(self, "_current_title", None) != new_status:
            self._current_title = new_status  # Store the new title
            self.input_linebox.original_widget.set_title(new_status)
            debug(f"Title updated to: {new_status}")

    def start_status_animation(self, base_status):
        """Start animating the chat title if not already active."""
        if self.is_animating:
            return  # Avoid starting the animation again if it's already active

        self.is_animating = True
        self.current_animation_status = base_status
        if self.status=="sent":
            self.loader = itertools.cycle(["   ",".  ", ".. ", "..."])  # Infinite thinker
        else:
            self.loader = itertools.cycle([" |", " /", " -", " \\"])  # Infinite spinner

        self.loop.set_alarm_in(0.1, self.animate_status)

    def animate_status(self, loop=None, user_data=None):
        """Animate the chat title with a spinner."""
        if not self.is_animating:
            return  # Stop the animation if it is no longer active

        next_loader = next(self.loader)
        new_status = f"{self.current_animation_status}{next_loader}"

        # Update only if the title has actually changed
        if new_status != self.default_status:
            self.update_status(new_status)
            debug(f"Chat status updated to: {new_status}")

        # Schedule the next update
        self.loop.set_alarm_in(0.1, self.animate_status)

    def stop_status_animation(self):
        """Stop the status animation and reset the title."""
        if not self.is_animating:
            return  # Avoid redundant calls
        self.status="idle"
        self.is_animating = False
        self.update_status(self.default_status)
        debug("Status animation stopped.")

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

        #self.update_chat(f"You: {user_input}")
        self.update_chat([('who', 'You'),": ", ('user_message', user_input)])
        
        self.input_box.set_edit_text("")
        self.status="sent"
        self.start_status_animation("AIm is Thinking")
        debug(f"User message sent: {user_input}")

        if user_input.lower() == "exit":
            self.update_chat("AIm: Goodbye!", spacer=False)
            raise self.on_quit()

        self.chat_manager.send_user_message(
            user_input,
            on_reply_ready=self.on_ai_reply_ready,
            on_error=self.on_ai_error
        )

    def on_ai_reply_ready(self, reply):
        """Handle when the AI reply is ready to process."""
        self.stop_status_animation()
        self.status="type"
        self.start_status_animation("AIm is Typing")
        placeholder = self.add_placeholder()
        self.chat_manager.start_typing_effect(placeholder, reply)

    def on_ai_error(self, error_msg):
        """Handle AI errors safely by scheduling the update in the main loop."""
        def safe_update(loop, _):
            self.update_chat(f"AIm: Error: {error_msg}")
            self.stop_status_animation()

        self.loop.set_alarm_in(0, safe_update)

    def add_placeholder(self):
        self.chat_box.append(urwid.AttrMap(urwid.Divider("-"), "divider"))
        placeholder = urwid.Text("")
        self.chat_box.append(placeholder)
        self.scroll_to_bottom()
        return placeholder

    def periodic_update(self, loop, _):
        if self.chat_manager.typing_in_progress:
            self.typewriter_effect(loop, None)
        else:
            self.stop_status_animation()
        loop.set_alarm_in(0.05, self.periodic_update)


    def typewriter_effect(self, loop, user_data):
        """Non-blocking typewriter effect using time checks."""
        if self.chat_manager.current_placeholder is None or self.chat_manager.current_reply is None:
            return

        # Initialize or retrieve the last update time
        if not hasattr(self, 'last_type_time'):
            self.last_type_time = time.time()

        # Delay calculation: 1 (moderate) to 10 (nearly instant)
        # Bias allows customization for overall speed adjustments
        BIAS = 0.12  # Adjust this value: lower = faster overall, higher = slower

        speed = self.config.typewriter_speed
        delay = max(0.001, (0.1 / speed) * BIAS)  # Ensure a minimum delay of 1ms

        # Check elapsed time
        if time.time() - self.last_type_time >= delay:
            self.last_type_time = time.time()  # Reset timer

            if self.chat_manager.current_index < len(self.chat_manager.current_reply):
                # Construct the current message
                current_message = self.chat_manager.current_reply[: self.chat_manager.current_index + 1]
                full_text = [('who', 'AIm'), ": ", ('ai_message', current_message)]

                # Update placeholder text
                self.chat_manager.current_placeholder.set_text(full_text)
                self.chat_manager.current_index += 1
                self.scroll_to_bottom()

                # Reschedule without blocking
                self.loop.set_alarm_in(0, self.typewriter_effect)
            else:
                # Typing complete: display full message
                full_text = [('who', 'AIm'), ": ", ('ai_message', self.chat_manager.current_reply)]
                self.chat_manager.current_placeholder.set_text(full_text)
                self.chat_manager.stop_typing_effect()
                self.scroll_to_bottom()
                self.stop_status_animation()

                # Clean up the timer
                del self.last_type_time

    def update_focus_style(self):
        """Update border styles based on focus."""
        if self.view.focus_part == "footer":
            self.input_linebox.set_attr_map({None: 'focus_linebox_border'})
            self.chat_linebox.set_attr_map({None: 'normal_linebox_border'})
        else:
            self.input_linebox.set_attr_map({None: 'normal_linebox_border'})
            self.chat_linebox.set_attr_map({None: 'focus_linebox_border'})