Rebuild the pot file and merge the manual pot file in it:
i18ndude rebuild-pot --pot locales/ityou.whoisonline.pot --merge locales/extra.pot --create ityou.whoisonline .

Synchronize the pot file with the po files 
i18ndude sync --pot locales/ityou.whoisonline.pot locales/de/LC_MESSAGES/ityou.whoisonline.po