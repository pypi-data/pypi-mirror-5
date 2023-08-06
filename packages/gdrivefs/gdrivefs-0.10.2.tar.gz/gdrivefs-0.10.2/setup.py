#!/usr/bin/python

from setuptools import find_packages
from distutils import core
from distutils.command.install import install

from sys import exit
from os import symlink
from os.path import dirname

from gdrivefs import tools

def pre_install():

# TODO: Ensure FUSE.
    return True

def post_install():
    tool_path = dirname(tools.__file__)

    gdfs_filepath = ('%s/%s' % (tool_path, 'gdfs.py'))
    gdfs_symlink_filepath = '/usr/local/sbin/gdfs'

    gdfstool_filepath = ('%s/%s' % (tool_path, 'gdfstool.py'))
    gdfstool_symlink_filepath = '/usr/local/sbin/gdfstool'

    print("Writing gdfs symlink (%s -> %s)." % 
          (gdfs_symlink_filepath, gdfs_filepath))
    symlink(gdfs_filepath, gdfs_symlink_filepath)

    print("Writing gdfstool symlink (%s -> %s)." % 
          (gdfstool_symlink_filepath, gdfstool_filepath))
    symlink(gdfstool_filepath, gdfstool_symlink_filepath)

if not pre_install():
    exit(1)

class custom_install(install):
    def run(self):
        install.run(self)

        post_install()

version = '0.10.2'

core.setup(name='gdrivefs',
      version=version,
      description="A complete FUSE adapter for Google Drive.",
      long_description="""\
A complete FUSE adapter for Google Drive. See Github for more information.""",
      classifiers=['Topic :: System :: Filesystems',
                   'Development Status :: 2 - Pre-Alpha',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Topic :: Internet',
                   'Topic :: Utilities',
                  ],
      keywords='google-drive google drive fuse filesystem',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/GDriveFS',
      license='New BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'ez_setup',
        'google_appengine',
        'google_api_python_client',
        'httplib2',
#        'python-dateutil',
        'fusepy',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      cmdclass={'install': custom_install
               },
      )

