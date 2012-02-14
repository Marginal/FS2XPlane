#!/usr/bin/python

from distutils.core import setup
from os import getcwd, listdir, name
from sys import platform
from glob import glob

import sys
sys.path.insert(0, getcwd())

from convutil import appname, appversion


# bogus crud to get WinXP "Visual Styles"
manifest=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'+
          '<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">\n'+
          '<assemblyIdentity\n'+
          '    version="%4.2f.0.0"\n' % appversion +
          '    processorArchitecture="X86"\n'+
          '    name="%s"\n' % appname +
          '    type="win32"\n'+
          '/>\n'+
          '<description>MSFS add-on scenery converter for X-Plane.</description>\n'+
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
          '<dependency>\n'+
          '    <dependentAssembly>\n'+
          '        <assemblyIdentity\n'+
          '            type="win32"\n'+
          '            name="Microsoft.VC90.CRT"\n'+
          '            version="9.0.30729.1"\n'+
          '            processorArchitecture="X86"\n'+
          '            publicKeyToken="1fc8b3b9a1e18e3b"\n'+
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
                'win32/bmp2dds.exe',
                'win32/bmp2png.exe',
                'win32/DSFTool.exe',
                ]),
              ('Microsoft.VC90.CRT',
               ['win32/Microsoft.VC90.CRT.manifest',
                'win32/msvcp90.dll',
                'win32/msvcr90.dll'
                ]),
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

res=["Resources/objects.txt",
     "Resources/opensceneryx_library.txt",
     "Resources/Rwy12.xml",
     "Resources/substitutions.txt"]
for f in listdir('Resources'):
    if f[-4:] in ['.bgl','.dds','.fac','.for','.lin','.obj','.png','.pol']: res.append('Resources/%s' % f)
    
setup(name='FS2XPlane',
      version=("%4.2f" % appversion),
      description='MSFS add-on scenery converter for X-Plane',
      author='Jonathan Harris',
      author_email='x-plane@marginal.org.uk',
      url='http://marginal.org.uk/xplanescenery',
      data_files=[('',
                   ['FS2XPlane.html',
                    'bglxml.copying.txt',
                    'Squish_license.txt',
                    ]),
                  ('Resources',
                   res),
                  ] + platdata,

      options = {'py2exe': {'ascii':True,
                            #'dll_excludes':['w9xpopen.exe'],
                            'bundle_files':True,
                            'compressed':True,
                            'includes':['OpenGL.platform.win32',
                                        'OpenGL.arrays',
                                        'OpenGL.arrays.ctypesarrays',
                                        'OpenGL.arrays.ctypesparameters',
                                        'OpenGL.arrays.ctypespointers',
                                        'OpenGL.arrays.lists',
                                        'OpenGL.arrays.nones',
                                        'OpenGL.arrays.numarrays',
                                        'OpenGL.arrays.numbers',
                                        'OpenGL.arrays.numeric',
                                        'OpenGL.arrays.numericnames',
                                        'OpenGL.arrays.numpymodule',
                                        #'OpenGL.arrays.strings',	# gives runtime error
                                        'OpenGL.arrays.vbo'],
                            'excludes':['Carbon', 'tcl', 'Tkinter', 'mx', 'socket', 'urllib', 'webbrowser'],
                            'packages':['encodings.ascii','encodings.mbcs','encodings.latin_1','encodings.utf_8','encodings.cp437'],
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
