.. _aiotraversal.cmd:

======================
Command-line interface
======================

Module ``aiotraversal.cmd`` makes if easy to write command-line interfaces for you application.

Parser
======

After ``config.include('aiotraversal.cmd')``, you can use these objects:

* ``config['cmd']['parser']``: :ref:`ArgumentParser` instance;
* ``config['cmd']['subparsers']``: subparsers for create commands, the main tool for extend console application;

After configure process finished:

* ``app['cmd']['args']``: ``Namespace`` instance from ``config['cmd']['parser'].parse_args()``;
* ``app['cmd']['run_func']``: function for :ref:`run`;


Add commands
------------

Something like this:

.. code:: python

    import asyncio

    from aiotraversal import Application
    from aiotraversal.cmd import run

    def cmd_func(app, loop):
        print('cmd_func is called!')


    def main():
        loop = asyncio.get_event_loop()
        app = Application()

        with app.configure(loop=loop) as config:
            config.include('aiotraversal.cmd')  # include

            subparsers = config['cmd']['subparsers']
            parser_test = subparsers.add_parser('test_command', help="Test")  # create subparser
            parser_test.set_defaults(func=cmd_func)  # add function for start
            # ... extend subpaser with `parser_test.add_argument`

        run(app, loop)  # in this place cmd_func is called

Now, if run your application with argument ``test_command`` (e.g. ``my_cmd test_command``),
"cmd_func is called!" printed.

Default key ``func`` of subparser, is magic for bind functions to commands.
It is called from the :ref:`run` with two arguments: ``app`` and ``loop``.


.. _argumentparser:

ArgumentParser
--------------

``ArgumentParser`` is modified for grouping subcommand arguments.

`StackOverflow <https://stackoverflow.com/questions/15782948/how-to-have-sub-parser-arguments-in-separate-namespace-with-argparse/15786238#15786238>`_
with this solution.


.. _run:

Function ``run``
================

After configure process, you must run ``aiotraversal.cmd.run``.
It run ``app['cmd']['run_func']``, finish application and close loop.
