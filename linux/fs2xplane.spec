Summary: MSFS add-on scenery converter for X-Plane
Name: fs2xplane
License: Creative Commons Attribution-ShareAlike 2.5
Group: Amusements/Games
URL: http://marginal.org.uk/x-planescenery
Icon: fs2xplane.xpm
Vendor: Jonathan Harris <x-plane@marginal.org.uk>
Prefix: /usr/local
Requires: bash, python >= 2.4, wxPython >= 2.6, python-opengl >= 2.0, python-opengl < 3, wine

%description
This application converts MS Flight Simulator 2004 add-on scenery packages to X-Plane DSF overlay scenery packages for X-Plane 8.60 or later.

%files
%defattr(644,root,root,755)
%attr(755,root,root) /usr/local/bin/fs2xp
%attr(755,root,root) /usr/local/bin/fs2xplane
/usr/local/lib/fs2xplane
%doc /usr/local/lib/fs2xplane/FS2XPlane.html
%attr(755,root,root) /usr/local/lib/fs2xplane/linux/bglunzip
%attr(755,root,root) /usr/local/lib/fs2xplane/win32/bglunzip.exe
%attr(755,root,root) /usr/local/lib/fs2xplane/linux/bglxml
%attr(755,root,root) /usr/local/lib/fs2xplane/linux/bmp2png
%attr(755,root,root) /usr/local/lib/fs2xplane/linux/fake2004
%attr(755,root,root) /usr/local/lib/fs2xplane/win32/fake2004.exe
%attr(755,root,root) /usr/local/lib/fs2xplane/linux/DSFTool
%attr(755,root,root) /usr/local/lib/fs2xplane/win32/DSFTool.exe
# doesn't always look in /usr/local/share/applications
#/usr/share/applications/fs2xplane.desktop
#/usr/share/icons/hicolor/48x48/apps/fs2xplane.png


%post
# see http://standards.freedesktop.org/basedir-spec/latest/ar01s03.html
DESKDIR=`echo $XDG_DATA_DIRS|sed -e s/:.*//`
if [ ! "$DESKDIR" ]; then
    if [ -d /usr/local/share/applications ]; then
        DESKDIR=/usr/local/share;
    elif [ -d /usr/share/applications ]; then
        DESKDIR=/usr/share;
    elif [ -d /opt/kde3/share/applications ]; then
        DESKDIR=/opt/kde3/share;
    else
        DESKDIR=$RPM_INSTALL_PREFIX/share;
    fi;
fi
mkdir -p "$DESKDIR/applications"
cp -f "$RPM_INSTALL_PREFIX/lib/fs2xplane/fs2xplane.desktop" "$DESKDIR/applications/fs2xplane.desktop"

# KDE<3.5.5 ignores XDG_DATA_DIRS - http://bugs.kde.org/show_bug.cgi?id=97776
if [ -d /opt/kde3/share/icons/hicolor ]; then
    ICONDIR=/opt/kde3/share/icons/hicolor;	# suse
else
    ICONDIR=$DESKDIR/icons/hicolor;
fi
mkdir -p "$ICONDIR/48x48/apps"
cp -f "$RPM_INSTALL_PREFIX/lib/fs2xplane/Resources/FS2XPlane.png" "$ICONDIR/48x48/apps/fs2xplane.png"
gtk-update-icon-cache -f -q -t $ICONDIR &>/dev/null
exit 0	# ignore errors from updating icon cache


%postun
DESKDIR=`echo $XDG_DATA_DIRS|sed -e s/:.*//`
rm -f "$DESKDIR/applications/fs2xplane.desktop"
rm -f /usr/local/share/applications/fs2xplane.desktop
rm -f /usr/share/applications/fs2xplane.desktop
rm -f /usr/share/applications/fs2xplane.desktop
rm -f /usr/local/share/icons/hicolor/48x48/apps/fs2xplane.png
rm -f /usr/share/icons/hicolor/48x48/apps/fs2xplane.png
rm -f /opt/kde3/share/icons/hicolor/48x48/apps/fs2xplane.png
exit 0	# ignore errors from updating icon cache
