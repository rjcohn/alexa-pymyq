# Recent Updates

* 22 Apr 2021: Revert to old instructions that support Pythone 3.8 (required by PyMyQ 3.0.4)
* 23 Feb 2021: Update to PyMyQ 3.0.4
* 13 Jan 2021: Update to PyMyQ 2.0.14 to fix API issues
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

* Move to Python 3.8 (required by PyMyQ).
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

      * Choose a method to host your skill's backend resources: Provision your own

    * Click Create skill at the top right.

4.  Choose a template: Start from Scratch

    * Click Choose at the top right.

    * Click Invocation on the left.
    Provide a Skill Invocation Name: "my garage" or a name of your choice.

    * Click Interaction Model and then JSON Editor on the left.
    Paste the contents of interaction_model.json here, replacing the Hello World contents.

    * Click Build Model at top.

5.  Click on Your Skills to return to the list of skills.

    * Click Copy Skill ID of your new skill.

      Sample Application ID:  amzn1.ask.skill.2dc3256e-f143-41a6-ab8f-194c3df2d789

6. In a new browser tab, go to https://aws.amazon.com.
   Sign in as the root user or create a new account.
   
    * At the top right, to the right of your name, if the location is not N. Virginia,
      choose US East (N. Virginia) us-east-1.
      
    * Search for the Lambda service.
    
7. Click Create function at the top right.

    * Provide the following information under Basic information:
    
      * Function name: A name without spaces such as OperateGarage
      * Runtime: Python 3.8
    
    * Click Create function.
    
8. On the function page, click Add trigger.

    * Choose Alexa Skills Kit as the trigger.
      (If it's not available, make sure you have set the region to N. Virginia.)
      
    * Paste the skill ID from the Alexa console.
    
    * Click Add.
    
9. Click General configuration on the left.
   
    * Click Edit.
    * Change the Timeout value to 5 sec.
    * Click Save.
    
10. Click Environment variables on the left.

    * Click Edit.
    * Click Add environment variable to add the following variables:
        * Key: USER_NAME
          
          Value: your MyQ account user name
        * Key: PASSWORD
    
          Value: Your MyQ account password
        * Key: ONLY_CLOSE
          
          Value: Y or N. Enter Y if you don't want Alexa to open doors for security reasons.
        * Key:  LEFT
    
          Value: 0 or 1. Door 0 is the door first set up with MyQ. If you're unsure, try 0.
          After deployment, if the wrong door opens, switch from 0 to 1.
    * Click Save.
    
11. Click the Code tab (below Add trigger)
    
    * Click Upload from on the right and choose .zip file.
    * Click Upload and choose lambda-upload.zip. 
    * Click Save.

12. Click the Test tab (Optional)
    
    * Enter HelpIntent as the Name.
    * Replace the event JSON with the contents of tests/HelpIntent.json.
    * Click Save changes
    * Click Test

    If you've done everything correctly, you should see "Execution result: succeeded (logs)".
    This test only communicates with Alexa and not your garage.
    If it failed, verify all the steps above.
    
    * Choose New event
    * Enter TestAllStates as the Name.
    * Replace the event JSON with the contents of tests/TestAllStates.json.
    * Click Save changes
    * Click Test

    If the test succeeds, you should see "Execution result: succeeded (logs)" again.
    The log output should show your actual door state (open or closed).
    If the test fails, make sure you have set up the environment variables correctly.
    
13. In the Function overview, copy the Function ARN by clicking the Copy icon.

14. Return to your Amazon developer account >> Alexa >> Alexa Skills Kit project and
    edit the custom skill that you have already started creating back in step 5.
    
    * Choose Endpoint on the left.
    * Paste the function ARN as the value of the Default Region.
    * Click Save Endpoints
    
15. Click Build at the top.

    * Click Build Model on the right.
    * Wait for "Full Build Successful"
    
16. Click Test at the top.

    * Change the pulldown value form Off to Development.
    
7. Congratulations!  You are now ready to test your skill by giving Alexa the
    commands below:

    Assuming that your skill invocation name is "my garage"

    If your MyQ unit is only linked to a single garage door, you would say:

        "Alexa, ask MY GARAGE if DOOR is open"
        OR
        "Alexa, ask MY GARAGE DOOR to close"

    If your MyQ unit is linked to two garage doors, you would say:

        "Alexa, ask MY GARAGE if THE LEFT DOOR is open"
        OR
        "Alexa, ask MY GARAGE if THE RIGHT DOOR is closed"
        OR
        "Alexa, ask MY GARAGE what's up?"

    In addition, for units linked to two garage doors, you may also drop the
    DOOR keyword and just say:

        "Alexa, ask MY GARAGE LEFT to close"
        OR
        "Alexa, ask MY GARAGE if RIGHT is open"

## Troubleshooting Tips

IMPORTANT:  Before attempting to troubleshoot an issue, first verify that Alexa and AWS Lambda are fully up and
 running by checking their status on the [AWS Service Health Dashboard](https://status.aws.amazon.com/).

Viewing the skill logs can usually tell you what's gone wrong.
Go to the Alexa Developer Console, click the Code tab and then click the Logs icon.
This takes you to CloudWatch, where you can check the logs  with the most recent
one at the top of the list.
For more detailed logging, add `LOG_LEVEL=DEBUG to the environment variables and redeploy.
The most common problem is that Chamberlain makes an incompatible change to their server.
Look for an update to this code or possibly to [PyMyQ](https://github.com/arraylabs/pymyq>)
if this is the problem.

To see logs, go to your lambda function in the AWS Console and click Monitor.
From there, you can look at CloudWatch metrocis or go directly to the logs.

You can also go to Alexa console and test commands by clicking on the Test tab.

You can say or enter commands there:

* open my garage
* ask my garage what's up
* ask my garage to close the left door

### Alexa Skills Kit Documentation
The documentation for the Alexa Skills Kit is available on the
[Amazon Alexa Portal](https://developer.amazon.com/en-US/alexa).

### Disclaimer

The code here is based off of an unsupported API from [Chamberlain](http://www.chamberlain.com/)
and is subject to change without notice.
The authors claim no responsibility for damages to your garage door or property by use of the code within.
