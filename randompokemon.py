from random import randint
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.parse import urlencode

from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

ASK_APPLICATION_ID = None # TODO: replace with real application id

ENDPOINT = "https://randompokemongenerator.com/api"

app = Flask(__name__)
ask = Ask(app, "/")

REGIONS = ['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola']
POKEMON_TYPES = []

@ask.launch
def launch():
    launch_text = render_template('welcome')
    return question(launch_text)


@ask.intent("GetPokemon")
def oneshot_pokemon():
    """
    Returns 1 to 6 Pokemon based on default generator values
    """

    number_of_pokemon = randint(1,6)

    try:
        api_response = _send_api_request(num_pokemon=number_of_pokemon)
    except:
        return statement(render_template("genator_problem")).simple_card("Random Pokemon Generator", 
                                                                        render_template("genator_problem"))

    generated_pokemon = ", ".join(_format_pokemon_as_list(api_response))
    statement_text = render_template("oneshot_pokemon", pokemon=generated_pokemon)
    return statement(statement_text)


@ask.intent("GetSpecificPokemon",
            mapping={'number_of_pokemon': 'Count', 'pokemon_type': 'Type', 'region': 'Region'},
            convert={'count': int},
            default={'number_of_pokemon': 1, 'pokemon_type': 'any', 'region': 'national'})
def get_random_pokemon(number_of_pokemon, pokemon_type, region):
    """
    Uses user-provided slots to request random pokemon that meet constraints from slots
    """
    if not 1 <= number_of_pokemon <= 6:
        return question(render_template("number_of_pokemon_error").reprompt("generate_reprompt"))

    if region not in REGIONS:
        return question(render_template("region_error").reprompt("generate_reprompt"))

    if pokemon_type not in POKEMON_TYPES:
        return question(render_template("pokemon_type_error").reprompt("generate_reprompt"))

    try:
        api_response = _send_api_request(number_of_pokemon, pokemon_type, region)
    except:
        return statement(render_template("genator_problem")).simple_card("Random Pokemon Generator", 
                                                                        render_template("genator_problem"))
    pass

@ask.intent("ListOfRegions")
def get_list_of_regions():
    # make fluent by inserting "and" before last element
    REGIONS.insert(-1, "and")
    
    list_of_regions = ", ".join(REGIONS)
    return question(render_template("list_of_regions", regions=list_of_regions)) \
            .reprompt(render_template("generate_reprompt"))


def _send_api_request(num_pokemon, pokemon_type="any", region="national"):
    """
    Helper method to send the actual POST request to API
    """
    pokemon_criteria = {'number_of_pokemon': num_pokemon, 'type1': pokemon_type, 'region': region}

    data = urlencode(pokemon_criteria)
    response = urlopen(ENDPOINT + "/generate", data=data)

    if response.code != 200:
        raise Exception("Response returned an error")
    return response.read()


def _format_pokemon_as_list(response):
    list_of_pokemon = list()

    pokemon_response = json.loads(response)

    for pokemon in pokemon_response:
        list_of_pokemon.append(pokemon.get('name'))

    # make the list sound more fluent by inserting "and" before last element
    if len(list_of_pokemon) >= 2:
        list_of_pokemon.insert(-1, 'and')

    return list_of_pokemon


if __name__ == '__main__':

    app.run(debug=True)