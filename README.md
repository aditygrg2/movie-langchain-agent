# Cinematica Movie Answer Bot for calling IMDb APIs by using Langchain ReAct agent

Cinematica is made using Langchain 'ReAct' agent for function calling different API's for receiving the data from IMDb.

Link to the deployed version: https://movie-langchain-agent.vercel.app

<img width="1535" alt="diagram" src="https://github.com/aditygrg2/movie-langchain-agent/assets/98523623/377cb1cf-9447-4b79-925f-255355bf6084">

Source of Image: https://react-lm.github.io   
Source of API: https://rapidapi.com/apidojo/api/imdb8

## How it works?

<img width="1371" alt="hotpotqa" src="https://github.com/aditygrg2/movie-langchain-agent/assets/98523623/125f402c-9dcd-4008-9592-01d49a909dfe">

*A sample query of ReAct Agent*

The main core idea of the ReAct agent is to take action on any reasoning that was provided earlier as visible in the query above.

<img width="1062" alt="Screenshot 2024-02-20 at 15 24 17" src="https://github.com/aditygrg2/movie-langchain-agent/assets/98523623/d47c8498-24a3-4d0d-839c-74b2f74e3acb">

*Sample Query in the Cinematica Agent*

1. The agent first thinks what it needs to do, and tries to search IMDb if the relevant query is present.
2. Once he founds the movie or actor or anything related, he fetches the ID and keeps it to query another APIs.

Let's ask a little hard question -

```{
    "query": "Who is gwen stacy in the movie the amazing spiderman 2?"
  },
  {
    "tool": "find",
    "tool_input": "Gwen Stacy The Amazing Spider-Man 2",
    "log": "We need to find information about the character Gwen Stacy in the movie \"The Amazing Spider-Man 2\".\\nAction: find\\nAction Input: Gwen Stacy The Amazing Spider-Man 2"
  },
  {
    "tool": "get-bio",
    "tool_input": "nm1297015",
    "log": "We have found the movie \"The Amazing Spider-Man 2\" and the character Gwen Stacy is played by Emma Stone.\\nAction: get-bio\\nAction Input: nm1297015"
  },
  {
    "tool": "_Exception",
    "log": "The character Gwen Stacy in the movie \"The Amazing Spider-Man 2\" is played by Emma Stone. Emma Stone was born on November 6, 1988 in Scottsdale, Arizona, USA. She is known for her bright emerald green eyes, distinctive husky voice, and red hair. She is married to Dave McCary and has one child."
  },
  {
    "response": "Gwen Stacy in the movie \"The Amazing Spider-Man 2\" is played by Emma Stone. Emma Stone was born on November 6, 1988 in Scottsdale, Arizona, USA. She is known for her bright emerald green eyes, distinctive husky voice, and red hair. She is married to Dave McCary and has one child."
  }
```

The agent follows a beautiful trajectory to fetch the results.
1. It understands the query and searches the IMDb for similar movies
2. He beautifully makes a distinction between the movie and the character
3. Uses the details of the movie to find the details about the actor
4. Return the response from finding details.

All these tools are defined in the file `agent/tools.py`

### Technologies Used
1. Backend:
- Flask: A micro web framework for Python.
- Sockets: For communication between client and server.
- Gunicorn: A WSGI HTTP server for running Python web applications.
2. Frontend:
- React
3. LLM:
- OpenAI

## How to use - 

#### Backend:

Add the following code with the API keys to the .env file and add it to the agent foler.
`
openai_api_key=
serpapi_api_key=
X-RapidAPI-Key=
`

Run `gunicorn --config gunicorn_config.py app:app` to start the backend on port 5000.

#### Frontend:

In the project directory, you can run:

### `npm install`

For installing all the directories

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.
