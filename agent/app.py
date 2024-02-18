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

Instructions:
1. Check if the query is related to movies, tvseries, shows, stories, actors, or anything similar. Use "find" tool or "final-search" for it.
2. If yes, try to answer the query using tools OTHER THAN "final-search". If no, return that you cannot find it on IMDb database
3. If not found a satisfied solution, use "final-search"

Begin!

Query: \n
"""


def search_runner(query):
    search_results = search.run(query)

    temp = f"""
    Answer the query from the context.

    If the query is not relevant to movies, tvseries, actor or movie or tvseries stories, return that you do not know as you are a movie bot.

    %INSTRUCTIONS
    Do not include links or IDs, just the answer.

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

    output = llm_chain.invoke({"search_results": search_results, "query": query})[
        'text'].strip()


def runner(query, socketio):
    try:
        new_thought = ThoughtHandler(socketio)
        output = agent_API_chain.run(text + query, callbacks=[new_thought])

    except Exception as e:
        try:
            output = search_runner(query)

        except Exception as new_exception:
            output = get_response_if_token_exceed(new_thought)

    if ((not output) or (len(output) == 0)):
        return "Sorry, I couldn't find any relevant data for this query. Please try again!"

    if (output.startswith("Agent stopped")):
        return search_runner(query)

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
