from random import randint
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.parse import urlencode

from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

ASK_APPLICATION_ID = None # TODO: replace with real application id

ENDPOINT = "https://randompokemongenerator.com/api"

app = Flask(__name__)
ask = Ask(app, "/")

request_mappings = {
    'num_pokemon': 'Count',
    'region': 'Region',
    'type': 'Type'
}

@ask.launch
def launch():
    launch_text = render_template('welcome')
    return question(launch_text)


@ask.intent("GetPokemon")
def oneshot_pokemon():
    """
    Returns one or more Pokemon based on default generator values
    """
    pokemon_data = _send_api_request(num_pokemon=randint(1,6))
    generated_pokemon = ", ".join(pokemon_data)
    statement_text = render_template("oneshot_pokemon", pokemon=pokemon_data)
    return statement(statement_text)


@ask.intent("GetSpecificPokemon")
def get_random_pokemon():
    """
    Uses user-provided slots to request random pokemon that meet constraints from slots
    """
    pass

def _send_api_request(num_pokemon, pokemon_type="any", region="national"):
    """
    Helper method to send the actual POST request to API
    """
    pokemon_criteria = {'number_of_pokemon': num_pokemon, 'type1': pokemon_type, 'region': region}

    data = urlencode(pokemon_criteria)
    response = urlopen(ENDPOINT + "/generate", data=data).read()

    if len(response) == 0 or response.code !== 200:
        statement_text = render_template('generator_problem')
        return statement(statement_text).simple_card("Pokemon Generator", statement_text)

    # put json values into list
    generated_pokemon = _format_generator_response(json.loads(response))

    return generated_pokemon

def _format_generator_response(response):
    list_of_pokemon = list()

    for pokemon_json in response:
        list_of_pokemon.append(pokemon_json.get('name'))

    return list_of_pokemon

