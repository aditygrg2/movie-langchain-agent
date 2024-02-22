import os
import requests
import json
from ThoughtHandler import ThoughtHandler
from tools import api_tools
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain_openai import OpenAI
from flask_app import socketio
from flask_app import app
from flask import jsonify, request
from langchain_community.utilities import SerpAPIWrapper
from langchain.prompts import PromptTemplate
from flask_app import CLIENT_URL

from flask_cors import CORS

load_dotenv()
openai_api_key = os.environ['openai_api_key']
serpapi_api_key = os.environ['serpapi_api_key']


llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key,
                 verbose=True, streaming=True)

search_params = {
    "engine": "google",
    "gl": "us",
    "hl": "en",
}

search = SerpAPIWrapper(params=search_params, serpapi_api_key=serpapi_api_key)

agent_API_chain = initialize_agent(
    api_tools, llm,
    agent='zero-shot-react-description',
    verbose=True, max_iterations=6, handle_parsing_errors=True)


def get_response_if_token_exceed(new_thought):
    vec = new_thought.get_vec()
    l = len(vec)
    for i in range(l-1, -1, -1):
        if (not str(vec[i].log).count("Action")):
            return str(vec[i].log)


text = """
You are a bot powered by IMDb. Provide the final answer to the input query. 
Answer queries only related to "movies", "tvseries", "actors", "cinema".

%Instructions:
You only reply with texts, you do not know the images, cover arts, videos or trailer something not text.

Begin!

Query: \n
"""


def search_runner(query):
    search_results = search.run(query)

    temp = f"""
    Answer the query from the context.
    Answer queries only related to "movies", "tvseries", "actors", "cinema".
    
    %INSTRUCTIONS
    1. Do not include Links or IDs, find the information from IDs using "find" tool.
    2. You only reply with texts, you do not know the images, cover arts, videos or trailer something not text.
    3. Words starting with "tt" or "nn" are IDs, use them as an input to relevant tools for fetching more details.

    %CONTEXT
    {search_results}

    %QUERY
    {query}

    Answer:
    """

    prompt = PromptTemplate(
        input_variables=["search_results", "query"],
        template=temp
    )

    llm_chain = LLMChain(
        llm=OpenAI(openai_api_key=openai_api_key),
        prompt=prompt,
    )

    return llm_chain.invoke({"search_results": search_results, "query": query})[
        'text'].strip()

def runner(query, socketio):
    try:
        new_thought = ThoughtHandler(socketio)
        output = agent_API_chain.run(text + query, callbacks=[new_thought])

    except Exception as e:
        print(e)
        try:
            output = search_runner(query)

        except Exception as new_exception:
            print(new_exception)
            output = get_response_if_token_exceed(new_thought)

    if ((not output) or (len(output) == 0)):
        output = "Sorry, I couldn't find any relevant data for this query. Please try again!"

    if (output.startswith("Agent stopped")):
        output = search_runner(query)

    return output


isAgentWorking = False

@socketio.on('message')
def handle_message(query):
    global isAgentWorking
    print(query, isAgentWorking)
    if (not isAgentWorking):
        isAgentWorking = True
        output = runner(query, socketio)
        socketio.emit("final_answer", output)
        isAgentWorking = False
    else:
        socketio.emit("final_answer", "Agent is currently busy!")


@app.route('/', methods=["GET"])
def index():
    return jsonify({'message': 'Hello, to access movie bot go to {}!'.format(CLIENT_URL)})


@app.route('/get_response', methods=['POST'])
def greet():
    return runner(request.json.get('query'))


if __name__ == '__main__':
    socketio.run(app)
