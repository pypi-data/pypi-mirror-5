#!/bin/sh

PRODUCTNAME='cs.navigation'
I18NDOMAIN='csnavigation'

# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --merge locales/${PRODUCTNAME}-manual.pot --create ${I18NDOMAIN} portlets
 	
# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/eu/LC_MESSAGES/${PRODUCTNAME}.po
i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/es/LC_MESSAGES/${PRODUCTNAME}.po

