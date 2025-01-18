from flask import Flask, request, jsonify
import anthropic
from openai import OpenAI


app = Flask(__name__)

@app.route('/api/v1/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})


@app.route('/',  methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the prompt from the form
        user_prompt = request.form.get('prompt', '')
        # client = anthropic.Anthropic(
        #      # defaults to os.environ.get("ANTHROPIC_API_KEY")
        #      api_key="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",
        #  )
        # response = client.messages.create(
        #     model="claude-3-5-sonnet-20241022",  # or whichever model you prefer
        #     max_tokens=1024,
        #     messages=[
        #         {"role": "user", "content": user_prompt}
        #     ]
        # )
        # client = OpenAI(
        #     api_key="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"
        #     )

        # completion = client.chat.completions.create(
        # model="gpt-4o", #"gpt-4o-mini",
        # store=True,
        # messages=[
        #     {"role": "user", "content": user_prompt},
        # ]
        # )
        res = some_function(user_prompt)
        # Return a very simple HTML page showing the result
        return f"""
        <h1>Here is your response:</h1>
        <pre>{res}</pre>
        <br>
        <a href="/">Go back</a>
        """
    
    # If method is GET, display the form
    return """
    <h1>Enter your prompt</h1>
    <form method="POST">
      <textarea name="prompt" rows="5" cols="60"></textarea><br><br>
      <input type="submit" value="Submit Prompt" />
    </form>
    """



@app.route('/api/v1/generate', methods=['POST'])
def generate_text():
    """
    Expects a JSON payload with a 'prompt' field.
    Example request body:
    {
      "prompt": "Help me write a story about friendship."
    }
    """
    data = request.get_json()
    user_prompt = data.get("prompt", "") if data else ""


    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key="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",
    )
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    return message.content




def some_function(user_prompt):
        client = OpenAI(
            api_key="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"
            )

        completion = client.chat.completions.create(
        model="gpt-4o", #"gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": user_prompt},
        ]
        )

        return completion.choices[0].message