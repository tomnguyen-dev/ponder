import requests
from PIL import Image
import speech_recognition as sr
import urllib.request
import os
PySimpleGUI_License = 'eVygJXMUaMWINBl6bznHNzl3VwH8l9wzZqSJIb6zIAkIRUlOdambVzstb13ZB8lWcDiRIRsoIokpxwpZYP2OVfuNcp2SVpJ9R5CVI56wMOT4c3x9OvD5UD37MADAQY09MJCVwfiSTqGjlij5ZQWM5EzWZtUDRKlJcbGHxUvOe2Wn10lpb7nsRNWLZOXhJrzFakWn9EuuIBj6oRxRLKCCJrOLYlWM1el9RKmaluyscF3OQTiTOfiQJPUQbD220wijLMCcJcOQYQWI10lAT7G0FRzldJCwIJ6gIekN50nLdGXKlplObsinIkstI8kVNPvvbzXDBghWb3n8kqiuOwivIbimL8CHJFDFd2XhND0Cbt2r1bl7cCkMlcEMIYjaoGieMijLUt5bMlDxU8ijLtCEJ4EQYMX3RHl9SDXyNhzydRWWVykrI6jnosiOMBDsYJv9MkTYcTvGMTjyAjywNZCqIUsEIukhRph5dJG8V5FDe0HKBLp5cimTVxzGIQjco1iCMaDqYzvlMnT3cav6MDjgAoyWNkSUI7sSI8kdVjtUYyWOljsPQWWmRhk9cgmUVXzQcky1Il6OIQn3RpvybtWI5qnSdhXtl1lQbUjfAb4GM3T8dvAsZW2e1dhPaeWCwcupYj2t9ethIri8wMiTSAVtBfBjZRGIREysZyXiNwzzISjQo6iQN8DTcRuYM2TVgf4pLVjaUr01LYjAkC3QIInN01=A30ba08771ae8d8df7ff80eebbdfe03317730b3d9b19c92c2e12d956ac4b04b7e04047c649ed620e8c1b25b5f5630b30d933eebb72f2debb20e0e252590990b1173db779cacaeea1e414ba8d19edbdfb55dbf5044e017c7946453c2b07f1f8bcd17028a9e24d2f9c96dceb5881f901acaedf752756e4d6dc25b95373ab63fef91db626b75fc13aadb02fbcd7518353ee696e7bc3db408c8a3a69c7bf7c47c57b16bb097ffba867920315fd0015d03347baff088283a086219b37cef8e473464d1a00dc61349ccef573e4a0f8983a389975e1df61dbf5346d0423ca49d53d640831cbe8eccf9a86ac11f3a99d0584b41b89c8cd80677b4f53a04b395e80fdfe7b4599a3db7f119ea1e588a642bdae7e3517e74c235b5a98c11966cdb94ca9c2ab16a1894d3f82974ecda084e0aefc1d7381f21a961060348a68eaf691b62d1d64a3c998ccf00ef7b04f6ad8db315857ecaa6942c8a4105c0216722065c00986cf6d2ce89d46e7fd3bb7cebe8eb1bf7cbf01f3b4c609d860a349b81d6f534e83cfb2a3445a59ec4814d8b2e776f15421a89136bbac3d126d769807b53c8e9347fd6f53c96f801276063bf0f11f7c96fffb8d32de0ca417e83f11983e18bb6644a33d895ad33f0830efb2f9bf7f0cb9b836f16cce08aa05936558f063c901dc4e090b3b1c0713b3456f102d485aab280b1e1ea8b7f7c117a87bbe709c757f249914f'
import PySimpleGUI as sg
import re

# clear out previous file
if os.path.exists('temp.png'):
    os.remove('temp.png')

# scryfall API
url = 'https://api.scryfall.com/cards/named?exact='

BACKGROUND_COLOR = '#3E3C3C'

card_name='notion+thief'

class Card:
    def __init__(self, name, rules, oracle_text):
        self.name = name
        self.rules = rules
        self.oracle_text = oracle_text

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Say Card Name!')
        audio = r.listen(source)

    # recognize with Google Speech
    try:
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio) + '\n--------------------------------------------------\n')
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def find_card():
    while True:
        # UNCOMMENT IN FINAL
        # user_input = get_audio()
        # card_name = user_input.replace(' ', '+').lower()

        response = requests.get(url+card_name + '&format=json')

        if response.status_code == 200:
            break

    card = Card(None, [], None)

    # rulings uri
    rulings_uri = response.json()['rulings_uri']
    rule_response = requests.get(rulings_uri)
    card.rules = rule_response.json()['data']

    # oracle text
    card.oracle_text = response.json()['oracle_text']

    # get image
    image_url = response.json()["image_uris"]["png"]
    urllib.request.urlretrieve(image_url, 'temp.png')

    return card

def process_ruling_text(card):
    rule_str = ''
    rule_cnt = 0

    for rule in card.rules:
        rule_cnt += 1
        rule_str = rule_str + ('\n> ' + rule['comment'] + '\n')

    return str(rule_cnt), rule_str


card = find_card()

rule_cnt, rule_str = process_ruling_text(card)

column = [
    [sg.Image('temp.png', key="-IMAGE-", background_color=BACKGROUND_COLOR)],

    [sg.Text('ORACLE TEXT', font='bold', background_color=BACKGROUND_COLOR)],
    [sg.Multiline(card.oracle_text, size=(60,5), key='-ORACLE-', text_color='white', font='bold', background_color=BACKGROUND_COLOR, no_scrollbar=True)],

    [sg.Text('\nRULES (' + rule_cnt + ')', font='bold', background_color=BACKGROUND_COLOR)],
    [sg.Multiline(rule_str, size=(60,10), key='-RULES-', text_color='white', font='bold', background_color=BACKGROUND_COLOR, no_scrollbar=True)]
]

layout = [
    [sg.Column(column, scrollable=True, vertical_scroll_only=True,background_color=BACKGROUND_COLOR)],

    [sg.Button('Voice Search', font='bold')]
]

window = sg.Window('Ponder', layout, background_color=BACKGROUND_COLOR, element_justification='c')

while True:
    event, values = window.read()

    if event == 'Voice Search':
        card = find_card()
        rule_cnt, rule_str = process_ruling_text(card)

        # refresh elements
        window['-IMAGE-'].update('temp.png')
        window['-ORACLE-'].update(card.oracle_text)
        window['-RULES-'].update(rule_str)
        window.refresh()

    if event == sg.WIN_CLOSED:
            break

