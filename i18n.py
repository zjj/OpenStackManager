import os
import web
import gettext

curdir = os.path.abspath(os.path.dirname(__file__))
i18n_dir = curdir + '/i18n'
allTranslations = web.storage()

def get_translations(lang='en_US'):
    # Init translation.
    if allTranslations.has_key(lang):
        translation = allTranslations[lang]
    elif lang is None:
        translation = gettext.NullTranslations()
    else:
        try:
            translation = gettext.translation(
                    'messages',
                    i18n_dir,
                    languages=[lang],
                    )
        except IOError:
            translation = gettext.NullTranslations()
    return translation

def load_translations(lang):
    lang = str(lang)
    translation  = allTranslations.get(lang)
    if translation is None:
        translation = get_translations(lang)
        allTranslations[lang] = translation

        for lk in allTranslations.keys():
            if lk != lang:
                del allTranslations[lk]
    return translation

def custom_gettext(string):
    translation = load_translations(web.ctx.session.get('lang'))
    if translation is None:
        return unicode(string)
    return translation.ugettext(string)

