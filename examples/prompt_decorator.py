"""Prompt management with @prompt decorator example."""

from rapidai import App, LLM
from rapidai.prompts import prompt, PromptManager

app = App(title="Prompt Decorator Example")
llm = LLM("claude-3-haiku-20240307")

# Initialize prompt manager with hot reloading
prompt_manager = PromptManager(prompt_dir="prompts", auto_reload=True)


@app.route("/greet", methods=["POST"])
@prompt(template="Hello {{ name }}! How can I assist you today?", manager=prompt_manager)
async def greet(name: str, prompt_template: str, prompt):
    """Greet using inline template (prompt_template automatically injected).

    Example:
        curl -X POST http://localhost:8005/greet \\
            -H "Content-Type: application/json" \\
            -d '{"name": "Bob"}'
    """
    # Render with variables
    filled_prompt = prompt.render(name=name)

    response = await llm.complete(filled_prompt)

    return {"response": response, "variables_used": prompt.variables}


@app.route("/analyze", methods=["POST"])
@prompt(
    template="""Analyze the following text and provide:
1. Sentiment (positive/negative/neutral)
2. Key topics (3-5 topics)
3. Summary (2-3 sentences)

Text: {{ text }}

Analysis:""",
    manager=prompt_manager,
)
async def analyze(text: str, prompt_template: str, prompt):
    """Analyze text using inline template.

    Example:
        curl -X POST http://localhost:8005/analyze \\
            -H "Content-Type: application/json" \\
            -d '{"text": "I love using RapidAI! It makes building AI apps so easy."}'
    """
    filled_prompt = prompt.render(text=text)
    response = await llm.complete(filled_prompt)

    return {"analysis": response}


@app.route("/custom", methods=["POST"])
async def custom_prompt(system_msg: str, user_msg: str):
    """Use custom prompt on the fly.

    Example:
        curl -X POST http://localhost:8005/custom \\
            -H "Content-Type: application/json" \\
            -d '{
                "system_msg": "You are a helpful assistant",
                "user_msg": "What is AI?"
            }'
    """
    # Register a temporary prompt
    prompt_manager.register(
        "temp_custom",
        "System: {{ system }}\n\nUser: {{ user }}\n\nAssistant:",
    )

    prompt_text = prompt_manager.render("temp_custom", system=system_msg, user=user_msg)

    response = await llm.complete(prompt_text)

    return {"response": response}


@app.route("/health", methods=["GET"])
async def health():
    """Health check."""
    return {"status": "healthy", "prompts_loaded": len(prompt_manager.list_prompts())}


if __name__ == "__main__":
    print("Starting Prompt Decorator Example...")
    print("Greet: POST /greet")
    print("Analyze: POST /analyze")
    print("Custom: POST /custom")
    print("")
    print("Features:")
    print("- Inline template definitions")
    print("- Automatic variable injection")
    print("- Hot reloading (auto_reload=True)")
    app.run(port=8005)
