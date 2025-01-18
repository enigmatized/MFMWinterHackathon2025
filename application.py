from flask import Flask, request, jsonify
import anthropic


app = Flask(__name__)

@app.route('/api/v1/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})


@app.route('/')
def index():
    return "Hello, World!"


def tryThisOut():

    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key="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",
    )
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Help me write about love"}
        ]
    )
    return message.content