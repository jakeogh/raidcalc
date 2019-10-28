#!/usr/bin/env python3

import shutil
import pprint
import math
from functools import update_wrapper
from icecream import ic
import click
try:
    from cytoolz.itertoolz import partition
except ModuleNotFoundError:
    from cytoolz.itertoolz import partition


PP = pprint.PrettyPrinter(indent=4)

CONTEXT_SETTINGS = \
    dict(help_option_names=['--help'],
         terminal_width=shutil.get_terminal_size((80, 20)).columns)


#https://stackoverflow.com/questions/171765/what-is-the-best-way-to-get-all-the-divisors-of-a-number
def divisors(n):
    divs = [1]
    for i in range(2,int(math.sqrt(n))+1):
        if n%i == 0:
            divs.extend([i,int(n/i)])
    divs.extend([n])
    return list(set(divs))


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
    if not device_count % 2 == 0:
        raise ValueError("device_count must be even")
    result = [device_size_tb] * device_count
    for define in [result]:
        ic(define)
        yield define


#@cli.command('group')
#@click.argument("group_size", nargs=1, required=True, type=int)
#@processor
def group(togroup, group_size):
    #ic(togroup)
    dev_count = len(togroup)
    if not dev_count % group_size == 0 or group_size > dev_count:
        msg = "Possible group sizes for {} devices are: {}".format(dev_count, divisors(dev_count)[:-1])
        raise ValueError(msg)
    grouped = list(partition(group_size, togroup))
    #ic(grouped)
    return grouped


def raid(toraid, group_size, level):
    groups = group(toraid, group_size)
    ic(groups)
    if level == "mirror":
        raided = [group[0] for group in groups]
    elif level == "stripe":
        raided = [sum(group) for group in groups]
    else:
        raise ValueError("unknown RAID level:", level)
    #ic(raided)
    return raided


@cli.command('mirror')
@click.argument("group_size", nargs=1, required=True, type=int)
@processor
def mirror(results, group_size):
    for result in results:
        mirrored = raid(toraid=result, group_size=group_size, level="mirror")
        ic(mirrored)
        yield mirrored


@cli.command('stripe')
@click.argument("group_size", nargs=1, required=True, type=int)
@processor
def stripe(results, group_size):
    for result in results:
        striped = raid(toraid=result, group_size=group_size, level="stripe")
        ic(striped)
        yield striped
        ##ic(result)
        #striped = [sum(group) for group in result]
        #ic(striped)
        #yield striped


@cli.command('z1')
@processor
def z1(results):
    for result in results:
        #ic(result)
        raidz1 = [sum(group[:-1]) for group in result]
        ic(raidz1)
        yield raidz1


@cli.command('z2')
@processor
def z2(results):
    for result in results:
        #ic(result)
        raidz2 = tuple([sum(group[:-2]) for group in result])
        ic(raidz2)
        yield raidz2


@cli.command('z3')
@processor
def z3(results):
    for result in results:
        #ic(result)
        raidz3 = [sum(group[:-2]) for group in result]
        ic(raidz3)
        yield raidz3


@cli.command('show')
@processor
def show(results):
    for shown in results:
        #ic(result)
        ic(shown)
        yield shown
