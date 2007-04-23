#!/usr/bin/python

from convutil import appname, appversion
from distutils.core import setup
from os import listdir, name
from sys import platform


# bogus crud to get WinXP "Visual Styles"
manifest=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'+
          '<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">\n'+
          '<assemblyIdentity\n'+
          '    version="%4.2f.0.0"\n' % appversion +
          '    processorArchitecture="X86"\n'+
          '    name="%s"\n' % appname +
          '    type="win32"\n'+
          '/>\n'+
          '<description>Convert FS2004 sceneries to X-Plane.</description>\n'+
          '<dependency>\n'+
          '    <dependentAssembly>\n'+
          '        <assemblyIdentity\n'+
          '            type="win32"\n'+
          '            name="Microsoft.Windows.Common-Controls"\n'+
          '            version="6.0.0.0"\n'+
          '            processorArchitecture="X86"\n'+
          '            publicKeyToken="6595b64144ccf1df"\n'+
          '            language="*"\n'+
          '        />\n'+
          '    </dependentAssembly>\n'+
          '</dependency>\n'+
          '</assembly>\n')


if platform=='win32':
    # http://www.py2exe.org/  Invoke with: setup.py py2exe
    import py2exe
    platdata=[('win32',
               ['win32/bglxml.exe',
                'win32/bglunzip.exe',
                'win32/bmp2png.exe',
                'win32/DSFTool.exe',
                'win32/FS2XPlane.ico',
                ])
              ]

elif platform.lower().startswith('darwin'):
    # http://undefined.org/python/py2app.html  Invoke with: setup.py py2app
    import py2app
    platdata=[('MacOS',
               ['MacOS/bglxml',
                'MacOS/bmp2png',
                #'MacOS/FS2XPlane.icns',
                ]),
              # Include wxPython 2.4
              #('../Frameworks',
              # ['/usr/local/lib/libwx_mac-2.4.0.rsrc',
              #  ]),
              ]

res=["Resources/library objects.txt"]
for f in listdir('Resources'):
    if f[-4:] in ['.bgl', '.obj', '.png']: res.append('Resources/%s' % f)
    
setup(name='FS2XPlane',
      version=("%4.2f" % appversion),
      description='Convert FS2004 sceneries to X-Plane',
      author='Jonathan Harris',
      author_email='x-plane@marginal.org.uk',
      url='http://marginal.org.uk/xplanescenery',
      data_files=[('',
                   ['FS2XPlane.html',
                    'bglxml.copying.txt',
                    ]),
                  ('Resources',
                   res),
                  ] + platdata,

      options = {'py2exe': {'ascii':True,
                            #'dll_excludes':['w9xpopen.exe'],
                            'bundle_files':True,
                            'compressed':True,
                            'excludes':['Carbon', 'tcl', 'Tkinter', 'mx', 'socket', 'urllib', 'webbrowser'],
                            'packages':['encodings.ascii','encodings.mbcs','encodings.latin_1','encodings.utf_8'],
                            'optimize':2,
                            },
                 'py2app': {'argv_emulation':False,
                            'iconfile':'MacOS/FS2XPlane.icns',
                            'compressed':True,
                            'optimize':2,
                            'semi_standalone':True,
                            },
                 },

      # win32
      console = ['fs2xp.py'],
      windows = [{'script':'FS2XPlane.py',
                  'icon_resources':[(1,'win32/FS2XPlane.ico')],
                  'other_resources':[(24,1,manifest)],
                  }],

      # mac
      #app = ['FS2XPlane.py'],
)
