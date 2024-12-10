# SheLLMind

**SheLLMind** is a terminal-based interactive chat application that integrates with the [Ollama](https://ollama.ai/) API to provide a local LLM-based chat experience. It supports session persistence, multiple model selection, scrolling chat history, and various configuration menus, all within the terminal environment.

I built this software just because I wanted to run it on my old green CRT monitor. It's all about the nostalgia of typing away in a dark room with the gentle glow of phosphor characters dancing across the screen.

**Modern AI, retro style.**

![](http://thelabexpedition67.com/vectors/github/shellmind/shellmind_1s.jpg)

## Features

- **Local LLM Chat**: Interact with a Large Language Model through the Ollama API on your local machine.
- **Persistent Chat Sessions**: Conversations are automatically saved, allowing you to resume where you left off.
- **History Management**: Browse a list of saved chats, sorted by modification time, and see chat details like creation time, last modified time, and an optional chat name.
- **Multiple Model Selection**: Choose from available Ollama models before starting a new chat, or use the configured default model.
- **UI**:
  - **Chat**: Send messages, switch focus between chat history and input box, enjoy auto-scrolling and optional typewriter effects.
  - **History Menu**: View previously saved chat sessions with additional metadata (name, creation time, last modified time).
  - **Help Menu**: Display available keyboard shortcuts and commands.
  - **Chat Settings**: Edit the chat name or delete the chat (both history and details).
  - **System Settings**: Edit the system settings like the Ollama API url and the default model with ease.
- **Shortcuts Keys**: Use various key combinations to navigate, send messages, insert newlines, open menus, switch focus, and more.

## Requirements

- **Python 3.9+**: Ensure you have a compatible Python version.
- **[Urwid](https://urwid.org/)**: Required for terminal UI rendering.
- **[Ollama](https://ollama.ai/) Server**: Requires Ollama to be installed and running locally with accessible models.
- **File System Access**:
  - `history` directory to store conversation JSON files.
  - `history_details` directory to store metadata for each chat.
- **`config.json`**: Holds basic configuration like `ollama_host`, `model_name`, and `typewriter_speed`.

The application is primarily tested on macOS/Linux. Windows users may consider using WSL or a similar environment.

## Installation & Setup

1. **Clone the Repository**:
  ```bash
  git clone https://github.com/thelabexpedition67/SheLLMind.git
  cd SheLLMind
  ```
2. **Create a Virtual Environment (Recommended)**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # macOS/Linux
  # For Windows: venv\Scripts\activate
  ```
3. **Install Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
4. **Set Up Ollama**:

  - Install Ollama and ensure it’s running.
  - Pull or prepare your models with ollama pull modelname.

5. **Prepare Directories**:
  ```bash
  mkdir -p history history_details
  ```
6. **Set permissions**:
  ```bash
  chmod +x run.sh
  ```  
## Running SheLLMind

Start the application:
  ```bash
  python main.py
  ```
  or (on Linux)
  ```bash
  ./run.sh
  ```
You will see a main menu with options:
- **Start Chat**: Begin a new conversation (you’ll choose a model if available).
- **History**: View saved chats, ordered by modification time.
- **Configuration**: Configure the Ollama API url and other parameters (You must do this on the first run).
- **Help**: Show keyboard shortcuts and commands.
- **About**: Show about.
- **Quit**: Exit the application.

## Keyboard Shortcuts

**In Chat**:
  - **enter**: Send the current message.
  - **ctrl+l**: Insert a newline in the input box.
  - **ctrl+w**: Toggle focus between chat history and input box.
  - **ctrl+o**: Quit the application.
  - **esc**: Return to the main menu.
  - **ctrl+e**: Open the chat settings menu (rename or delete chat).
  - **alt+h**: Show keyboard shortcuts and commands.

**Menus**:

Use arrow keys and enter to select menu items.
Press b to go back to the previous menu.

**Important: Navigating Long Responses**

When the AI response is very long, the chat interface pauses scrolling once the first line of the response reaches the top of the screen. This is intentional and ensures that you can start reading the response from the beginning without it being scrolled too quickly out of view.

How to Navigate Using the Keyboard

1. **Switch Focus to Chat History**:
   - Press **`Ctrl+W`** to toggle the focus from the input box to the chat history.

2. **Scroll Through the Response**:
   - Use the **`Up`** and **`Down`** arrow keys to navigate through the response at your own pace.

3. **Return to the Input Box**:
   - When ready to type a new message, press **`Ctrl+W`** again to switch focus back to the input box.

**Using the Mouse**

If you prefer using a **mouse**, you can:
- Click on the chat history and scroll through the response.
- Click back on the input box to resume typing.

This behavior ensures that long responses are fully visible from the start, giving you time to read and scroll as needed.

## Directory Structure
  - **main.py**: Entry point.
  - **chat_screen.py**: Chat interface logic.
  - **chat_logic.py**: Interaction with Ollama and state management.
  - **menu.py**: Defines various menus (main, history, help, model, settings).
  - **ui_elements.py**: Custom widgets (e.g., CustomEdit).
  - **config.py**: Loads settings from config.json.
  - **debug.py**: Logging and debugging utilities.
  - **classes/**: Menu elements Classes.
  
**Data Files**:
  - **history/**: JSON files for conversation messages.
  - **history_details/**: JSON files for metadata (model name, chat name, etc.).

## Troubleshooting
- **No Models Found**: Check if Ollama is running and models are listed by ollama list.
- **No Chats in History**: Start a new chat and send a message; it will appear in history on return.
- **Terminal Rendering Issues**: Try a larger terminal or a different terminal emulator.

## Development Notice

This software is currently in **open development** and continues to evolve with ongoing improvements. It may contain bugs or incomplete features. 

I welcome feedback and will gladly work on resolving issues when possible, balancing updates with my available free time.

Feel free to contribute to the project if you’d like! Your ideas, code contributions, and feedback are all greatly appreciated.

## License

**SheLLMind** is released under the MIT License.