"""Basic prompt management example."""

from rapidai import App, LLM
from rapidai.prompts import PromptManager

app = App(title="Prompt Basic Example")
llm = LLM("claude-3-haiku-20240307")

# Initialize prompt manager
# Prompts will be loaded from ./prompts/ directory
prompt_manager = PromptManager(prompt_dir="prompts", auto_reload=True)

# Register prompts programmatically
prompt_manager.register(
    "greeting",
    "Hello {{ name }}! Welcome to {{ app_name }}. How can I help you today?",
)

prompt_manager.register(
    "summarize",
    """Please summarize the following text in {{ max_words }} words or less:

{{ text }}

Summary:""",
)


@app.route("/greet", methods=["POST"])
async def greet(name: str):
    """Greet a user using a prompt template.

    Example:
        curl -X POST http://localhost:8004/greet \\
            -H "Content-Type: application/json" \\
            -d '{"name": "Alice"}'
    """
    # Render the prompt
    prompt_text = prompt_manager.render("greeting", name=name, app_name="RapidAI")

    # Use with LLM
    response = await llm.complete(prompt_text)

    return {"greeting": response, "prompt_used": "greeting"}


@app.route("/summarize", methods=["POST"])
async def summarize(text: str, max_words: int = 50):
    """Summarize text using a prompt template.

    Example:
        curl -X POST http://localhost:8004/summarize \\
            -H "Content-Type: application/json" \\
            -d '{"text": "Long text here...", "max_words": 30}'
    """
    # Render the prompt
    prompt_text = prompt_manager.render("summarize", text=text, max_words=max_words)

    # Use with LLM
    response = await llm.complete(prompt_text)

    return {"summary": response, "prompt_used": "summarize"}


@app.route("/list-prompts", methods=["GET"])
async def list_prompts():
    """List all available prompts.

    Example:
        curl http://localhost:8004/list-prompts
    """
    prompts = prompt_manager.list_prompts()
    return {"prompts": prompts, "count": len(prompts)}


@app.route("/health", methods=["GET"])
async def health():
    """Health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Starting Prompt Basic Example...")
    print("Greet: POST /greet")
    print("Summarize: POST /summarize")
    print("List prompts: GET /list-prompts")
    print("")
    print("Create prompts in ./prompts/ directory for auto-loading!")
    app.run(port=8004)
