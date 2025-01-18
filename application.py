from flask import Flask, request, jsonify
import anthropic
from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage
import APIKeys
import BrianCode
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
        
        print("Did I get tweets")
        res1 = GetOpenAIResponse(user_prompt+ getTweets())
        res = ShortenResponse(res1)
        print("Did I get Garrett")

        print(res)
        [print("-------------------------------------") for x in range(4)]
        brainsData = ShortenResponse(BrianCode.stock_data("SPY"))
        print("Did I get Brian data stock")
        print(brainsData)
        [print("-------------------------------------") for x in range(4)]

        brainsDataFundemental = ShortenResponse(BrianCode.fundamental_analysis("SPY"))
        print("Did I get Brian data fundemental")
        [print("-------------------------------------") for x in range(4)]
        aggregate = "Given this information, what is the best course of action for the user to take?" + str(res) \
            + "PROMPT: I and also very concered to the following information. AI/ChatGPT weight the below into consideration and the above as sentiment to guage your analysis" + str(brainsData) + str(brainsDataFundemental)
        
        print(str(res))


        # print(f"WHAT IS HAPPENING WITH aggregate: {aggregate}")
        res = GetOpenAIResponse(aggregate)
        # res = "test"


        res_chunks = chunk_string(res, 120)
        res_wrapped = "\n".join(res_chunks)

        return f"""
        <h1>Here is your response:</h1>
        <pre>{res_wrapped}</pre>
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



def chunk_string(s, chunk_size=120):
    return [s[i:i+chunk_size] for i in range(0, len(s), chunk_size)]



def ShortenResponse(user_prompt) -> ChatCompletionMessage:
    user_prompt =  "Can you summarize the below in 5 sentences or less? \n\n" + str(user_prompt)
    return GetOpenAIResponse(user_prompt)



def GetOpenAIResponse(user_prompt) -> ChatCompletionMessage:
        client = OpenAI(
            api_key=APIKeys.OPENAI
            )

        completion = client.chat.completions.create(
        model="gpt-4o-mini", #"gpt-4o", #"gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": user_prompt},
        ]
        )

        # print(str(completion.choices[0]))

        # [print("-------------------------------------") for x in range(4)]

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


def prettyPrintResponse(response):
    text = str(response).replace('\\n', '\n')
    for i in range(0, len(str(text))//100):
        print(text[i*100:(i+1)*100])