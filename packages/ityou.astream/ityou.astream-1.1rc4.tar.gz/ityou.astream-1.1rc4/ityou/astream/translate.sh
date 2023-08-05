#!/bin/sh
#
# Shell script to manage .po files.
# Run this file in the folder main __init__.py of product
# E.g. if your product is yourproduct.name
# you run this file in yourproduct.name/yourproduct/name
# Copyright 2009 Twinapex Research http://www.twinapex.com
# Assume the product name is the current folder name

CURRENT_PATH=`pwd`
CATALOGNAME="ityou.astream"
I18NDUDE_HOME="/srv/zope/esi/Python-2.6/bin"

# List of languages
LANGUAGES="de en fr"



# Create locales folder structure for languages
echo "========= start ============="
install -d locales
for lang in $LANGUAGES; do
    install -d locales/$lang/LC_MESSAGES
done

# Rebuild .pot

echo "REBUILDING POT-File ...."
$I18NDUDE_HOME/i18ndude rebuild-pot --pot locales/$CATALOGNAME.pot --create $CATALOGNAME .
echo "... finisched"
echo


# Compile po files
echo "COMPILING PO-Files ..."
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then

        PO=$lang/LC_MESSAGES/${CATALOGNAME}.po

        # Create po file if not exists
        touch $PO

        # Sync po file
        echo "Syncing $PO"
        $I18NDUDE_HOME/i18ndude sync --pot locales/$CATALOGNAME.pot $PO

        # Compile .po to .mo
        MO=$lang/LC_MESSAGES/${CATALOGNAME}.mo
        echo "Compiling $MO"
        msgfmt -o $MO $lang/LC_MESSAGES/${CATALOGNAME}.po
    fi
done
echo "finished compiling. "
echo "========= end ========================="

