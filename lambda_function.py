"""AWS Lambda function to support an Alexa skill that opens and closes one or two garage doors.

Pymyq provides access to the Chamberlain API.

The Alexa interaction model assumes:
- door states in the API contain all the DoorState values
- door commands in the API contain the DoorCommand values

See https://github.com/arraylabs/pymyq/blob/master/pymyq/device.py
"""

import asyncio
import logging
from typing import TYPE_CHECKING

import pymyq
from aiohttp import ClientSession
from environs import Env
from pymyq.api import API

if TYPE_CHECKING:
    from pymyq.garagedoor import MyQGaragedoor

# load system env vars and read .env (set override=True for .env values to override existing vars)
env = Env()
env.read_env(override=False)

logger = logging.getLogger()
logger.setLevel(env.log_level('LOG_LEVEL', logging.INFO))


class GarageRequestHandler:
    """Handle a request by the garage skill"""

    myq: API

    user_name: str
    password: str

    # The order of the doors returned in the MyQ covers dictionary.
    # Using order (while arbitrary) is simpler than specifying the names of the left and right doors.
    left_door: int
    right_door: int

    # By default, the skill will not open the door. Set env var NO_OPEN to 'No'
    only_close: bool

    def __init__(self):
        self.validate_env()

        # information messages that may be modified if there is only one door
        self.move_msg = 'close the left or right door'
        if not self.only_close:
            self.move_msg = 'open or ' + self.move_msg
        self.check_msg = "check the state of your garage door by asking what's up"
        self.check1_msg = 'check the state of your garage door by asking if the left or right door is open'

    def validate_env(self) -> None:
        """Make sure environment is set up correctly. Else raise an exception."""
        errors = []

        self.user_name = env.str('USER_NAME')
        if not self.user_name:
            errors.append('USER_NAME environment variable needs to be set to your MyQ user name')

        self.password = env.str('PASSWORD')
        if not self.password:
            errors.append('PASSWORD environment variable needs to be set to your MyQ password')

        self.left_door = env.int('LEFT', 0)
        self.right_door = 1 - self.left_door

        self.only_close = env.bool('ONLY_CLOSE', True)

        if errors:
            raise Exception(','.join(errors))

    # see https://developer.amazon.com/blogs/alexa/post/
    # 5882651c-6377-4bc7-bfd7-0fd661d95abc/entity-resolution-in-skill-builder
    @staticmethod
    def slot_value_id(intent, slot):
        return intent['slots'][slot]['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']

    def has_one_door(self):
        return len(self.myq.covers) == 1

    def get_door(self, device_ind: int) -> 'MyQGaragedoor':
        return list(self.myq.covers.values())[device_ind]

    def get_door_index(self, door_name: str) -> int:
        """Convert a door name to an index"""
        if door_name == 'left':
            return self.left_door
        elif door_name == 'right':
            return self.right_door
        elif door_name == 'both':
            return 0
        else:
            return int(door_name) - 1

    def status(self, device_ind: int) -> str:
        door = self.get_door(device_ind)
        logger.info(f'Check door state: {door.name} ({device_ind}) is {door.state}')
        return door.state

    async def open_door(self, device_ind: int) -> None:
        door = self.get_door(device_ind)
        logger.info(f'Change door state: {door.name} ({device_ind}) is {door.state}')
        await door.open()

    async def close_door(self, device_ind: int) -> None:
        door = self.get_door(device_ind)
        logger.info(f'Change door state: {door.name} ({device_ind}) is {door.state}')
        await door.close()

    # Called when the user launches the skill without specifying what they want.
    def on_launch(self) -> dict:
        return self.get_welcome_response()

    # Called when the user specifies an intent for this skill.
    async def on_intent(self, intent: dict) -> dict:
        intent_name = intent['name']
        if intent_name == 'StateIntent':
            return self.execute_state_intent(intent)
        elif intent_name == 'AllStatesIntent':
            if self.has_one_door():
                return self.execute_state1_intent()
            else:
                return self.execute_all_states_intent()
        elif intent_name == 'MoveIntent':
            return await self.execute_move_intent(intent)
        elif intent_name == 'AMAZON.HelpIntent':
            return self.get_welcome_response()
        elif intent_name in ('AMAZON.StopIntent', 'AMAZON.CancelIntent'):
            return self.execute_stop_intent()
        else:
            raise Exception(f"Invalid Intent ('{intent_name}')")

    # Called when the user ends the session.
    # Is not called when the skill returns should_end_session=true.
    @staticmethod
    def on_session_ended() -> dict:
        # Add cleanup logic here
        logger.info('Session ended')
        return {}

    def get_welcome_response(self) -> dict:
        speech_output = f'You can {self.move_msg}. You can also {self.check_msg}.'
        return self.build_speechlet_response('Welcome', speech_output)

    async def execute_move_intent(self, intent: dict) -> dict:
        # Ask garage {door|door 1|door 2} to {open|close|shut}
        #     "intent": {
        #       "name": "StateIntent",
        #       "slots": {
        #         "Name": {
        #           "name": "Name",
        #           "value": "1"
        #         }
        #         "Command": {
        #           "name": "Command",
        #           "value": "close"
        #         }
        #       }
        #     }

        failure_msg = f"I didn't understand that. You can say {self.move_msg}."
        reprompt_msg = f'Ask me to {self.move_msg}.'

        # noinspection PyBroadException
        try:
            door_name = intent['slots']['Name']['value']
            door_name_id = self.slot_value_id(intent, 'Name')
            door_action_id = self.slot_value_id(intent, 'Command')

            if door_name_id == 'both' and not self.has_one_door():
                if door_action_id == 'close':
                    return await self.execute_close_all_intent()
                else:
                    return await self.execute_open_all_intent()

            device_ind = self.get_door_index(door_name_id)
            door_state = self.status(device_ind)

            if door_action_id == 'close':
                card_title = 'Close door'
                if door_state in ('closed', 'closing'):
                    speech_output = f'{door_name} is already {door_state}'
                else:
                    await self.close_door(device_ind)
                    speech_output = f'Ok, closing {door_name} now'
            else:
                card_title = 'Open door'
                if door_state in ('open', 'opening'):
                    speech_output = f'{door_name} is already {door_state}'
                elif self.only_close:
                    speech_output = 'Sorry, I can only close the door'
                    card_title = 'Try again'
                else:
                    await self.open_door(device_ind)
                    speech_output = f'Ok, opening {door_name} now'

            return self.build_speechlet_response(card_title, speech_output)

        except Exception:
            logger.exception(f'Error executing {intent}')
            return self.build_speechlet_response('Try again', failure_msg, reprompt_msg)

    async def execute_open_all_intent(self):
        # Open all doors

        door_state_left = self.status(self.left_door)
        door_state_right = self.status(self.right_door)

        card_title = 'Open doors'

        if door_state_left not in ['open', 'opening']:
            await self.open_door(self.left_door)
        if door_state_right not in ['open', 'opening']:
            await self.open_door(self.right_door)

        if door_state_left not in ['open', 'opening'] and door_state_right not in ['open', 'opening']:
            speech_output = 'Ok, opening both garage doors now'
        elif door_state_left not in ['open', 'opening']:
            speech_output = 'Ok, opening the left garage door now'
        elif door_state_right not in ['open', 'opening']:
            speech_output = 'Ok, opening the right garage door now'
        else:
            speech_output = 'Both doors are open'

        return self.build_speechlet_response(card_title, speech_output)

    async def execute_close_all_intent(self):
        # Close all doors

        door_state_left = self.status(self.left_door)
        door_state_right = self.status(self.right_door)

        card_title = 'Close doors'

        if door_state_left not in ['closed', 'closing']:
            await self.close_door(self.left_door)
        if door_state_right not in ['closed', 'closing']:
            await self.close_door(self.right_door)

        if door_state_left not in ['closed', 'closing'] and door_state_right not in ['closed', 'closing']:
            speech_output = 'Ok, closing both garage doors now'
        elif door_state_left not in ['closed', 'closing']:
            speech_output = 'Ok, closing the left garage door now'
        elif door_state_right not in ['closed', 'closing']:
            speech_output = 'Ok, closing the right garage door now'
        else:
            speech_output = 'Both doors are closed'

        return self.build_speechlet_response(card_title, speech_output)

    def execute_state_intent(self, intent: dict) -> dict:
        # Ask garage if {door|door 1|door 2} is {open|up|closed|shut|down}
        #     'intent': {
        #       'name': 'StateIntent',
        #       'slots': {
        #         'Name': {
        #           'name': 'name',
        #           'value': '1'
        #         }
        #         'State': {
        #           'name': 'state',
        #           'value': 'closed'
        #         }
        #       }
        #     }

        failure_msg = f"I didn't understand that. You can {self.check1_msg}."
        reprompt_msg = f'Ask me to {self.check1_msg}.'

        # noinspection PyBroadException
        try:
            door_name = intent['slots']['Name']['value']
            door_name_id = self.slot_value_id(intent, 'Name')
            device_ind = self.get_door_index(door_name_id)
            door_state = intent['slots']['State']['value']
            actual_door_state = self.status(device_ind)

            if not door_state:
                speech_output = f'{door_name} is {actual_door_state}'
            else:
                door_state_id = self.slot_value_id(intent, 'State')
                if door_state_id == actual_door_state:
                    speech_output = f'Yes, {door_name} is {door_state}'
                else:
                    speech_output = f'No, {door_name} is {actual_door_state}'
            card_title = 'Check door status'

            return self.build_speechlet_response(card_title, speech_output)

        except Exception:
            logger.exception(f'Error executing {intent}')
            return self.build_speechlet_response('Try again', failure_msg, reprompt_msg)

    def execute_all_states_intent(self) -> dict:
        # Ask garage what's up

        door_state_left = self.status(self.left_door)
        door_state_right = self.status(self.right_door)

        if door_state_left == door_state_right:
            speech_output = f'Both doors are {door_state_left}'
        else:
            speech_output = f'The left door is {door_state_left}, and the right door is {door_state_right}.'
        card_title = 'Check door status'

        return self.build_speechlet_response(card_title, speech_output)

    def execute_state1_intent(self) -> dict:
        # Ask garage what's up when there's one door
        door_state = self.status(0)
        speech_output = f'The door is {door_state}.'
        card_title = 'Check door status'
        return self.build_speechlet_response(card_title, speech_output)

    def execute_stop_intent(self) -> dict:
        # Cancel or stop
        return self.build_speechlet_response('Goodbye', 'Goodbye')

    # --------------- Helpers that build all of the responses -----------------------

    @staticmethod
    def build_speechlet_response(title: str, output: str, reprompt_text: str = '') -> dict:
        # If reprompt_text is available and the user either does not reply message or says something
        # that is not understood, they will be prompted again with the reprompt_text.
        should_end_session = not reprompt_text
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Simple',
                'title': f'MyQ - {title}',
                'content': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'should_end_session': should_end_session
        }

    @staticmethod
    def build_response(session_attributes, speechlet_response) -> dict:
        return {
            'version': '1.0',
            'session_attributes': session_attributes,
            'response': speechlet_response
        }

    async def process(self, event: dict) -> dict:
        """Create the aiohttp session and run"""
        async with ClientSession() as http_session:
            self.myq = await pymyq.login(self.user_name, self.password, http_session)

            # Not using sessions for now
            session_attributes = {}

            if self.has_one_door():
                self.move_msg = self.move_msg.replace(' left or right', '')
                self.check_msg = self.check1_msg = self.check1_msg.replace(' left or right', '')

            if event['session']['new']:
                logger.info(f"New session: request_id={event['request']['requestId']}, " 
                            f"sessionId={event['session']['sessionId']}")

            request_type = event['request']['type']
            if request_type == 'LaunchRequest':
                speechlet = self.on_launch()
            elif request_type == 'IntentRequest':
                speechlet = await self.on_intent(event['request']['intent'])
            elif request_type == 'SessionEndedRequest':
                speechlet = self.on_session_ended()
            else:
                raise Exception(f'Unknown request type: {request_type}')

        # Return a response for speech output
        return self.build_response(session_attributes, speechlet)


def lambda_handler(event: dict, _context=None) -> dict:
    logger.debug(f'Event: {event}')
    handler = GarageRequestHandler()
    return asyncio.get_event_loop().run_until_complete(handler.process(event))
