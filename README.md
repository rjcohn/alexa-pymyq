# Recent Updates

* 29 Dec 2020: Created based on https://github.com/tigerbrain/Alexa-MyQ-WithMultiDoorSupport.

--------------------------------------

# Enable Alexa to Control Your MyQ Garage Opener
Use Alexa to activate your Chamberlain/LiftMaster MyQ garage gateway that is connected to one or two doors.

## Summary
By using the Alexa Skills Kit, you can control your Chamberlain or LiftMaster MyQ garage
door through your Amazon Echo device.
Many thanks for previous work:
* https://github.com/tigerbrain/Alexa-MyQ-WithMultiDoorSupport
  the code that this skill is directly based on.
* https://github.com/jbnunn/Alexa-MyQGarage
  the original skill for a one-car garage.
* https://github.com/pfeffed/liftmaster_myq
  the Ruby API that Alexa-MyQGarage adapted to Python.

The major changes from Alexa-MyQ-WithMultiDoorSupport:

* Move to latest (simplified) Alexa framework.
* Move to Python 3.
* Move to [PyMyQ](https://github.com/arraylabs/pymyq).

## Instructions

1.  Create a free Amazon developer account or sign in at https://developer.amazon.com/alexa.

2.  On the Amazon Alexa developer main page, click on the three dots at top right
and choose "Alexa Developer Console".

3.  Click Create Skill to add a new skill.

    * Provide the following settings:

      * Skill name: _Your own custom skill name such as Operate Garage_

      * Default language: _Your preferred language_

      * Choose a model to add to your skill: Custom

      * Choose a method to host your skill's backend resources: Alexa-hosted (Python)

    * Click Create skill

4.  Choose a template: Start from Scratch

    * Click Continue with template.

    * Click Invocation on the left.
    Provide a Skill Invocation Name (My Garage).

    * Click Interaction Model and then JSON Editor on the left.
    Paste the contents of interaction_model.json here.

    * Click Build Model

5.  Click the Code tab

    * Replace the contents of lambda_function.py with the lambda_function.py file.

    * Replace the contents of requirements.txt all but the last two lines of requirements.txt.
    This leaves out test packages -- if you forget, it won't hurt to include them.

    * Click New file to create lambda/.env with this content:
    ```
        USER_NAME=<Your MyQ account user name>
        PASSWORD=<Your MyQ account password>
        ONLY_CLOSE=<Y or N. Enter Y if you don't want Alexa to open doors for security reasons.>
        LEFT=<0 or 1. Door 0 is the door first set up with MyQ. If you're unsure try 0.
              If the wrong door opens, switch from 0 to 1.>
    ```
    * Click Deploy

6.  Click the Test tab (Optional)

    You may proceed to the next step and try out the commands directly with Alexa
    or you may opt to do a simulation test to verify that you did everything
    correctly by saying or typing a command.

7. Congratulations!  You are now ready to test your skill by giving Alexa the
    commands below:

    Assuming that your skill invocation name is "Garage"

    If your MyQ unit is only linked to a single garage door, you would say:

        "Alexa, ask GARAGE if DOOR is open"
        OR
        "Alexa, ask GARAGE DOOR to close"

    If your MyQ unit is linked to two garage doors, you would say:

        "Alexa, ask GARAGE if THE LEFT DOOR is open"
        OR
        "Alexa, ask GARAGE if THE RIGHT DOOR is closed"
        OR
        "Alexa, ask GARAGE what's up"

    In addition, for units linked to two garage doors, you may also drop the
    DOOR keyword and just say:

        "Alexa, ask GARAGE LEFT to close"
        OR
        "Alexa, ask GARAGE if RIGHT is open"

## Troubleshooting Tips

IMPORTANT:  Before attempting to troubleshoot an issue, first verify that Alexa and AWS Lambda are fully up and
 running by checking their status on the [AWS Service Health Dashboard](https://status.aws.amazon.com/).

Viewing the skill logs can usually tell you what's gone wrong.
Go to the Alexa Developer Console, click the Code tab and then click the Logs icon.
This takes you to CloudWatch, where you can check the logs  with the most recent
one at the top of the list.
For more detailed logging, add `LOG_LEVEL=DEBUG` to .env and redeploy.
The most common problem is that Chamberlain makes an incompatible change to their server.
Look for an update to this code or possibly to [PyMyQ](https://github.com/arraylabs/pymyq>)
if this is the problem.

### Alexa Skills Kit Documentation
The documentation for the Alexa Skills Kit is available on the
[Amazon Alexa Portal](https://developer.amazon.com/en-US/alexa).

### Disclaimer

The code here is based off of an unsupported API from [Chamberlain](http://www.chamberlain.com/)
and is subject to change without notice.
The authors claim no responsibility for damages to your garage door or property by use of the code within.
