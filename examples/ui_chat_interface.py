"""Example: UI Components with RapidAI.

This example demonstrates:
1. Using pre-built chat interface
2. Custom themes and styling
3. File upload integration
4. Serving HTML pages with @page decorator
5. Real-time chat with LLM
"""

from rapidai import App, LLM
from rapidai.ui import page, ChatInterface, get_chat_template
from rapidai.memory import ConversationMemory

app = App(title="UI Chat Interface Example")
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()


# Default chat interface
@app.route("/")
@page("/")
async def index():
    """Serve default chat interface."""
    return get_chat_template(title="RapidAI Chat", theme="dark")


# Light theme chat
@app.route("/light")
@page("/light")
async def light_theme():
    """Serve chat with light theme."""
    return get_chat_template(title="Light Theme Chat", theme="light")


# Custom themed chat
@app.route("/custom")
@page("/custom")
async def custom_theme():
    """Serve chat with custom configuration."""
    config = ChatInterface(
        title="Custom Chat Bot",
        theme="dark",
        show_timestamps=True,
        enable_markdown=True,
        enable_file_upload=False,
        placeholder="Ask me anything...",
        max_height="700px",
        avatar_user="👤",
        avatar_assistant="🤖",
    )

    return get_chat_template(config=config)


# Chat with file upload
@app.route("/upload")
@page("/upload")
async def chat_with_upload():
    """Serve chat interface with file upload enabled."""
    config = ChatInterface(
        title="Chat with File Upload",
        theme="dark",
        enable_file_upload=True,
        placeholder="Upload a file or ask a question...",
    )

    return get_chat_template(config=config)


# Chat API endpoint (stateless)
@app.route("/chat", methods=["POST"])
async def chat(message: str):
    """Simple chat endpoint without memory."""
    response = await llm.complete(message)
    return {"response": response}


# Chat API with memory
@app.route("/api/chat", methods=["POST"])
async def chat_with_memory(user_id: str, message: str):
    """Chat endpoint with conversation memory."""
    # Add user message
    memory.add_message(user_id, "user", message)

    # Get conversation history
    history = memory.get_history(user_id, limit=10)

    # Generate response
    response = await llm.chat(history)

    # Add assistant response
    memory.add_message(user_id, "assistant", response)

    return {"response": response}


# Clear conversation
@app.route("/api/clear", methods=["POST"])
async def clear_conversation(user_id: str):
    """Clear conversation history."""
    memory.clear(user_id)
    return {"message": "Conversation cleared", "user_id": user_id}


# File upload handler
@app.route("/api/upload", methods=["POST"])
async def upload_file(filename: str, content: str):
    """Handle file upload (simplified example)."""
    # In real app, would process file content
    # For now, just use it as context

    summary = await llm.complete(f"Summarize this file content:\n\n{content[:1000]}")

    return {"filename": filename, "summary": summary, "status": "processed"}


# Health check
@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ui-chat-interface"}


# Demo page with links
@app.route("/demo")
@page("/demo")
async def demo():
    """Demo page with links to different chat interfaces."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RapidAI UI Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #0a0a0a;
                color: #ffffff;
            }
            h1 {
                color: #00ffff;
                margin-bottom: 30px;
            }
            .links {
                display: grid;
                gap: 15px;
            }
            a {
                display: block;
                padding: 20px;
                background: #1a1a1a;
                color: #00ffff;
                text-decoration: none;
                border-radius: 8px;
                border: 1px solid #333;
                transition: all 0.2s;
            }
            a:hover {
                background: #2a2a2a;
                transform: translateX(5px);
            }
            .description {
                color: #999;
                font-size: 0.9em;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <h1>🚀 RapidAI UI Components Demo</h1>
        <div class="links">
            <a href="/">
                <div>Default Chat Interface</div>
                <div class="description">Dark theme with default settings</div>
            </a>
            <a href="/light">
                <div>Light Theme Chat</div>
                <div class="description">Chat interface with light color scheme</div>
            </a>
            <a href="/custom">
                <div>Custom Themed Chat</div>
                <div class="description">Customized configuration and appearance</div>
            </a>
            <a href="/upload">
                <div>Chat with File Upload</div>
                <div class="description">Upload files and chat about them</div>
            </a>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    print("UI Chat Interface Example")
    print("=" * 50)
    print("\nChat Interfaces:")
    print("  /demo    - Demo page with all options")
    print("  /        - Default dark theme")
    print("  /light   - Light theme")
    print("  /custom  - Custom configuration")
    print("  /upload  - With file upload")
    print("\nAPI Endpoints:")
    print("  POST /chat         - Simple chat")
    print("  POST /api/chat     - Chat with memory")
    print("  POST /api/clear    - Clear conversation")
    print("  POST /api/upload   - Upload file")
    print("\nOpen in browser:")
    print("  http://localhost:8000/demo")
    print("\nStarting server on http://localhost:8000")
    print("=" * 50)

    app.run(port=8000)
