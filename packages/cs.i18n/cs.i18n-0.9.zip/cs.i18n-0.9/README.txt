=========
 cs.i18n
=========

We found ourselves constantly changing the way Plone and LinguaPlone
show the language change forms.

We don't like the way Plone and LinguaPlone have for showing the
language change in a combo-box using Javascript to redirect the user
when no flags are used.

We want to have a simple product that just needs to be put in the
PYTHONPATH, install it, and have plaintext links to get the language
changed.

We think that the language names must be shown in the native language:
Espanol, Français, Euskara or English, not always in English or in the
interface's language.

This is what our product does. You have just had to disable the "show
flags" checkbox in the portal_languages (for now in the ZMI, until
someone ports LinguaPlone's language control panel to Plone and adds
all that features it had beforehand, but we have no hope for this, 
because Wiggy said in a mailing list that they don't want to release 
an out-of-the-box language-changeable Plone)..

So, if you want to have plain-text links without Javascript, and
language names in the native language, this is your product !

(and is my first Python egg ;))
