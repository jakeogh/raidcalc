#!/usr/bin/env python3

import shutil
import pprint
from functools import update_wrapper
import click
try:
    from cytoolz.itertoolz import partition
except ModuleNotFoundError:
    from cytoolz.itertoolz import partition


PP = pprint.PrettyPrinter(indent=4)

CONTEXT_SETTINGS = \
    dict(help_option_names=['--help'],
         terminal_width=shutil.get_terminal_size((80, 20)).columns)


@click.group(chain=True)
@click.pass_context
def cli(ctx):
    pass

@cli.resultcallback()
def process_commands(processors):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    From: https://github.com/pallets/click/blob/master/examples/imagepipe/imagepipe.py
    """
    # Start with an empty iterable.
    stream = ()

    # Pipe it through all stream processors.
    for processor in processors:
        stream = processor(stream)

    # Evaluate the stream and throw away the items.
    for _ in stream:
        pass


def processor(f):
    """Helper decorator to rewrite a function so that it returns another function from it.
    From: https://github.com/pallets/click/blob/master/examples/imagepipe/imagepipe.py
    """
    def new_func(*args, **kwargs):
        def processor(stream):
            return f(stream, *args, **kwargs)
        return processor
    return update_wrapper(new_func, f)


def generator(f):
    """Similar to the :func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    From: https://github.com/pallets/click/blob/master/examples/imagepipe/imagepipe.py
    """
    @processor
    def new_func(stream, *args, **kwargs):
        for item in stream:
            yield item
        for item in f(*args, **kwargs):
            yield item
    return update_wrapper(new_func, f)


@cli.command('define')
@click.argument('device-size-TB', required=True, nargs=1, type=int)
@click.argument('device-count', required=True, nargs=1, type=int)
@generator
def define(device_size_tb, device_count):
    return [device_size_tb] * device_count


@cli.command('group')
@click.argument("number_of_groups", nargs=1, required=True, type=int)
@processor
def group(results, number_of_groups):
    return list(partition(number_of_groups, results))


@cli.command('show')
@processor
def show(results):
    PP.pprint(results)
