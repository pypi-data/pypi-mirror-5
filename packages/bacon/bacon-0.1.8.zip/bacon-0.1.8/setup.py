import distutils
from distutils.core import setup
import os

version = '0.1.8'

windows_dlls = [
    'bacon/Bacon.dll',
    'bacon/libEGL.dll',
    'bacon/libGLESv2.dll',
    'bacon/d3dcompiler_46.dll'
]

osx_dlls = [
    'bacon/Bacon.dylib'
]

if __name__ == '__main__':
    setup(name='bacon',
          description='Bacon Game Engine',
          long_description='Bacon Game Engine', # TODO
          license='MIT',
          classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Topic :: Games/Entertainment',
            'Topic :: Software Development :: Libraries :: Python Modules',
          ],

          version=version,
          author='Alex Holkner',
          author_email='alex.holkner@gmail.com',
          url='https://github.com/aholkner/bacon',
          packages=['bacon'],
          data_files=[
            (os.path.join(distutils.sysconfig.get_python_lib(), 'bacon'), windows_dlls + osx_dlls),
          ],
    )
