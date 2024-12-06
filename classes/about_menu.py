import urwid

class AboutMenu:
    def __init__(self, on_back):
        self.on_back = on_back
        text_content = (
            "SheLLMind - A Retro Terminal Chat Experience\n\n"
            "Created by TheLabExpedition67 (GitHub: https://github.com/TheLabExpedition67)\n"
            "Website: http://thelabexpedition67.com/\n\n"
            "Why SheLLMind?\n"
            "I built this software just because I wanted to run it on my old green CRT monitor.\n"
            "It's all about the nostalgia of typing away in a dark room with the gentle glow of\n"
            "phosphor characters dancing across the screen. Modern AI, retro style.\n\n"
            "Press 'esc' to return to the main menu."
        )
        text_widget = urwid.Text(text_content, align='center')
        filler = urwid.Filler(text_widget, 'top')
        self.view = urwid.LineBox(filler, title="About ShellMind")

    def widget(self):
        return self.view

    def handle_input(self, key):
        if key == 'esc':
            self.on_back()