from setuptools import setup, find_packages, Command

files = ["paegan/*"]
readme = open('README.md', 'rb').read()

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(namespace_packages = ['paegan'],
    name                = "paegan-transport",
    version             = "0.1.0",
    description         = "Particle transport packages for the Paegan library",
    long_description    = readme,
    license             = 'LICENSE.txt',
    author              = "Kyle Wilcox",
    author_email        = "kwilcox@sasascience.com",
    url                 = "https://github.com/asascience-open/paegan-transport",
    packages            = find_packages(),
    cmdclass            = {'test': PyTest},
    install_requires    = [
                            "GDAL == 1.9.1",
                            "Fiona == 0.8",
                            "paegan >= 0.9.3"
                          ],
    classifiers         = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
        ],
    include_package_data = True,
) 
