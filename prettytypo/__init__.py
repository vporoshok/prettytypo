#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Typograph for LaTeX.
'''

import logging

import click

from prettytypo.states import STATES
from prettytypo.state_stack import StateStack

logging.basicConfig(level=logging.ERROR)


@click.command()
@click.argument('source', type=click.File('r', encoding='utf-8'),
                default='-')
def main(source):
    stack = StateStack()
    for state in STATES:
        stack.register(state)

    stack.push('root')
    for char in source.read():
        stack(char)

    click.echo(stack.current.result)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
