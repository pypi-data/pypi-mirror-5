*** Settings ***

Resource  plone/app/robotframework/server.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/annotate.robot

Suite Setup  Setup
Suite Teardown  Teardown
Test Setup  Test Setup
Test Teardown  Test Teardown

*** Variables ***

${TEST_LAYER}  collective.behavior.localskin.testing.COLLECTIVE_BEHAVIOR_LOCALSKIN_ROBOT_TESTING

*** Keywords ***

Setup
    Setup Plone site  ${TEST_LAYER}

Test Setup
    Import library  Remote  ${PLONE_URL}/RobotRemote
    Enable autologin as  Manager
    Set autologin username  test-user-1

Test Teardown
    Set Zope layer  ${TEST_LAYER}
    ZODB TearDown
    ZODB SetUp

Teardown
    Teardown Plone Site

New microsite
    [Arguments]  ${title}
    Go to  ${PLONE_URL}
    Open add new menu
    Click link  microsite
    Input text for sure  form-widgets-IBasic-title  ${title}
    Click button  Save
    Page should contain  Item created

New microsite with skin
    [Arguments]  ${title}  ${skinname}
    New microsite  ${title}
    Click link  ${title}
    Click link  Edit
    Select from list  form-widgets-ILocalSkin-skinname  Plone Default
    Click button  Save
    Page should contain  Changes saved

*** Test Cases **

Activate behavior
    Go to  ${PLONE_URL}/dexterity-types/MicroSite/@@behaviors
    ${note} =  Add note
    ...    css=label[for="form-widgets-collective-behavior-localregistry-behavior-ILocalRegistry-0"]
    ...    At first, enable both Local registry and Local skin theme -behaviors for your type.
    ...    width=300  position=right
    Capture page screenshot  01-activate-behaviors.png

Create microsite
    Go to  ${PLONE_URL}/++add++MicroSite
    ${note} =  Add note
    ...    form-buttons-save
    ...    Then create and save a new content of your type.
    ...    width=350  position=right
    Capture and crop page screenshot   02-create-microsite.png  ${note}
    ...    css=h1.documentFirstHeading
    ...    form-buttons-save

Select local skin
    New microsite with skin  My MicroSite  Plone Default
    Go to  ${PLONE_URL}/my-microsite/edit
    ${note} =  Add note
    ...    form-widgets-ILocalSkin-skinname
    ...    Finally, edit the type again to be able to select the local skin.
    ...    width=300  position=right
    Capture and crop page screenshot   03-select-local-skin.png  ${note}
    ...    css=h1.documentFirstHeading
    ...    formfield-form-widgets-ILocalSkin-skinname
    ...    form-widgets-ILocalSkin-skinname
    ...    form-buttons-save

Have microsite with local skin
    New microsite with skin  My MicroSite  Plone Default
    Go to  ${PLONE_URL}/my-microsite
    ${note} =  Add note
    ...    css=h1.documentFirstHeading
    ...    Enjoy!  width=60
    Capture page screenshot  04-have-local-skin.png
