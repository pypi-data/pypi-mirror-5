#!/bin/bash

# don't forget to activate your i18ndude workingenv before running this
# script.

I18NDUDE="../../../../../bin/i18ndude"
PRODUCTNAME="collective.contentrules.mailtorole"
I18NDOMAIN=$PRODUCTNAME

# Synchronise the .pot with the templates.
# Also merge it with generated.pot, which includes the items
# from schema.py

$I18NDUDE rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${I18NDOMAIN} --merge locales/manual.pot .

# Synchronise the resulting .pot with the Dutch .po files
$I18NDUDE sync --pot locales/${PRODUCTNAME}.pot locales/nl/LC_MESSAGES/${PRODUCTNAME}.po

# Zope3 is lazy so we have to compile the po files ourselves
msgfmt -o locales/nl/LC_MESSAGES/${PRODUCTNAME}.mo locales/nl/LC_MESSAGES/${PRODUCTNAME}.po
