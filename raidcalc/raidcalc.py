#!/usr/bin/env python3

import sys
import math
from functools import update_wrapper
from shutil import get_terminal_size
import click
from colorama import Fore
from icecream import ic
#ic.configureOutput(includeContext=True)
#ic.lineWrapWidth, _ = get_terminal_size((80, 20))
ic.lineWrapWidth, _ = get_terminal_size()
#ic.disable()

try:
    from cytoolz.itertoolz import partition
except ModuleNotFoundError:
    from cytoolz.itertoolz import partition

VERBOSE = False


#https://stackoverflow.com/questions/171765/what-is-the-best-way-to-get-all-the-divisors-of-a-number
def divisors(n):
    divs = [1]
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.extend([i, int(n / i)])
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
@click.option("--verbose", is_flag=True)
@generator
def define(device_size_tb, device_count, verbose):
    if verbose:
        global VERBOSE
        VERBOSE = True
    if not device_count % 2 == 0:
        print(Fore.RED + "Warning: device_count is not even.", file=sys.stderr)
    result = [device_size_tb] * device_count
    for define in [result]:
        ic(define)
        yield define


def group(togroup, group_size):
    dev_count = len(togroup)
    if group_size == "all":
        group_size = dev_count
    else:
        group_size = int(group_size)
    if not dev_count % group_size == 0 or group_size > dev_count:
        msg = "Possible group sizes for {} devices are: {}".format(dev_count, divisors(dev_count)[:-1])
        raise ValueError(msg)
    grouped = list(partition(group_size, togroup))
    return grouped


def raid(toraid, group_size, level):
    dev_count = len(toraid)
    grouped = group(toraid, group_size)
    global VERBOSE
    if VERBOSE:
        ic(grouped)
    if level == "mirror":
        if dev_count < 2:
            raise ValueError("Error: mirror requires >= 2 devices")
        raided = [group[0] for group in grouped]
    elif level == "stripe":
        raided = [sum(group) for group in grouped]
    elif level == "z1":
        if dev_count < 3:
            raise ValueError("Error: z1 requires >= 3 devices")
        raided = [sum(group[:-1]) for group in grouped]
    elif level == "z2":
        if dev_count < 4:
            raise ValueError("Error: z2 requires >= 4 devices")
        raided = [sum(group[:-2]) for group in grouped]
    elif level == "z3":
        if dev_count < 5:
            raise ValueError("Error: z3 requires >= 5 devices")
        raided = [sum(group[:-3]) for group in grouped]
    else:
        raise NotImplementedError("Error: unknown RAID level:", level)
    return raided


@cli.command('mirror')
@click.argument("group_size", nargs=1, required=True)
@processor
def mirror(results, group_size):
    for result in results:
        try:
            mirrored = raid(toraid=result, group_size=group_size, level="mirror")
        except ValueError as e:
            print(Fore.RED + str(e))
            quit(1)
        ic(mirrored)
        yield mirrored


@cli.command('stripe')
@click.argument("group_size", nargs=1, required=True)
@processor
def stripe(results, group_size):
    for result in results:
        try:
            striped = raid(toraid=result, group_size=group_size, level="stripe")
        except ValueError as e:
            print(Fore.RED + str(e))
            quit(1)
        ic(striped)
        yield striped


@cli.command('z1')
@click.argument("group_size", nargs=1, required=True)
@processor
def z1(results, group_size):
    for result in results:
        try:
            raidz1 = raid(toraid=result, group_size=group_size, level="z1")
        except ValueError as e:
            print(Fore.RED + str(e))
            quit(1)
        ic(raidz1)
        yield raidz1


@cli.command('z2')
@click.argument("group_size", nargs=1, required=True)
@processor
def z2(results, group_size):
    for result in results:
        try:
            raidz2 = raid(toraid=result, group_size=group_size, level="z2")
        except ValueError as e:
            print(Fore.RED + str(e))
            quit(1)
        ic(raidz2)
        yield raidz2


@cli.command('z3')
@click.argument("group_size", nargs=1, required=True)
@processor
def z3(results, group_size):
    for result in results:
        try:
            raidz3 = raid(toraid=result, group_size=group_size, level="z3")
        except ValueError as e:
            print(Fore.RED + str(e))
            quit(1)
        ic(raidz3)
        yield raidz3


#@cli.command('show')
#@processor
#def show(results):
#    for shown in results:
#        #ic(result)
#        ic(shown)
#        yield shown
