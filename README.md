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
2. Once he finds the movie or actor or anything related, he fetches the ID and keeps it to query another API.

Let's try something else -

```{
    "query": "Who is Gwen Stacy in the movie The Amazing Spiderman 2?"
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
    "log": "The character Gwen Stacy in the movie \"The Amazing Spider-Man 2\" is played by Emma Stone. Emma Stone was born on November 6, 1988, in Scottsdale, Arizona, USA. She is known for her bright emerald green eyes, distinctive husky voice, and red hair. She is married to Dave McCary and has one child."
  },
  {
    "response": "Gwen Stacy in the movie \"The Amazing Spider-Man 2\" is played by Emma Stone. Emma Stone was born on November 6, 1988, in Scottsdale, Arizona, USA. She is known for her bright emerald green eyes, distinctive husky voice, and red hair. She is married to Dave McCary and has one child."
  }
```

The agent follows a beautiful trajectory to fetch the results.
1. It understands the query and searches the IMDb for similar movies
2. He beautifully makes a distinction between the movie and the character
3. Uses the details of the movie to find the details about the actor
4. Return the response from finding details.

What if IMDb does not have particular data?

```{
    "query": "PLease list me all abuse words used in Animal movie, list them word by word"
  },
  {
    "tool": "find",
    "tool_input": "Animal",
    "log": "We need to find the ID of the movie \"Animal\" first to get the information about the abuse words used in the movie.\\nAction: find\\nAction Input: Animal"
  },
  {
    "tool": "get-details-title",
    "tool_input": "tt13751694",
    "log": "We have found the ID for the movie \"Animal\". Now we can get the details of the movie to find the abuse words used.\\nAction: get-details-title\\nAction Input: tt13751694"
  },
  {
    "tool": "_Exception",
    "tool_input": "Invalid or incomplete response",
    "log": "Parsing LLM output produced both a final answer and a parse-able action:: We have the details of the movie \"Animal\", but we need to find the specific information about the abuse words used in the movie.\\nAction: final-search\\nAction Input: List of abuse words used in the movie \"Animal\"\\nFinal Answer: The list of abuse words used in the movie \"Animal\" is not available on IMDb database."
  },
  {
    "tool": "_Exception",
    "tool_input": "Invalid or incomplete response",
    "log": "Parsing LLM output produced both a final answer and a parse-able action:: We were unable to find the list of abuse words used in the movie \"Animal\" on IMDb. Let\\"
  },
  {
    "response": "The list of abuse words used in the movie \"Animal\" is not available on IMDb."
  }
```

It fallbacks nicely.

**Note:** Due to the free OpenAI API, the tokens are limited to first 1800 defined in `app.py` file. So some results might have little mismatched information. But amazingly it still give nice results.

The prompts and the code for this are discussed in the file `agent/app.py`

All these tools are defined in the file `agent/tools.py`

### Technologies Used
1. Backend:
- Flask: A micro web framework for Python. Defined in `agent/flask_app.py`
- Sockets: For communication between client and server.
- Gunicorn: A WSGI HTTP server for running Python web applications. Configurations defined in `gunicorn_config.py`
2. Frontend:
- React
3. LLM:
- OpenAI
4. API
- RapidApi- IMDB

## How to use - 

### Backend:

Install all the dependencies using `pip install -r requirements.txt`  

Add the following code with the API keys to the .env file and add it to the agent folder.  

```
openai_api_key=
serpapi_api_key=
X-RapidAPI-Key=
```

Run `gunicorn --config gunicorn_config.py app:app` to start the backend on port 5000.  

### Frontend:

- Run `npm install` to install the libraries used in the project.
- Run `npm run start` to start the frontend on port 3000.

## More prompts -

```{
    "query": "Please list at least 4 lines about the movie Homelander?"
  },
  {
    "tool": "find",
    "tool_input": "Homelander",
    "log": "We need to find the IMDb ID for the movie \"Homelander\" first.\\nAction: find\\nAction Input: Homelander"
  },
  {
    "tool": "final-search",
    "tool_input": "Please list at least 4 lines about the movie Homelander",
    "log": "The movie \"Homelander\" does not have a specific IMDb ID. We will need to use the \"final-search\" tool to find more information about it.\\n\\nAction: final-search\\nAction Input: Please list at least 4 lines about the movie Homelander"
  },
  {
    "response": "Here are some details about the movie \"Homelander\":\n- Homelander thinks of himself and every other superhero as a different species. He doesn't believe that ordinary people are worthy.\n- Homelander has some memorable quotes, such as \"I'm stronger, I'm smarter, I'm better! I AM BETTER!\" and \"No God. The only man in the sky is me.\"\n- Homelander is a complex character with several quotes that sum up his personality.\n- Homelander, with the face of a movie star and the powers of a god, is considered the greatest superhero alive."
  },
  {
    "query": "List me the names of all the superheroes in the series 'The Boys'"
  },
  {
    "tool": "find",
    "tool_input": "The Boys",
    "log": "I should use the \"find\" tool to get the ID of the series \\"
  },
  {
    "tool": "get-top-cast",
    "tool_input": "tt1190634",
    "log": "I should now use the \"get-top-cast\" tool to determine the top cast of the series \\"
  },
  {
    "tool": "get-bio",
    "tool_input": "nm0881631",
    "log": "I should now use the \"get-bio\" tool to get more information about the actors in the series \\"
  },
  {
    "tool": "get-bio",
    "tool_input": "nm4425051",
    "log": "I should now use the \"get-bio\" tool to get more information about the other actors in the series \\"
  },
  {
    "tool": "get-bio",
    "tool_input": "nm1102278",
    "log": "I should now use the \"get-bio\" tool to get more information about the other actors in the series \\"
  },
  {
    "response": "The superheroes in the series 'The Boys' are Billy Butcher, Hughie Campbell, and Homelander."
  }
```

Uses almost perfect routes! The responses from the API are not visible here, but they will be visible when you run the code locally.

```{
    "query": "Spiderman Across the Spiderverse have how many spidermans?"
  },
  {
    "tool": "find",
    "tool_input": "Spiderman Across the Spiderverse",
    "log": "We need to find the ID of the movie \"Spiderman Across the Spiderverse\" first to gather more information about it.\\nAction: find\\nAction Input: Spiderman Across the Spiderverse"
  },
  {
    "tool": "get-details-title",
    "tool_input": "tt29003913",
    "log": "We have found the ID for the movie \"Spiderman Across the Spiderverse.\" Now, let\\"
  },
  {
    "tool": "final-search",
    "tool_input": "How many Spidermans are in the movie \"Spiderman Across the Spiderverse\"?",
    "log": "The movie \"Spiderman Across the Spiderverse\" has a running time of 12 minutes. It seems to be a podcast episode rather than a movie. Let\\"
  },
  {
    "response": "The movie \"Spiderman Across the Spiderverse\" includes 280 variations of Spider-Man, with 95 of them being unique and named characters."
  }
```

Fetches wrong results, but then try to improve.

Do your hands dirty too. Try it here: https://movie-langchain-agent.vercel.app/


