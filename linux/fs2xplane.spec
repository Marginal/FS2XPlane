Summary: MSFS add-on scenery converter for X-Plane
Name: fs2xplane
Version: %{version}
Release: %{release}
License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0
Group: Amusements/Games
URL: http://marginal.org.uk/x-planescenery
Vendor: Jonathan Harris <x-plane@marginal.org.uk>
Prefix: /usr/local
Requires: bash, python >= 2.4, wxPython >= 2.6, python-opengl >= 3.0.1, wine
BuildArch: noarch

%description
This application converts MS Flight Simulator 2004 and FSX add-on scenery packages to X-Plane DSF overlay scenery packages for X-Plane 8.64 or later.

%files
%defattr(-,root,root,-)
%attr(755,root,root) /usr/local/bin/fs2xp
%attr(755,root,root) /usr/local/bin/fs2xplane
/usr/local/lib/fs2xplane
%doc /usr/local/lib/fs2xplane/FS2XPlane.html

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
