conflib
=========

Simplifies configuration stacking. Primarily, this was written to allow stacking of default, global, and local settings for subpub. It allows for validation so that you can enforce contraints on supplied options.

## Usage

    import conflib

    Default = {'hello': 'world', 'alpha': 5}
    Global = {'wat': 'wut', 'fancy': (20, 'fish')}
    Local = {'hello': 'everybody', 'beta': 'qwerty'}

    Validator = {
        'alpha': lambda x: x < 10,
        'fancy': tuple,
        'beta': [('asdf', 'qwerty'), ('fizz','buzz')]
    }

    my_config = conflib.Config(Default, Global, Local, validation_dict=Validator)
    print(my_config.options)

## Installation

    pip install conflib

## License

conflib is released under the MIT License. See the bundled LICENSE file for details.

