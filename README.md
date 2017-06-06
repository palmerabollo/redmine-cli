# redmine-cli
A simple redmine client

## Installation

```bash
pip install red
```
If you get the warning InsecureRequestWarning while running the command, this is likely that you are running an old
python version that uses a deprecated ssl version.

You'd better upgrade to a newer python interpreter but if you can not, you can omit the warning with this command:

```bash
pip install 'requests[security]'
```

## Usage

```sh
export REDMINE_ENDPOINT=xxx
export REDMINE_API_KEY=xxx

./redmine --help

./redmine list --help
./redmine detail --help
./redmine close --help
```

## TODO

- pip install
- create issue
- docs
