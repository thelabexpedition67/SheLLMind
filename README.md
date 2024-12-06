# SheLLMind

**SheLLMind** is a terminal-based interactive chat application that integrates with the [Ollama](https://ollama.ai/) API to provide a local LLM-based chat experience. It supports session persistence, multiple model selection, scrolling chat history, and various configuration menus—all within the terminal environment.

## Features

- **Local LLM Chat**: Interact with a Large Language Model through the Ollama API on your local machine.
- **Persistent Chat Sessions**: Conversations are automatically saved, allowing you to resume where you left off.
- **History Management**: Browse a list of saved chats, sorted by modification time, and see chat details like creation time, last modified time, and an optional chat name.
- **Multiple Model Selection**: Choose from available Ollama models before starting a new chat, or use the configured default model.
- **Configurable UI**:
  - **Chat**: Send messages, switch focus between chat history and input box, enjoy auto-scrolling and optional typewriter effects.
  - **History Menu**: View previously saved chat sessions with additional metadata (name, creation time, last modified time).
  - **Help Menu**: Display available keyboard shortcuts and commands.
  - **Chat Settings**: Edit the chat name or delete the chat (both history and details).
- **Customizable Keys**: Use various key combinations to navigate, send messages, insert newlines, open menus, switch focus, and more.

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
  - Update config.json with the correct ollama_host and a default model_name.

5. **Prepare Directories**:
  ```bash
  mkdir -p history history_details
  ```

6. **Create configuration**:
  - Create a config.json file inside the root folder with this content:
  ```bash
  {
    "ollama_host": "http://10.20.30.40:11434",
    "model_name": "llama3.1:8b",
    "typewriter_speed": 1
  }
  ```
  Obviously, you need to change the reported example values.

## Running SheLLMind

Start the application:
  ```bash
  python app.py
  ```

You will see a main menu with options:
- **Start Chat**: Begin a new conversation (you’ll choose a model if available).
- **History**: View saved chats, ordered by modification time.
- **Help**: Show keyboard shortcuts and commands.
- **Quit**: Exit the application.

## Keyboard Shortcuts

**In Chat**:
  - **enter**: Send the current message.
  - **ctrl+l**: Insert a newline in the input box.
  - **ctrl+w**: Toggle focus between chat history and input box.
  - **ctrl+o**: Quit the application.
  - **esc**: Return to the main menu.
  - **ctrl+e**: Open the chat settings menu (rename or delete chat).

**Menus**:

Use arrow keys and enter to select menu items.
Press b to go back to the previous menu.

## Directory Structure
  - **app.py**: Entry point.
  - **chat_screen.py**: Chat interface logic.
  - **chat_logic.py**: Interaction with Ollama and state management.
  - **menu.py**: Defines various menus (main, history, help, model, settings).
  - **ui_elements.py**: Custom widgets (e.g., CustomEdit).
  - **config.py**: Loads settings from config.json.
  - **debug.py**: Logging and debugging utilities.
  - **classes/**: Classes.
  
**Data Files**:
  - **history/**: JSON files for conversation messages.
  - **history_details/**: JSON files for metadata (model name, chat name, etc.).

## Customization

- **Configuration**: Edit config.json to change default model or typewriter speed.
- **Keybindings**: Adjust handle_input methods or CustomEdit keypress handling.
- **Extensibility**: Add new menus, features, or logic in separate modules.

## Troubleshooting
- **No Models Found**: Check if Ollama is running and models are listed by ollama list.
- **No Chats in History**: Start a new chat and send a message; it will appear in history on return.
- **Terminal Rendering Issues**: Try a larger terminal or a different terminal emulator.

## License

**SheLLMind** is released under the MIT License.
