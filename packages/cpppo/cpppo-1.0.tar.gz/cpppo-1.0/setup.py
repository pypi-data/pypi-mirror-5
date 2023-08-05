from distutils.core import setup

from misc import __version__

setup(
    name = "cpppo",
    version = __version__,
    requires = ['greenery', 'web'],
    packages = ['', 'server', 'server/enip'],
    package_dir = {'': '.'},
    extra_path = 'cpppo',
    author = "Perry Kundert",
    author_email = "perry@hardconsulting.com",
    description = "Cpppo is a Communication Protocol Python Parser and Originator",
    long_description = """\
Cpppo is used to create event-driven state machines which consume a stream
of input and generate a series of state changes, or an indication that no
progress is possible due to (for example) exhaustion of input symbols.

This is useful for creating parsers for complex grammars describing
languages, including binary computer protocols.

An example included with cpppo is an implementation of a subset of the
EtherNet/IP CIP language used by some industrial control equipment, such as
Rockwell's Logix Controllers.  The cpppo.server.enip package can be used to
create Python programs which can parse requests in this protocol (eg. as a
server, to implement something like a simulated Controller) or originate
requests in this protocol (eg. as a client, sending commands to a
Controller).""",
    license = "Dual License; GPLv3 and Proprietary",
    keywords = "cpppo protocol parser DFA",
    url = "https://github.com/pkundert/cpppo",
    classifiers = [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Text Processing :: Filters"
    ],
)
