# Agentic Whiteboard Application
This is an intelligent whiteboard application that combines traditional drawing tools with AI agents powered by Google Gemini for assistance and document analysis.
## Features

### Core Whiteboard Features
- **Freehand Drawing** - Mouse drawing with adjustable brush size (1-10)
- **Color Palette** - 6 colors: black, red, blue, green, orange, purple
- **Text Tool** - Click anywhere to add text with adjustable font size
- **Eraser** - Remove content by drawing over it
- **Clear Canvas** - Reset entire whiteboard

### Document Features
- **PDF/TXT Loading** - Load and navigate through documents
- **Slide Navigation** - Previous/Next buttons to browse content
- **Full Document Context** - Complete document content available to AI
- **Enhanced Text Display** - Improved formatting and readability

### AI Assistant Features
- **Google Gemini Integration** - Powered by Google's AI API
- **Multi-Agent System** - 4 specialized AI agents:
  - **Vision Agent**: Analyzes canvas drawings and visual content
  - **Tutor Agent**: Provides educational explanations and learning support
  - **Drawing Agent**: Suggests artistic improvements and drawing tips
  - **Document Agent**: Processes and analyzes loaded documents
- **Conversation Memory** - Remembers chat history and context
- **Canvas Awareness** - AI can "see" what you've drawn
- **Human-in-Loop Fallback** - Suggests human assistance for complex queries

### Additional Features
- **Screenshot Capture** - Save full window as PNG with timestamp
- **Centered Window** - Automatically centers on screen


## Installation

1. **Install Python packages:**
```bash
pip install -r requirements.txt
```

2. **Set up Google API Key:**
Create a `.env` file in the project directory:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

3. **Run the application:**
```bash
python app.py
```

## Usage

### Drawing
1. **Freehand**: Simply click and drag to draw
2. **Colors**: Click color squares on the left to change color
3. **Text**: Click "Text" button, then click canvas to add text
4. **Brush Size**: Use slider at bottom to adjust thickness

### Documents
1. **Load**: Click "Doc" button to load PDF or TXT files
2. **Navigate**: Use buttons to browse through content
3. **AI Analysis**: Ask AI questions about the loaded document

### AI Chat
1. **Initialize**: Click "AI Chat" then "Initialize AI"
2. **Chat**: Type questions in the input box at top
3. **Context**: AI knows about your drawings and loaded documents
4. **Memory**: AI remembers previous conversation

### Screenshots
- Click "Save" to capture the entire application window

## Example AI Queries
- "What do you see on my canvas?"
- "Explain this concept I'm drawing"
- "How can I improve my diagram?"
- "Summarize the key points from the loaded document"
- "Help me understand page 3 of the PDF"

### AI System
- **LangGraph Framework**: Manages agent workflows and routing
- **Google Gemini API**: Provides intelligent responses
- **Smart Routing**: Automatically selects appropriate agent based on query
- **Fallback System**: Built-in tools activate if API fails
- **Memory Integration**: Maintains conversation context

