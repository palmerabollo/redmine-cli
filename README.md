# redmine-cli
A simple redmine client

## Installation

The project is available at Pypy and you can simply install in the usually way:

```bash
pip install pyRedmineClient
```

## Usage

```sh
export REDMINE_ENDPOINT=xxx
export REDMINE_API_KEY=xxx

red --help

red list --help
red detail --help
red close --help
```

## Development


You can install the last version in github in this way:

```bash
python setup.py install
```

If you get the warning InsecureRequestWarning while running the command, this is likely that you are running an old
python version that uses a deprecated ssl version.

You'd better upgrade to a newer python interpreter but if you can not, you can omit the warning with this command:

```bash
pip install 'requests[security]'
```

## TODO

- [ ] create issue
- [ ] docs
