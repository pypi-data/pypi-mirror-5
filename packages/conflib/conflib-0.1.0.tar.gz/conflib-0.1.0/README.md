conflib - Configuration hierarchies made --easy-- easier
=====

Overview
-----

This module is designed to simplify the management of configurations. Primarily, this was written to allow easy ststacking of default, global, and local settings. It also handles validation of settings so you can confirm that user input looks like it's supposed to.

How to use
-----

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

