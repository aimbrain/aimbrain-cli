# aimbrain-cli

aimbrain-cli is a simple to use Command Line Interface that allows you to
perform common day to day tasks quickly and easily.


## Getting Started

In order to install the CLI locally (on Linux), just clone the repo and do:

```
sudo pip install --prefix /usr/local .
```

However, if you wish to do some dev work on it, run the following for a better
dev experience:

```
virtualenv /path/to/envs/aimbrain-cli
source /path/to/envs/aimbrain-cli/bin/activate
pip install --editable .
```

Instrucutions on how to use can be found by running:

```
aimbrain-cli --help
```

And see Python DocOpt docs for details on how to add new commands etc:

https://github.com/docopt/docopt
