import json
import os
from pathlib import Path

import pytest

from lambda_function import lambda_handler

# Tests assume there are two doors and both are closed

# Set this to false to test open/close commands
# Even when true, tests will still authenticate and get current state
MOCK_MYQ_COMMANDS = True


def slot_value(slot_type, spoken_value, name=None, value_id=None):
    if name is None:
        name = spoken_value
    if value_id is None:
        value_id = name
    return {
        'value': spoken_value,
        'resolutions': {
            'resolutionsPerAuthority': [
                {
                    'authority': f'amzn1.er-authority.echo-sdk.<skill_id>.{slot_type}',
                    'status': {
                        'code': 'ER_SUCCESS_MATCH'
                    },
                    'values': [
                        {
                            'value': {
                                'name': name,
                                'id': value_id
                            }
                        }
                    ]
                }
            ]
        }
    }


left_door_name = slot_value('DoorName', 'the left door', 'left')
one_door_name = slot_value('DoorName', '1', 'left')
both_door_name = slot_value('DoorName', 'both doors', 'both')
closed_door_state = slot_value('DoorState', 'closed')
open_door_action = slot_value('DoorCommand', 'open')
close_door_action = slot_value('DoorCommand', 'shut', 'close')


@pytest.fixture()
def event():
    with Path('event.json').open() as f:
        return json.load(f)


def test_launch(event):
    event['request']['type'] = 'LaunchRequest'
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'].startswith('You can open or close the left or right door')


def test_state(event):
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {
        'name': 'StateIntent',
        'slots': {
            'Name': left_door_name,
            'State': closed_door_state
        }}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == 'Yes, the left door is closed'


def test_all_states(event):
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'AllStatesIntent'}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == 'Both doors are closed'


def test_only_close(event, mocker):
    mocker.patch.dict(os.environ, {'ONLY_CLOSE': 'Y'})
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'MoveIntent',
                                  'slots': {
                                      'Name': left_door_name,
                                      'Command': open_door_action
                                  }}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == 'Sorry, I can only close the door'


def test_open(event, mocker):
    if MOCK_MYQ_COMMANDS:
        mocker.patch('pymyq.device.MyQDevice.open')
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'MoveIntent',
                                  'slots': {
                                      'Name': left_door_name,
                                      'Command': open_door_action
                                  }}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == 'Ok, opening the left door now'


# WARNING: this will close the actual door if it is open
def test_close(event, mocker):
    if MOCK_MYQ_COMMANDS:
        mocker.patch('pymyq.device.MyQDevice.close')
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'MoveIntent',
                                  'slots': {
                                      'Name': one_door_name,
                                      'Command': close_door_action
                                  }}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == '1 is already closed'


# WARNING: this will close the actual doors if they are open, but test assumes they are closed
def test_close_all(event, mocker):
    if MOCK_MYQ_COMMANDS:
        mocker.patch('pymyq.device.MyQDevice.close')
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'MoveIntent',
                                  'slots': {
                                      'Name': both_door_name,
                                      'Command': close_door_action
                                  }}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == 'Both doors are closed'


def test_help(event):
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'AMAZON.HelpIntent'}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'].startswith('You can open or close the left or right door')


def test_stop(event):
    event['request']['type'] = 'IntentRequest'
    event['request']['intent'] = {'name': 'AMAZON.StopIntent'}
    result = lambda_handler(event)
    assert result['response']['outputSpeech']['text'] == 'Goodbye'
