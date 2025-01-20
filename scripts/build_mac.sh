#!/bin/bash

echo "========= SimpleToolSuite macOS Build Script ========="


echo " => Cleaning up previous builds!"
rm -f ./dist/simpletoolsuite


echo " => Creating and activating virtual environment..."
python3 -m venv venv
source ./venv/bin/activate


echo " => Upgrading pip and installing necessary dependencies..."
venv/bin/pip install --upgrade pip wheel pyinstaller
venv/bin/pip install -r requirements.txt


echo " => Running PyInstaller to create executable..."
pyinstaller --onefile \
    --add-data "src/simpletoolsuite/*.ui:simpletoolsuite" \
    --add-data "src/simpletoolsuite/*.css:simpletoolsuite" \
    --name="SimpleToolSuite" \
    --icon="src/simpletoolsuite/simpletoolsuite.png" \
    src/portable.py


echo " => Setting executable permissions..."
chmod +x dist/SimpleToolSuite.app


echo " => Creating dmg..."
mkdir -p dist/dmg
mv dist/SimpleToolSuite.app dist/dmg/SimpleToolSuite.app
ln -s /Applications dist/dmg
hdiutil create -srcfolder dist/dmg -format UDZO -o dist/SimpleToolSuite.dmg


echo " => Cleaning up temporary files..."
rm -rf __pycache__ build venv *.spec


echo " => Done!"
