#!/bin/sh

DOMAIN='cciaa.portlet.calendar'

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --create ${DOMAIN} .
i18ndude merge --pot locales/${DOMAIN}.pot --merge locales/${DOMAIN}-manual.pot
i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

i18ndude rebuild-pot --pot ./i18n/plone.pot --create plone profiles/default
i18ndude sync --pot i18n/plone.pot i18n/plone-??.po
