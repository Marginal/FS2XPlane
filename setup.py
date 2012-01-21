#!/bin/sh

VERSION=`python -c "from version import appversion; print appversion"`
VER=`python -c "from version import appversion; print int(round(appversion*100,0))"`
RELEASE=1

rm -f FS2XPlane_${VER}_src.zip
rm -f fs2xplane-$VERSION-$RELEASE.noarch.rpm
rm -f fs2xplane_$VERSION-$RELEASE_all.deb
rm -f FS2XPlane_${VER}_mac.zip
rm -rf FS2XPlane.app

PY='fs2xp.py FS2XPlane.py convbgl.py convmain.py convmdl.py convobjs.py convphoto.py convtaxi.py convutil.py convxml.py MessageBox.py version.py'
DATA='FS2XPlane.html bglxml.copying.txt Squish_license.txt'
RSRC='Resources/*.bgl Resources/*.dds Resources/*.obj Resources/*.png Resources/*.txt Resources/Rwy12.xml'

# linux
RPM=/tmp/fs2xplane
RPMRT=$RPM/root
rm -rf $RPM
mkdir -p $RPM/BUILD
mkdir -p $RPM/SOURCES
mkdir -p $RPM/SPECS
mkdir -p $RPM/RPMS/noarch
mkdir -p $RPMRT/usr/local/bin
mkdir -p $RPMRT/usr/local/lib/fs2xplane/Resources
mkdir -p $RPMRT/usr/local/lib/fs2xplane/linux
mkdir -p $RPMRT/usr/local/lib/fs2xplane/win32
cp linux/fs2xplane.desktop $RPMRT/usr/local/lib/fs2xplane/
cp -p linux/fs2xplane.spec $RPM/SPECS/
cp -p linux/fs2xp $RPMRT/usr/local/bin/
cp -p linux/fs2xplane $RPMRT/usr/local/bin/
for i in $PY $DATA; do cp -p "$i" $RPMRT/usr/local/lib/fs2xplane/; done
for i in $RSRC; do cp -p "$i" $RPMRT/usr/local/lib/fs2xplane/Resources/; done
for i in linux/bglunzip linux/bglxml linux/bmp2dds linux/bmp2png linux/DSFTool linux/fake2004 linux/winever; do cp -p "$i" $RPMRT/usr/local/lib/fs2xplane/linux/; done
for i in win32/bglunzip.exe win32/fake2004.exe; do cp -p "$i" $RPMRT/usr/local/lib/fs2xplane/win32/; done
rpmbuild -bb --buildroot $RPMRT --define "_topdir $RPM" --define "_unpackaged_files_terminate_build 0" --define "version $VERSION" --define "release $RELEASE" --quiet $RPM/SPECS/fs2xplane.spec
mv $RPM/RPMS/noarch/fs2xplane-$VERSION-$RELEASE.noarch.rpm .

# Debian/Ubuntu
mkdir -p $RPMRT/DEBIAN
mkdir -p $RPMRT/usr/local/share/applications
mkdir -p $RPMRT/usr/local/share/icons/hicolor/48x48/apps
cp -p linux/fs2xplane.desktop $RPMRT/usr/local/share/applications/
cp -p Resources/FS2XPlane.png $RPMRT/usr/local/share/icons/hicolor/48x48/apps/fs2xplane.png
echo Version: $VERSION-$RELEASE> $RPMRT/DEBIAN/control
cat   linux/control >> $RPMRT/DEBIAN/control
cp -p linux/postinst $RPMRT/DEBIAN/
sudo chown -R 0:0 $RPMRT/*
dpkg-deb -b $RPMRT .	# requires gnu-tar
sudo chown -R $USER:staff $RPMRT/*

# mac
mkdir -p FS2XPlane.app/Contents/MacOS
cp -p MacOS/* FS2XPlane.app/Contents/MacOS/
rm -f FS2XPlane.app/Contents/MacOS/Info.plist
for i in $PY; do cp -p "$i" FS2XPlane.app/Contents/MacOS/; done
mkdir -p FS2XPlane.app/Contents/MacOS/win32
for i in win32/bglunzip.exe win32/fake2004.exe; do cp -i "$i" FS2XPlane.app/Contents/MacOS/win32/; done
mkdir -p FS2XPlane.app/Contents/Resources
for i in $DATA; do cp -p "$i" FS2XPlane.app/Contents/; done
for i in $RSRC; do cp -p "$i" FS2XPlane.app/Contents/Resources/; done
sed s/appversion/$VERSION/ <MacOS/Info.plist >FS2XPlane.app/Contents/Info.plist
mv FS2XPlane.app/Contents/MacOS/FS2XPlane.icns FS2XPlane.app/Contents/Resources/
mv -f FS2XPlane.app/Contents/MacOS/FS2XPlane.png FS2XPlane.app/Contents/Resources/	# overwrite with higher res
zip -r FS2XPlane_${VER}_mac.zip FS2XPlane.app