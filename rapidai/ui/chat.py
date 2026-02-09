"""Chat interface components for RapidAI."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatInterface:
    """Configuration for chat interface."""

    title: str = "RapidAI Chat"
    theme: str = "dark"
    show_timestamps: bool = True
    enable_markdown: bool = True
    enable_file_upload: bool = False
    placeholder: str = "Type your message..."
    max_height: str = "600px"
    avatar_user: str = "👤"
    avatar_assistant: str = "🤖"


def get_chat_template(config: Optional[ChatInterface] = None) -> str:
    """Generate HTML template for chat interface.

    Args:
        config: Optional chat interface configuration

    Returns:
        HTML string
    """
    if config is None:
        config = ChatInterface()

    theme_colors = {
        "dark": {
            "bg": "#0a0a0a",
            "bg_secondary": "#1a1a1a",
            "text": "#ffffff",
            "text_secondary": "#999999",
            "border": "#333333",
            "user_bg": "#00ffff",
            "user_text": "#000000",
            "assistant_bg": "#2a2a2a",
            "assistant_text": "#ffffff",
            "input_bg": "#1a1a1a",
        },
        "light": {
            "bg": "#ffffff",
            "bg_secondary": "#f5f5f5",
            "text": "#000000",
            "text_secondary": "#666666",
            "border": "#dddddd",
            "user_bg": "#007bff",
            "user_text": "#ffffff",
            "assistant_bg": "#f0f0f0",
            "assistant_text": "#000000",
            "input_bg": "#ffffff",
        },
    }

    colors = theme_colors.get(config.theme, theme_colors["dark"])

    markdown_script = ""
    if config.enable_markdown:
        markdown_script = """
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            function renderMarkdown(text) {
                return marked.parse(text);
            }
        </script>
        """
    else:
        markdown_script = """
        <script>
            function renderMarkdown(text) {
                return text.replace(/\\n/g, '<br>');
            }
        </script>
        """

    file_upload_html = ""
    if config.enable_file_upload:
        file_upload_html = """
        <label class="file-upload-btn" for="file-input">
            📎
            <input type="file" id="file-input" style="display: none;">
        </label>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: {colors['bg']};
            color: {colors['text']};
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .chat-container {{
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 1rem;
        }}

        .chat-header {{
            padding: 1.5rem;
            background: {colors['bg_secondary']};
            border-radius: 12px 12px 0 0;
            border-bottom: 1px solid {colors['border']};
        }}

        .chat-header h1 {{
            font-size: 1.5rem;
            font-weight: 600;
        }}

        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            background: {colors['bg_secondary']};
            max-height: {config.max_height};
        }}

        .message {{
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
            animation: fadeIn 0.3s ease-in;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .message-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        }}

        .message-content {{
            flex: 1;
            min-width: 0;
        }}

        .message-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }}

        .message-role {{
            font-weight: 600;
            font-size: 0.875rem;
        }}

        .message-timestamp {{
            font-size: 0.75rem;
            color: {colors['text_secondary']};
        }}

        .message-text {{
            padding: 1rem;
            border-radius: 12px;
            line-height: 1.5;
            word-wrap: break-word;
        }}

        .message-text p {{
            margin-bottom: 0.5rem;
        }}

        .message-text p:last-child {{
            margin-bottom: 0;
        }}

        .message-text code {{
            background: rgba(0, 0, 0, 0.2);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
        }}

        .message-text pre {{
            background: rgba(0, 0, 0, 0.3);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 0.5rem 0;
        }}

        .message-text pre code {{
            background: none;
            padding: 0;
        }}

        .message.user .message-avatar {{
            background: {colors['user_bg']};
            color: {colors['user_text']};
        }}

        .message.user .message-text {{
            background: {colors['user_bg']};
            color: {colors['user_text']};
        }}

        .message.assistant .message-avatar {{
            background: {colors['assistant_bg']};
            color: {colors['assistant_text']};
        }}

        .message.assistant .message-text {{
            background: {colors['assistant_bg']};
            color: {colors['assistant_text']};
        }}

        .chat-input {{
            padding: 1.5rem;
            background: {colors['bg_secondary']};
            border-radius: 0 0 12px 12px;
            border-top: 1px solid {colors['border']};
        }}

        .input-wrapper {{
            display: flex;
            gap: 0.75rem;
            align-items: flex-end;
        }}

        .file-upload-btn {{
            padding: 0.75rem;
            background: {colors['input_bg']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.25rem;
            transition: all 0.2s;
        }}

        .file-upload-btn:hover {{
            background: {colors['assistant_bg']};
        }}

        #message-input {{
            flex: 1;
            padding: 0.875rem 1rem;
            background: {colors['input_bg']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            color: {colors['text']};
            font-size: 1rem;
            font-family: inherit;
            resize: none;
            max-height: 150px;
            min-height: 48px;
        }}

        #message-input:focus {{
            outline: none;
            border-color: {colors['user_bg']};
        }}

        #send-button {{
            padding: 0.875rem 1.5rem;
            background: {colors['user_bg']};
            color: {colors['user_text']};
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s;
        }}

        #send-button:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}

        #send-button:active {{
            transform: translateY(0);
        }}

        #send-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .loading {{
            display: none;
            padding: 1rem;
            text-align: center;
            color: {colors['text_secondary']};
        }}

        .loading.active {{
            display: block;
        }}

        .loading-dots {{
            display: inline-block;
        }}

        .loading-dots::after {{
            content: '.';
            animation: dots 1.5s steps(3, end) infinite;
        }}

        @keyframes dots {{
            0%, 20% {{ content: '.'; }}
            40% {{ content: '..'; }}
            60%, 100% {{ content: '...'; }}
        }}

        ::-webkit-scrollbar {{
            width: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: {colors['bg']};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {colors['border']};
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {colors['text_secondary']};
        }}
    </style>
    {markdown_script}
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>{config.title}</h1>
        </div>

        <div class="chat-messages" id="messages">
            <!-- Messages will be added here -->
        </div>

        <div class="loading" id="loading">
            <span class="loading-dots">Thinking</span>
        </div>

        <div class="chat-input">
            <div class="input-wrapper">
                {file_upload_html}
                <textarea
                    id="message-input"
                    placeholder="{config.placeholder}"
                    rows="1"
                ></textarea>
                <button id="send-button">Send</button>
            </div>
        </div>
    </div>

    <script>
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const loadingIndicator = document.getElementById('loading');

        // Auto-resize textarea
        messageInput.addEventListener('input', function() {{
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        }});

        // Send on Enter (Shift+Enter for new line)
        messageInput.addEventListener('keydown', function(e) {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }});

        sendButton.addEventListener('click', sendMessage);

        function addMessage(role, content, timestamp = new Date()) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{role}}`;

            const avatar = role === 'user' ? '{config.avatar_user}' : '{config.avatar_assistant}';
            const roleName = role === 'user' ? 'You' : 'Assistant';

            const timestampStr = {'`${timestamp.toLocaleTimeString()}`' if config.show_timestamps else '""'};
            const timestampHtml = timestampStr ? `<span class="message-timestamp">${{timestampStr}}</span>` : '';

            messageDiv.innerHTML = `
                <div class="message-avatar">${{avatar}}</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-role">${{roleName}}</span>
                        ${{timestampHtml}}
                    </div>
                    <div class="message-text">${{renderMarkdown(content)}}</div>
                </div>
            `;

            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}

        async function sendMessage() {{
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage('user', message);
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // Disable input
            sendButton.disabled = true;
            messageInput.disabled = true;
            loadingIndicator.classList.add('active');

            try {{
                // Send to backend
                const response = await fetch('/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ message }}),
                }});

                const data = await response.json();

                // Add assistant response
                addMessage('assistant', data.response || data.message || 'No response');
            }} catch (error) {{
                addMessage('assistant', 'Sorry, an error occurred: ' + error.message);
            }} finally {{
                // Re-enable input
                sendButton.disabled = false;
                messageInput.disabled = false;
                loadingIndicator.classList.remove('active');
                messageInput.focus();
            }}
        }}

        // Focus input on load
        messageInput.focus();

        // Welcome message
        addMessage('assistant', 'Hello! How can I help you today?');
    </script>
</body>
</html>
    """

    return html
