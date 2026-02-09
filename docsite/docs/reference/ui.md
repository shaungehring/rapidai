# UI Components API Reference

Complete API reference for RapidAI's UI components.

## Classes

### ChatInterface

```python
@dataclass
class ChatInterface:
    title: str = "RapidAI Chat"
    theme: str = "dark"
    show_timestamps: bool = True
    enable_markdown: bool = True
    enable_file_upload: bool = False
    placeholder: str = "Type your message..."
    max_height: str = "600px"
    avatar_user: str = "👤"
    avatar_assistant: str = "🤖"
```

Configuration for chat interface.

**Attributes:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | `"RapidAI Chat"` | Chat interface title |
| `theme` | `str` | `"dark"` | Theme name (dark/light) |
| `show_timestamps` | `bool` | `True` | Show message timestamps |
| `enable_markdown` | `bool` | `True` | Enable markdown rendering |
| `enable_file_upload` | `bool` | `False` | Enable file upload button |
| `placeholder` | `str` | `"Type your message..."` | Input placeholder text |
| `max_height` | `str` | `"600px"` | Maximum chat height |
| `avatar_user` | `str` | `"👤"` | User avatar emoji |
| `avatar_assistant` | `str` | `"🤖"` | Assistant avatar emoji |

**Example:**

```python
from rapidai.ui import ChatInterface

config = ChatInterface(
    title="Customer Support",
    theme="light",
    show_timestamps=True,
    enable_markdown=True,
    enable_file_upload=True,
    placeholder="How can we help?",
    max_height="800px",
    avatar_user="😊",
    avatar_assistant="🤝"
)
```

## Functions

### get_chat_template

```python
def get_chat_template(
    config: Optional[ChatInterface] = None,
    title: Optional[str] = None,
    theme: Optional[str] = None,
    **kwargs
) -> str
```

Generate HTML template for chat interface.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `ChatInterface` | `None` | Chat interface configuration |
| `title` | `str` | `None` | Chat title (shorthand) |
| `theme` | `str` | `None` | Theme name (shorthand) |
| `**kwargs` | - | - | Additional ChatInterface parameters |

**Returns:** `str` - Complete HTML page as string

**Usage patterns:**

```python
# Default configuration
html = get_chat_template()

# With custom title and theme
html = get_chat_template(title="My Chat", theme="light")

# With full configuration
config = ChatInterface(
    title="Support Bot",
    theme="dark",
    enable_file_upload=True
)
html = get_chat_template(config=config)

# With kwargs
html = get_chat_template(
    title="AI Assistant",
    theme="light",
    placeholder="Ask me anything...",
    enable_markdown=True
)
```

**Template structure:**

The generated HTML includes:
- Responsive layout with flexbox
- Auto-resizing textarea
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Loading indicator
- Auto-scroll to latest message
- Markdown rendering (optional)
- File upload (optional)
- Custom theme colors
- Smooth animations

**Default API endpoint:**

The template expects a POST endpoint at `/chat` that accepts:

```json
{
  "message": "user message"
}
```

And returns:

```json
{
  "response": "assistant response"
}
```

**Example:**

```python
from rapidai import App
from rapidai.ui import get_chat_template

app = App()

@app.route("/")
async def index():
    return get_chat_template(
        title="My AI Chat",
        theme="dark"
    )

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    # Process message
    return {"response": "Hello!"}
```

## Decorators

### @page

```python
def page(route: str) -> Callable
```

Decorator to serve HTML content with proper content type.

**Parameters:**

- `route` (`str`) - Route path (informational, not used for routing)

**Returns:** Decorator function that wraps async handlers

**Behavior:**

The decorator:
1. Calls the wrapped function to get HTML content
2. Wraps the HTML in a proper HTTP response:
   ```python
   {
       "status": 200,
       "headers": {"Content-Type": "text/html; charset=utf-8"},
       "body": html_content
   }
   ```

**Example:**

```python
from rapidai import App
from rapidai.ui import page, get_chat_template

app = App()

@app.route("/")
@page("/")
async def index():
    return get_chat_template()

@app.route("/dashboard")
@page("/dashboard")
async def dashboard():
    return "<h1>Dashboard</h1>"
```

**Without decorator:**

```python
# Manual approach (not recommended)
@app.route("/")
async def index():
    html = get_chat_template()
    return {
        "status": 200,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": html
    }
```

## Themes

### Built-in Themes

#### Dark Theme

```python
{
    "bg": "#0a0a0a",
    "bg_secondary": "#1a1a1a",
    "text": "#ffffff",
    "text_secondary": "#999999",
    "border": "#333333",
    "user_bg": "#00ffff",
    "user_text": "#000000",
    "assistant_bg": "#2a2a2a",
    "assistant_text": "#ffffff",
    "input_bg": "#1a1a1a"
}
```

**Usage:**

```python
get_chat_template(theme="dark")
```

#### Light Theme

```python
{
    "bg": "#ffffff",
    "bg_secondary": "#f5f5f5",
    "text": "#000000",
    "text_secondary": "#666666",
    "border": "#dddddd",
    "user_bg": "#007bff",
    "user_text": "#ffffff",
    "assistant_bg": "#f0f0f0",
    "assistant_text": "#000000",
    "input_bg": "#ffffff"
}
```

**Usage:**

```python
get_chat_template(theme="light")
```

### Custom Themes

To create a custom theme, modify the generated HTML:

```python
from rapidai.ui import get_chat_template

def get_custom_template():
    html = get_chat_template(theme="dark")

    # Replace colors
    html = html.replace("#00ffff", "#ff6b6b")  # Custom primary color
    html = html.replace("#0a0a0a", "#1a1a2e")  # Custom background

    return html

@app.route("/")
@page("/")
async def index():
    return get_custom_template()
```

## Frontend API

### JavaScript Interface

The chat template exposes these JavaScript functions:

#### addMessage

```javascript
function addMessage(role, content, timestamp = new Date())
```

Add a message to the chat interface.

**Parameters:**
- `role` (`string`) - Either "user" or "assistant"
- `content` (`string`) - Message content (supports markdown if enabled)
- `timestamp` (`Date`) - Message timestamp (optional)

**Example:**

```javascript
addMessage('user', 'Hello!');
addMessage('assistant', 'Hi there!');
```

#### sendMessage

```javascript
async function sendMessage()
```

Send the current input value to the backend.

**Behavior:**
1. Gets message from textarea
2. Adds user message to chat
3. Disables input and shows loading
4. POSTs to `/chat` endpoint
5. Adds assistant response
6. Re-enables input

**Endpoint requirements:**

```javascript
// POST /chat
{
  "message": "user message"
}

// Response
{
  "response": "assistant response"
}
```

#### renderMarkdown

```javascript
function renderMarkdown(text)
```

Render markdown text to HTML (if markdown enabled).

**Parameters:**
- `text` (`string`) - Markdown text

**Returns:** HTML string

**Uses:**
- `marked.js` library if `enable_markdown=True`
- Simple newline to `<br>` if `enable_markdown=False`

### DOM Elements

**IDs:**
- `#messages` - Messages container
- `#message-input` - Input textarea
- `#send-button` - Send button
- `#loading` - Loading indicator
- `#file-input` - File input (if enabled)

**Classes:**
- `.chat-container` - Main container
- `.chat-header` - Header section
- `.chat-messages` - Messages area
- `.chat-input` - Input area
- `.message` - Individual message
- `.message.user` - User message
- `.message.assistant` - Assistant message
- `.message-avatar` - Message avatar
- `.message-content` - Message content
- `.message-text` - Message text
- `.loading` - Loading indicator
- `.loading.active` - Active loading state

## Customization Examples

### Custom Colors

```python
from rapidai.ui import get_chat_template

def get_branded_chat():
    html = get_chat_template(theme="dark")

    # Replace brand colors
    replacements = {
        "#00ffff": "#ff6b6b",  # Primary color
        "#0a0a0a": "#1a1a2e",  # Background
        "#1a1a1a": "#16213e",  # Secondary background
    }

    for old, new in replacements.items():
        html = html.replace(old, new)

    return html
```

### Custom JavaScript

```python
from rapidai.ui import get_chat_template

def get_enhanced_chat():
    base = get_chat_template()

    # Add custom script
    custom_script = """
    <script>
        // Track analytics
        window.addEventListener('load', () => {
            console.log('Chat loaded');
        });

        // Custom send handler
        const originalSend = sendMessage;
        sendMessage = async function() {
            console.log('Sending message...');
            await originalSend();
            console.log('Message sent');
        };
    </script>
    """

    # Insert before </body>
    return base.replace("</body>", f"{custom_script}</body>")
```

### Custom Styles

```python
from rapidai.ui import get_chat_template

def get_styled_chat():
    base = get_chat_template()

    custom_css = """
    <style>
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .message-text {
            border-radius: 20px;
        }

        .message.user .message-text {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
    </style>
    """

    return base.replace("</head>", f"{custom_css}</head>")
```

### Add Features

```python
from rapidai.ui import get_chat_template

def get_chat_with_clear():
    base = get_chat_template()

    # Add clear button
    clear_button = """
    <button id="clear-button" style="margin-top: 10px; padding: 0.5rem 1rem; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer;">
        Clear Chat
    </button>
    """

    # Add clear script
    clear_script = """
    <script>
        document.getElementById('clear-button').addEventListener('click', () => {
            messagesContainer.innerHTML = '';
            addMessage('assistant', 'Hello! How can I help you today?');
        });
    </script>
    """

    html = base.replace("</div>\n        </div>\n\n        <div class=\"chat-input\">",
                       f"{clear_button}</div>\n        </div>\n\n        <div class=\"chat-input\">")

    return html.replace("</body>", f"{clear_script}</body>")
```

## Complete Integration Example

```python
from rapidai import App, LLM
from rapidai.memory import ConversationMemory
from rapidai.ui import page, ChatInterface, get_chat_template

app = App()
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()

# Configure interface
interface = ChatInterface(
    title="AI Assistant",
    theme="light",
    show_timestamps=True,
    enable_markdown=True,
    enable_file_upload=False,
    placeholder="Ask me anything...",
    max_height="700px",
    avatar_user="👤",
    avatar_assistant="🤖"
)

# Serve UI
@app.route("/")
@page("/")
async def index():
    return get_chat_template(config=interface)

# Chat endpoint
@app.route("/chat", methods=["POST"])
async def chat(message: str, user_id: str = "default"):
    # Add to memory
    memory.add_message(user_id, "user", message)

    # Get history
    history = memory.get_history(user_id, limit=10)

    # Generate response
    response = await llm.chat(history)

    # Add to memory
    memory.add_message(user_id, "assistant", response)

    return {"response": response}

# Clear endpoint
@app.route("/clear", methods=["POST"])
async def clear(user_id: str = "default"):
    memory.clear(user_id)
    return {"message": "Cleared"}

if __name__ == "__main__":
    app.run()
```

## See Also

- [UI Guide](../advanced/ui.md) - Complete UI usage guide
- [Testing](testing.md) - Test UI components
- [Deployment](../tutorial/deployment.md) - Deploy UI applications
