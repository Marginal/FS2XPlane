Summary: MSFS add-on scenery converter for X-Plane
Name: fs2xplane
License: Creative Commons Attribution-ShareAlike 2.5
Group: Amusements/Games
URL: http://marginal.org.uk/x-planescenery
Icon: fs2xplane.xpm
Vendor: Jonathan Harris <x-plane@marginal.org.uk>
Prefix: /usr/local
Requires: bash, python >= 2.4, wxPython >= 2.6, python-opengl >= 2.0, wine

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
# see http://lists.freedesktop.org/archives/xdg/2006-February/007757.html
DESKDIR=`echo $XDG_DATA_DIRS|sed -e s/:.*//`
if [ ! "$DESKDIR" ]; then
    if [ -d /usr/local/share/applications ]; then
        DESKDIR=/usr/local/share;
    else
        DESKDIR=/usr/share;
    fi;
fi
mkdir -p "$DESKDIR/applications"
cp -f "$RPM_INSTALL_PREFIX/lib/fs2xplane/fs2xplane.desktop" "$DESKDIR/applications/fs2xplane.desktop"

if [ -d /opt/kde3/share/icons/hicolor ]; then
    ICONDIR=/opt/kde3/share/icons/hicolor;	# suse
else
    ICONDIR=/usr/share/icons/hicolor;
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

if [ -f /opt/kde3/share/icons/hicolor/48x48/apps/fs2xplane.png ]; then
    rm -f /opt/kde3/share/icons/hicolor/48x48/apps/fs2xplane.png
#    gtk-update-icon-cache -q -t /opt/kde3/share/icons/hicolor &>/dev/null;
fi
if [ -f /usr/share/icons/hicolor/48x48/apps/fs2xplane.png ]; then
    rm -f /usr/share/icons/hicolor/48x48/apps/fs2xplane.png
#    gtk-update-icon-cache -q -t /usr/share/icons/hicolor &>/dev/null;
fi
exit 0	# ignore errors from updating icon cache
