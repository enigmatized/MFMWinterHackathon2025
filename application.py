from flask import Flask, request, jsonify
import anthropic
from openai import OpenAI
import FinTwitUsers


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
        user_prompt+= getTweets()
        print("Did I get tweets")
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
        model="gpt-4o-mini", #"gpt-4o", #"gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": "Does this work?"},
        ]
        )

        return completion.choices[0].message


def getTweets():
    newLsUsers = FinTwitUsers.create_fintwit_users_from_csv("tweets.csv" )
    sendToOpenAI = ""
    for x in newLsUsers:

        if len(x.retreivedTweets) > 0:
            tweets = ""
            for (id, tweet) in x.retreivedTweets.items():
                tweets += "id:" + id +  "tweet" + tweet
                
            sendToOpenAI += f"{x.name} has the following tweets: {tweets}\n"
    prompt = "Can you give me categorize the tweets from a given user, then give a general sentiment of these different tweets?" \
    + "Can you also group the tweets that are not finance related and give  a general sentiment to them ? " \
    + "Can you also give me seperate general sentitment for all the finacial related tweets from these users. " \
    +"I am looking to make financial day trades based on sentiment, specifically extreme sentiment as many times it is mean reverting." \
    +" Then can you give a general sentiment of each category with a summary of the category in either?" \
    +"Please do not include any warning about trading, day trading for any warning of any nature." 
    prompt = prompt + sendToOpenAI
    return prompt