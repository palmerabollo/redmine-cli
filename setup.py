from os.path import dirname, join
from setuptools import setup
from redmine_cli import CLI_VERSION

try:
    with open(join(dirname(__file__), 'README.md')) as f:
        README = f.read()
except IOError:
    README = ''


def get_requirements():
    reqs_file = 'requirements.txt'
    try:
        with open(reqs_file) as reqs_file:
            reqs = filter(None, map(lambda line: line.replace('\n', '').strip(), reqs_file))
            return reqs
    except IOError:
        pass
    return []


setup(
    name='pyRedmine',
    version=CLI_VERSION,
    packages=['redmine_cli'],
    entry_points={
        'console_scripts': [
            'red = redmine_cli.redmine:command',
        ]
    },
    install_requires=get_requirements(),
    license='(C) Telefonica I+D',  # example license
    description='CLI library to manage and operate all the entities of the service directory via HTTP',
    long_description=README,
    url='https://github.com/palmerabollo/redmine-cli',
    author='4pf team',
    author_email='guido.garciabernardo@telefonica.com, eduardo.alonsogarcia@telefonica.com',
    classifiers=[
        'Environment :: CLI',
        'Framework :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Commercial',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.x',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)
