# Remote Agent: AI-Powered Android TV Controller

Remote Agent is an intelligent Android TV remote control system powered by AI agents. It enables users to control their Android TV devices using natural language commands, automatically planning and executing sequences of actions to accomplish complex tasks.

## 🌟 Features

- **Natural Language Control**: Control your Android TV with simple voice or text commands
- **AI-Powered Planning**: Automatically determines the optimal sequence of actions to achieve your goal
- **Multi-Platform Support**: Find where your favorite movies and TV shows are available
- **YouTube Integration**: Search and play YouTube videos directly on your TV
- **Smart Recommendations**: Get suggestions for similar content based on your preferences
- **Remote Control Simulation**: Send key codes to control volume, navigation, playback, and more

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- An Android TV device with Android Debug Bridge (ADB) enabled (i use test function for testing without android tv)
- Groq API key for AI capabilities

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Surajdusane/tv-agent.git
   cd tv-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or if using uv:
   ```bash
   uv sync
   ```

3. Set up your environment variables in `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Configure your TV settings in `config.json`:
   ```json
   {
     "tv_ip": "10.34.76.78",
     "certfile": "cert.pem",
     "keyfile": "key.pem",
     "client_name": "MyPythonClient"
   }
   ```

### Usage

Run the main application:
```bash
python main.py 
```
or

```bash
uv run main.py 
```

The system will process the default task "i want to watch movie war". To customize the task, modify the `initial_state` in `main.py`:
```python
initial_state = {"current_task": "your command here", "task_number": 0}
```

Example commands:
- "Play romantic songs"
- "Find movies similar to Inception"
- "Increase volume"
- "Watch the latest trailer of Avengers"

## 🧠 How It Works

Remote Agent uses a sophisticated AI agent architecture built with LangGraph:

### Core Components

1. **Planner Agent**: Analyzes user requests and creates a plan of action
2. **Task Executors**: Specialized tools for different functions:
   - `get_key`: Determines appropriate remote control key codes
   - `send_code`: Sends key codes to the TV
   - `get_youtube_query`: Creates search queries for YouTube
   - `get_youtube_link`: Finds YouTube video links
   - `send_link`: Sends video links to the TV
   - `get_platform`: Finds where content is available
   - `get_recommendations`: Suggests similar content
   - `set_show_name`: Extracts show/movie names from requests

### Workflow

1. User provides a natural language command
2. Planner analyzes the request and creates a sequence of tool executions
3. Each tool in the sequence processes the request and updates the state
4. Results are executed on the Android TV device
5. Process continues until the task is complete

## 🔧 Supported Actions

- Volume control (up, down, mute)
- Navigation (up, down, left, right, select)
- Media controls (play, pause, home, back)
- Power controls
- YouTube video search and playback
- Content discovery and recommendations
- Platform information for movies/TV shows

## 📁 Project Structure

```
final-remote/
├── agent_tools/           # Specialized AI tools
├── androidtv_remote_certs/ # TV connection certificates
├── config.json            # TV connection settings
├── main.py                # Entry point
├── pyproject.toml         # Dependencies
└── tools.json             # Tool mappings and documentation
```

## 🛠️ Configuration

### TV Connection

Update `config.json` with your Android TV's IP address and certificate paths:
```json
{
  "tv_ip": "YOUR_TV_IP_ADDRESS",
  "certfile": "path/to/cert.pem",
  "keyfile": "path/to/key.pem",
  "client_name": "YourClientName"
}
```

### API Keys

Set your Groq API key in `.env`:
```env
GROQ_API_KEY=your_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the agent framework
- [Groq](https://groq.com/) for fast AI inference
- [androidtvremote2](https://github.com/tronikos/androidtvremote2) for Android TV control
- [JustWatch](https://www.justwatch.com/) for content availability information