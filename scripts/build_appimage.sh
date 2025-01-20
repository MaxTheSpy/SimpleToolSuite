#!/bin/bash

echo "========= SimpleToolSuite AppImage Build Script ==========="


echo " => Cleaning up !"
rm -rf dist build


echo " => Fetch Dependencies"
mkdir build
cd build

curl -L -o appimagetool-x86_64.AppImage https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

curl -L -o python.AppImage https://github.com/niess/python-appimage/releases/download/python3.12/python3.12.8-cp312-cp312-manylinux2014_x86_64.AppImage
chmod +x python.AppImage

./python.AppImage --appimage-extract
mv squashfs-root SimpleToolSuite.AppDir


echo " => Build SimpleToolSuite.whl"
cd ..
build/SimpleToolSuite.AppDir/AppRun -m build


echo " => Prepare SimpleToolSuite AppImage"
cd build/SimpleToolSuite.AppDir
./AppRun -m pip install -r ../../requirements.txt
./AppRun -m pip install ../../dist/simpletoolsuite-*-py3-none-any.whl

rm AppRun .DirIcon python.png python*.desktop usr/share/applications/python*.desktop

cp -t . ../../src/simpletoolsuite/simpletoolsuite.png ../../src/simpletoolsuite/org.simpletoolsuite.SimpleToolSuite.desktop
cp ../../src/simpletoolsuite/resources/org.simpletoolsuite.SimpleToolSuite.desktop usr/share/applications/

echo '#! /bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH=$HERE/usr/bin:$PATH;
export APPIMAGE_COMMAND=$(command -v -- "$ARGV0")
export TCL_LIBRARY="${APPDIR}/usr/share/tcltk/tcl8.6"
export TK_LIBRARY="${APPDIR}/usr/share/tcltk/tk8.6"
export TKPATH="${TK_LIBRARY}"
export SSL_CERT_FILE="${APPDIR}/opt/_internal/certs.pem"
"$HERE/opt/python3.12/bin/python3.12" "-m" "simpletoolsuite" "$@"' > AppRun

chmod -R 0755 ../SimpleToolSuite.AppDir
chmod +x AppRun


echo " => Build SimpleToolSuite AppImage"
cd ..
./appimagetool-x86_64.AppImage --appimage-extract
squashfs-root/AppRun SimpleToolSuite.AppDir

mv SimpleToolSuite-x86_64.AppImage ../dist/SimpleToolSuite-x86_64.AppImage


echo " => Done "
