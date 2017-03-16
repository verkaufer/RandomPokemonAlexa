import os
from random import randint

from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.parse import urlencode

from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement


ENDPOINT = "https://randompokemongenerator.com/api"

app = Flask(__name__)
app.config['ASK_APPLICATION_ID'] = os.environ.get('ask_application_id')
ask = Ask(app, "/")


@ask.launch
def launch():
    return question(render_template('welcome'))


@ask.intent("GetPokemon")
def generate_without_options():
    """
    Returns 1 to 6 Pokemon based on default generator values
    """
    # Generator chooses how many Pokemon to generate
    number_of_pokemon = randint(1,6)

    try:
        api_response = _send_api_request(num_pokemon=number_of_pokemon)
    except:
        return statement(render_template("genator_problem")) \
                .simple_card("Random Pokemon Generator", render_template("genator_problem"))

    generated_pokemon = _format_pokemon_as_list(api_response)

    generated_pokemon_response = render_template("oneshot_pokemon", pokemon=generated_pokemon)
    return statement(generated_pokemon_response)


@ask.intent("GetSpecificPokemon",
            mapping={'number_of_pokemon': 'Count', 'pokemon_type': 'Type', 'region': 'Region'},
            convert={'number_of_pokemon': int},
            default={'number_of_pokemon': 1, 'pokemon_type': 'any', 'region': 'national'})
def get_random_pokemon(number_of_pokemon, pokemon_type, region):
    """
    Uses user-provided slots to request random pokemon that meet constraints from slots
    """
    if not 1 <= number_of_pokemon <= 6:
        return question(render_template("number_of_pokemon_error")) \
                .reprompt(render_template("generate_reprompt"))        

    try:
        api_response = _send_api_request(number_of_pokemon, pokemon_type, region)

    except InvalidPokemonType:
        return question(render_template("pokemon_type_error")) \
                .reprompt(render_template("generate_reprompt"))

    except InvalidPokemonRegion:
        return question(render_template("region_error")) \
                .reprompt(render_template("generate_reprompt"))

    except:
        return statement(render_template("genator_problem")) \
                .simple_card("Random Pokemon Generator", render_template("genator_problem"))
    
    # Format results so they are correctly read by Alexa
    generated_pokemon = _format_pokemon_as_list(api_response)

    # Render our response from template
    generated_pokemon_results = render_template("custom_generated_pokemon", 
                                                 num_pokemon=number_of_pokemon,
                                                 pokemon_type=pokemon_type if pokemon_type != "any" else "",
                                                 region=region,
                                                 pokemon=generated_pokemon)
    return statement(generated_pokemon_results)


@ask.intent("ListOfRegions")
def get_list_of_regions():
    # make fluent by inserting "and" before last element
    list_of_regions = ['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola']
    list_of_regions.insert(-1, "and")
    
    return question(render_template("list_of_regions", regions=list_of_regions)) \
            .reprompt(render_template("generate_reprompt"))


# ======================
# Basic intent handling for Help, End, Cancel, and Stop
# ======================
@ask.intent('AMAZON.HelpIntent')
def helpme():
    return question(render_template('help_main'))\
            .reprompt(render_template('generate_reprompt'))

@ask.session_ended
def session_ended():
    return "", 200


@ask.intent('AMAZON.StopIntent')
def stop_action():
    return statement(render_template('end_generator_session'))


@ask.intent('AMAZON.CancelIntent')
def cancel_request():
    return statement(render_template('end_generator_session'))


# ======================
# Helper methods
# ======================
def _send_api_request(num_pokemon, pokemon_type="any", region="national"):
    """
    Helper method to send the actual POST request to API
    """
    pokemon_criteria = {'number_of_pokemon': num_pokemon, 'type1': pokemon_type, 'region': region}

    data = urlencode(pokemon_criteria)
    response = urlopen(ENDPOINT + "/generate", data=data)

    if response.code != 200:
        errors = response.json()
        if errors.get('type1') or errors.get('type2'):
            raise InvalidPokemonType
        else:
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


# ======================
# Exceptions
# ======================
class InvalidPokemonType(Exception):
    """Raise if Pokemon Type given is not one of the real Pokemon types"""
    pass


class InvalidPokemonRegion(Exception):
    """Raise if Pokemon Region is not valid"""
    pass


if __name__ == '__main__':
    app.run()
