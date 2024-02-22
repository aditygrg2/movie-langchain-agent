import re
import os
import requests
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from flask_app import socketio

load_dotenv()
openai_api_key = os.environ['openai_api_key']
serpapi_api_key = os.environ['serpapi_api_key']
X_RapidAPIKey = os.environ['X-RapidAPI-Key']

llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key,
                 verbose=True, streaming=True)

search_params = {
    "engine": "google",
    "gl": "us",
    "hl": "en",
}

search = SerpAPIWrapper(params=search_params, serpapi_api_key=serpapi_api_key)


def get_summary(tokens):
    template = """
    Please list all the information present in the JSON in a proper readable format. 
    {json}

    Delete the non-relevant data

    Data:"""

    prompt = PromptTemplate(
        input_variables=["json"],
        template=template
    )

    chain = LLMChain(llm=llm, verbose=True, prompt=prompt)

    output = chain.invoke({"json": tokens})

    return output['text']


def extract_tt_id(string):
    pattern = r'(tt|nm)\d+'
    match = re.search(pattern, string)
    if match:
        return match.group(0)
    else:
        return None


headers = {
    "X-RapidAPI-Key": X_RapidAPIKey,
    "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
}

url = "https://imdb8.p.rapidapi.com"


def req_hook(endpoint, params):
    res = requests.get("{}/{}".format(url, endpoint),
                       headers=headers, params=params)

    if (not res):
        return "Not Found"

    return str(res.json())[0:1800]


def t_const_hook(endpoint, id):
    id = extract_tt_id(id)

    if (id.startswith("nm")):
        return "This is not a correct movie or TV Series title ID. Please find a movie or TV Series title ID."

    return req_hook(endpoint, params={
        "tconst": id
    })


def n_const_hook(endpoint, id):
    id = extract_tt_id(id)

    if (id.startswith("tt")):
        return "This is not a correct actor title ID. Please find a actor title ID."

    return req_hook(endpoint, params={
        "nconst": id
    })


def simple_hook(endpoint):
    return req_hook(endpoint, params={})


def get_initial_info(title):
    res = requests.get("{}/{}".format(url, 'title/find'), headers=headers, params={
        "q": title
    })

    try:
        id = res.json()['results'][0]['id'].split('/')[2]
    except:
        return None

    try:
        titleType = res.json()["results"][0]['titleType']
    except:
        titleType = "actor"

    try:
        image = res.json()["results"][0]['image']['url']
        if (len(image) > 0):
            socketio.emit("image_query", image)
    except:
        titleType = ""

    data = str(res.json())[0:1800]

    return (id, titleType, data)


def dob_actors(date):
    res = requests.get("{}/{}".format(url, 'actors/list-born-today'), headers=headers, params={
        "month": date.split(',')[0].strip(),
        "day": date.split(',')[1].strip()
    })

    if (len(str(res.json())) > 0):
        return "Not Found"

    return str(res.json())[0:1800]


def ids_hook(endpoint, id):
    return req_hook(endpoint, params={
        "ids": extract_tt_id(id)
    })


api_tools = [
    Tool(
        name='find',
        func=lambda string: get_initial_info(string),
        description="""
        Always use this first to get the id of the title.
        For any name of movie, album, song, actor_name, this will get a IMDb route and some data. 

        Input: Name of movie, album, song, actor_name or any other relevant title.
        Ouput: ID and some data of the input.
        """
    ),
    Tool(
        name="get-details-title",
        func=lambda id: t_const_hook("title/get-details", id),
        description="""
        Accepted titleType: movie or tvseries
        
        This can be used to give runningTimeInMinutes, numberOfEpisodes, seriesEndYear, seriesStartYear info about the movie or tvseries titles.

        Input: Single ID of the movie or tvseries titles For e.g, "tt32453"
        Output: JSON containing information of the movie or tvseries titles
        """
    ),
    Tool(
        name="get-top-cast",
        func=lambda id: t_const_hook("title/get-top-cast", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to determing top cast info of an movie or tvseries title.

        Input: Single ID of the movie or tvseries titles For e.g, "tt32453"
        Output: A route containing IDs of all the casts worked in that title
        """
    ),
    Tool(
        name="get-bio",
        func=lambda id: n_const_hook("actors/get-bio", id),
        description="""
        Accepted titleType: actor

        This can be used to determine birthdate, birthplace, gender, height, nicknames, spouses, trademarks, minibios for actors.

        Input: Single ID of the actor titles For e.g, "nm32453"
        Output: JSON containing details of actor or actress. Use it to fetch names, birthdate and any other relevant 
        """
    ),
    Tool(
        name="list-born-today",
        func=lambda date: dob_actors(date),
        description="""
        This can be used to determing actors with a particular birthday date.

        Input: Month and Day in integer format.
        Output: JSON containing IDs of actors with particular month and day. 
        """
    ),
    Tool(
        name="list-most-popular-celebs",
        func=lambda _: simple_hook("actors/list-most-popular-celebs"),
        description="""
        This can be used to determing most popular celebs/actors. 
        Use this only specifically needed.

        Input: ""
        Output: JSON containing IDs of most popular celebs. Search these IDs with "find" for more details.
        """
    ),
    Tool(
        name="list-most-popular-movies",
        func=lambda _: simple_hook("title/get-most-popular-movies"),
        description="""
        This can be used to determing most popular movies. 
        Use this only specifically needed.

        Input: ""
        Output: JSON containing IDs of most popular movies titles. Search these IDs with "find" for more details.
        """
    ),
    Tool(
        name="list-most-popular-tvshows",
        func=lambda _: simple_hook("title/get-most-popular-tv-shows"),
        description="""        
        This can be used to determing most popular tv shows. Use this only specifically needed.

        Input: ""
        Output: JSON containing IDs of most popular tvseries titles. Search these IDs with "find" for more details.
        """
    ),
    Tool(
        name="get-awards-summary",
        func=lambda id: n_const_hook("actors/get-awards-summary", id),
        description="""
        Accepted titleType: actor

        This can be used to determing the awards of the actor title.

        Input: Single ID of the actor titles. For e.g, "nm32453"
        Output: JSON containing awards summary of the actor titles.
        """
    ),
    Tool(
        name="get-known-for",
        func=lambda id: n_const_hook("actors/get-known-for", id),
        description="""
        Accepted titleType: actor

        Use this only specifically needed.
        This can be used to find interesting details of actor or actress and their personality and why this actor is popular
        
        Input: Single ID of the actor title. For e.g, "nm32453"
        Output: JSON containing the details about why this actor title is well known
        """
    ),
    Tool(
        name="get-interesting-jobs",
        func=lambda id: n_const_hook("actors/get-interesting-jobs", id),
        description="""
        Accepted titleType: actor

        Use this only specifically needed.
        This can be used to find details about interesting jobs of actor or actress
        
        Input: Single ID of the actor title. For e.g, "nm32453"
        Output: JSON containing the details about interesting jobs of actor or actress title. This might also return no data found.
        """
    ),
    Tool(
        name="get-crazycredits",
        func=lambda id: t_const_hook("title/get-crazycredits", id),
        description="""
        Accepted titleType: movie or tvseries

        Use this only specifically needed.
        This can be used to generate crazycredits, spoilers and funny things of movie or tvseries
        
        Input: Single ID of the movie or tvseries. For e.g, "tt32453"
        Output: JSON containing the details about crazycredits in specific title.
        """
    ),
    Tool(
        name="get-quotes",
        func=lambda id: t_const_hook("title/get-quotes", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to generate quotes of movie or tvseries
        
        Input: Single ID of the movie or tvseries. For e.g, "tt32453"
        Output: JSON containing the quotes of a title. Only limit the quotes upto 5, do not go beyond that.
        """
    ),
    Tool(
        name="get-meta-data",
        func=lambda id: ids_hook("title/get-meta-data", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to generate ways to watch and genres of the title
                
        Input: Single ID of the movie or tvseries title For e.g, "tt32453"
        Output: JSON containing the title, ratings, metacritic, popularity, ways to watch, and genres of any movie or tvseries title.
        """
    ),
    Tool(
        name="get-more-like-this",
        func=lambda id: t_const_hook("title/get-more-like-this", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to generate similar movie or tvseries similar to the input movie
        
        Input: Single ID of the movie or tvseries title For e.g, "tt32453"
        Output: JSON containing the routes for other similar movie or tvseries title. This can be used to recommend different movie or tvseries title similar to the input movie.
        """
    ),
    Tool(
        name="get-reviews",
        func=lambda id: t_const_hook("title/get-reviews", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to determine imdb ratings, meta critics, critic reviews, featured user reviews, certificates related to the movie or tvseries title.
        The popularity and movie quality can be inferred here
        
        Input: Single ID of the movie or tvseries title For e.g, "tt32453"
        Output: JSON containing the reviews for this movie or tvseries title. 
        """
    ),
    Tool(
        name="get-seasons",
        func=lambda id: t_const_hook("title/get-seasons", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to determine the season and epidode related to the movie or tvseries title
        
        Input: Single ID of the movie or tvseries title. For e.g, "tt32453"
        Output: JSON containing the seasons and episodes information of the movie or tvseries title.
        """
    ),
    Tool(
        name="get-awards-summary",
        func=lambda id: t_const_hook("title/get-awards-summary", id),
        description="""
        Accepted titleType: movie or tvseries

        This can be used to determine the awards summary, akas, of a movie or tvseries title
        
        Input: Single ID of the movie or tvseries title For e.g, "tt32453"
        Output: JSON containing the awards related to the movie or tvseries title
        """
    ),
    Tool(
        name="get-coming-soon-movies",
        func=lambda _: simple_hook("title/get-coming-soon-movies"),
        description="""
        This can be used to determine the coming soon TV movies.
        
        Input: ""
        Output: JSON containing the IDs of the coming soon movie or tvseries title with their release date.
        """
    ),
    Tool(
        name="get-coming-soon-tv-shows",
        func=lambda _: simple_hook("title/get-coming-soon-tv-shows"),
        description="""
        This can be used to determine the coming soon TV shows.

        Input: ""
        Output: JSON containing the IDs of the coming soon TV Shows with their release date.
        """
    ),
    Tool(
        name="get-parental-guide",
        func=lambda id: t_const_hook("title/get-parental-guide", id),
        description="""
        Accepted titleType: movie or tvseries
        This can be used to determine the nudity, violence, abuse, sex, and other similar details of the movie or tvseries title.
        This can be used to check if a series is good to watch.

        Input: Single ID of the movie or tvseries title For e.g, "tt32453"
        Output: JSON containing the parental guide related to the movie or tvseries title.
        """
    ),
    Tool(
        name="get-overview-details",
        func=lambda id: t_const_hook("title/get-overview-details", id),
        description="""
        Accepted titleType: movie or tvseries
        This can be used to give certificates, ratings, genres, plot outline and plot summary of the movie or tvseries title.

        Input: Single ID of the Title For e.g, "tt32453"
        Output: JSON containing the overview information of the movie or tvseries title. It can give the basic information about the movie or tvseries title.
        """
    ),
    Tool(
        name="get-plots",
        func=lambda id: t_const_hook("title/get-plots", id),
        description="""
        Accepted titleType: movie or tvseries
        This can be used to:
        - give the storylines and the main movie plot of the movie or tvseries title.
        - explain the movie

        Input: Single ID of the Title For e.g, "tt32453"
        Output: JSON containing the plots information of the movie or tvseries title
        """
    ),
    Tool(
        name="final-search",
        func=search.run,
        description=""" 
        Look for answer here, only if not found using any other tool. 
        
        ``
        Only movie, tvseries, actor related inputs are allowed.
        ``


        INSTRUCTIONS
        Input: Question of the user
        Output: Answer
        """,
    )
]
