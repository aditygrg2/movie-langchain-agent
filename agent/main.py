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
from flask import Flask, jsonify, request
from langchain_community.utilities import SerpAPIWrapper
from langchain.prompts import PromptTemplate
from flask_socketio import SocketIO
from flask_cors import CORS

load_dotenv()
openai_api_key = os.environ['openai_api_key']
serpapi_api_key = os.environ['serpapi_api_key']
CLIENT_URL = "http://localhost:3000"

llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key, verbose=True, streaming=True)

search_params = {
    "engine": "google",
    "gl": "us",
    "hl": "en",
}

search = SerpAPIWrapper(params=search_params, serpapi_api_key=serpapi_api_key)

agent_API_chain = initialize_agent(
    api_tools, llm,
    agent='zero-shot-react-description',
    verbose=True, max_iterations=5, handle_parsing_errors=True)

def get_response_if_token_exceed(new_thought):
    vec = new_thought.get_vec()
    l = len(vec)
    for i in range(l-1, -1, -1):
        if(not str(vec[i].log).count("Action")):
            return str(vec[i].log)

text = """
You are a movie and actor information bot. Provide the final answer to the input query.

Do not repeat tools!

Begin!

Query: \n
"""

def runner(query):
    try:
        new_thought = ThoughtHandler()
        output = agent_API_chain.run(text + query, callbacks=[new_thought])

    except Exception as e:
        try:
            search_results = search.run(query)

            temp = f"""
            Answer the query from the context. If not found, revert not found!

            DO NOT EVER ANSWER ANYTHING UNRELATED TO MOVIES!

            %INSTRUCTIONS
            Do not include links, just the answer.

            %CONTEXT
            {search_results}

            %QUERY
            {query}
            """

            prompt = PromptTemplate(
                input_variables=["search_results", "query"],
                template=temp
            )

            llm_chain = LLMChain(
                llm=OpenAI(openai_api_key=openai_api_key), 
                prompt=prompt, 
            )

            output = llm_chain.invoke({"search_results": search_results, "query": query})['text'].strip()

        except Exception as new_exception:
            output = get_response_if_token_exceed(new_thought)

    if(len(output) == 0):
        return "Sorry, I couldn't find any relevant data for this query. Please try again!"

    return output

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(query):
    return runner(query)

@app.route('/', methods=["GET"])
def index():
    return jsonify({'message': 'Hello, to access movie bot go to {}!'.format(CLIENT_URL)})

@app.route('/get_response', methods=['POST'])
def greet():
    return runner(request.json.get('query'))

if __name__ == '__main__':
    socketio.run(app, debug=True)