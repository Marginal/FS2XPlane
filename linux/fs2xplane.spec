Summary: MSFS add-on scenery converter for X-Plane
Name: fs2xplane
Version: %{version}
Release: %{release}
License: GPLv2
Group: Amusements/Games
URL: http://marginal.org.uk/x-planescenery
Vendor: Jonathan Harris <x-plane@marginal.org.uk>
Prefix: /usr/local
Requires: bash, numpy, python >= 2.4, wxPython >= 2.6, python-opengl >= 3.0.1, wine
BuildArch: noarch

%description
This application converts MS Flight Simulator 2004 and FSX add-on scenery packages to X-Plane DSF overlay scenery packages for X-Plane 8.64 or later.

%files
%defattr(644,root,root,755)
%attr(755,root,root) /usr/local/bin/fs2xp
%attr(755,root,root) /usr/local/bin/fs2xplane
/usr/local/share/applications/fs2xplane.desktop
/usr/local/share/icons/hicolor/48x48/apps/fs2xplane.png
/usr/local/share/icons/hicolor/128x128/apps/fs2xplane.png
/usr/local/lib/fs2xplane/*.py
/usr/local/lib/fs2xplane/Resources
%attr(755,root,root) /usr/local/lib/fs2xplane/linux
%attr(755,root,root) /usr/local/lib/fs2xplane/win32


%post
gtk-update-icon-cache -f -q -t $ICONDIR &>/dev/null
exit 0	# ignore errors from updating icon cache
