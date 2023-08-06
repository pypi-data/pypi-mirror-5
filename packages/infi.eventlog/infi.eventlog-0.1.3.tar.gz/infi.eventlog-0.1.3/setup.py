
SETUP_INFO = dict(
    name = 'infi.eventlog',
    version = '0.1.3',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """Bindings to Windows Event Log""",
    long_description = """Bindings to Windows Event Log""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'Brownie', 'infi.exceptools', 'xmltodict', 'infi.cwrap', 'infi.pyutils', 'infi.wioctl', 'mock'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = []),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

