import gettext
import pycountry
pycountry_german = gettext.translation('iso3166', pycountry.LOCALES_DIR,languages=['de'])
pycountry_german.install()

