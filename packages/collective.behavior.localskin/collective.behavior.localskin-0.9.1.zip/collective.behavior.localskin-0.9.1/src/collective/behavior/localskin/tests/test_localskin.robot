*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Open SauceLabs test browser  Background
Test Teardown  Run keywords  Report test status  Close all browsers

*** Keywords ***

Background
    Enable autologin as  Member  Contributor  Editor
    Set autologin username  test-user-

At
    [Arguments]  ${location}
    Go to  ${location}

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
    Page source should contain  portal_css/Plone%20Default

Page source should contain
    [Arguments]  ${needle}
    ${source} =  Get source
    Should contain  ${source}  ${needle}

Page source should not contain
    [Arguments]  ${needle}
    ${source} =  Get source
    Should not contain  ${source}  ${needle}

*** Test cases ***

Plone is up
    When go to  ${PLONE_URL}
    Then page should contain element  content-core

MicroSite is available to be added
    Given at  ${PLONE_URL}
    When open add new menu
    Then element should be visible  microsite

MicroSite can be added
    Given at  ${PLONE_URL}
    When open add new menu
     and click link  microsite
     and input text for sure  form-widgets-IBasic-title  My MicroSite
     and click button  Save
    Then page should contain  Item created

MicroSite can have its own skin
    Given new microsite  My MicroSite
      and at  ${PLONE_URL}/my-microsite/edit
     When select from list  form-widgets-ILocalSkin-skinname  Plone Default
      and click button  Save
     Then page should contain  Changes saved
      and page source should contain  portal_css/Plone%20Default
      and page source should not contain  portal_css/Sunburst%20Theme

MicroSite skin does not affect the main site skin
    Given new microsite with skin  My MicroSite  Plone Default
     When go to  ${PLONE_URL}
     Then page source should contain  portal_css/Sunburst%20Theme
      and page source should not contain  portal_css/Plone%20Default
