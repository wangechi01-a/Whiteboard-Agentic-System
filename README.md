# Agentic Whiteboard Application
I created this intelligent whiteboard tool to empower remote teams, educators, and learners with a collaborative space that blends traditional drawing with AI Assistant support. By integrating agents like a visual analyzer, document assistant, and tutor, the tool helps users brainstorm, explain, and structure ideas more efficiently—making meetings, planning sessions, and study workflows smarter and more interactive.
## Features

### Core Whiteboard Features
- **Freehand Drawing** - Mouse drawing with adjustable brush size (1-10)
- **Color Palette** - 6 colors: black, red, blue, green, orange, purple
- **Text Tool** - Click anywhere to add text with adjustable font size
- **Eraser** - Remove content by drawing over it
- **Clear Canvas** - Reset entire whiteboard
- **PDF/TXT Loading** - Load and navigate through documents
- **Slide Navigation** - Previous/Next buttons to browse content
- **Full Document Context** - Complete document content available to AI
- **Enhanced Text Display** - Improved formatting and readability

### AI Assistant Features Powered by Google's AI API
- **Multi-Agent System** - 4 specialized AI agents:
  - **Vision Agent**: Analyzes canvas drawings and visual content
  - **Tutor Agent**: Provides educational explanations and learning support
  - **Drawing Agent**: Suggests artistic improvements and drawing tips
  - **Document Agent**: Processes and analyzes loaded documents
- **Conversation Memory** - Remembers chat history and context
- **Canvas Awareness** - AI can "see" what you've drawn
- **Human-in-Loop Fallback** - Suggests human assistance for complex queries
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
