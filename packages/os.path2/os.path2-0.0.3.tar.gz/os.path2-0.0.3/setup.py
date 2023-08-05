# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from setuptools.command.install_egg_info import install_egg_info

from distutils.sysconfig import get_python_lib

from path2 import path


pth_file = "os.path2.pth"

class Install(install):
    def run(self):
        install.run(self)


class InstallEggInfo(install_egg_info):
    def run(self):
        install_egg_info.run(self)

        filepath = '%s/installed-files.txt' % self.target
        with open(filepath, "w") as f:
            f.write("../%s\n" % pth_file)


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py', 'tests.py'])
        raise SystemExit(errno)


setup(name='os.path2',
      version="0.0.3",
      data_files = [
         (get_python_lib(), [pth_file]),
      ],
      packages=find_packages(),
      author='Sebastian Pawluś',
      author_email='sebastian.pawlus@gmail.com',
      url='https://github.com/xando/osome',
      description="The os.path module replacement, with simple API.",
      keywords="os path ",
      license=path("LICENSE").open("r").read(),
      long_description=path("README.rst").open("r").read(),
      include_package_data=True,
      zip_safe=False,
      platforms=['any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: PyPy'
      ],
      cmdclass = {
          'install': Install,
          'install_egg_info': InstallEggInfo,
          'test': PyTest,
      },
)
