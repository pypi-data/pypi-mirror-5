pytest plugin to all passing the path to a paste config file

Usage
-----

install/update via::

    pip install -U pytest-paste-config

and to run tests type::

    py.test


Rationale
=========

This plugin is written purely so that I can do:

    def test_connection(pytestconfig):
        engine = engine_from_config(pytestconfig.paste_file)
        models.Base.metadata.create_all(engine)
        # some test code...
        

and then run:

    py.test --paste-file testing.ini
