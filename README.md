# aimbrain-cli

aimbrain-cli is a simple to use Command Line Interface that allows you to test
AimBrain's API endpoints quickly and easily.

## Getting Started

In order to install the CLI locally (on Linux), just clone the repo and do:

```
virtualenv /path/to/envs/aimbrain-cli
source /path/to/envs/aimbrain-cli/bin/activate
pip install .
cp /path/to/envs/aimbrain-cli/bin/aimbrain-cli /usr/bin/aimbrain-cli
deactivate
```

However, if you wish to do some dev work on it, it is recomended to run the
following:

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
