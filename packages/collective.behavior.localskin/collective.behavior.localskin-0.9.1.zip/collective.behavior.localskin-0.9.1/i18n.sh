#!/bin/bash

bin/i18ndude rebuild-pot --pot src/collective/behavior/localskin/locales/collective.behavior.localskin.pot --merge src/collective/behavior/localskin/locales/manual.pot --create collective.behavior.localskin src/collective/behavior/localskin

bin/i18ndude sync --pot src/collective/behavior/localskin/locales/collective.behavior.localskin.pot src/collective/behavior/localskin/locales/*/LC_MESSAGES/collective.behavior.localskin.po
