#!/usr/bin/env python3

# Simple script that dies in a random way :)
# Used for testing LogMailer

import sys
import random

def fail_exit1():
    print('Exitting with retval=1')
    sys.exit(1)

def fail_Exception():
    raise Exception('Something is broken')

def fail_KeyError():
    d = { 'a': 1 }
    return d['b']

def lambda_handler(event, context):
    failures = [
        fail_exit1,
        fail_Exception,
        fail_KeyError,
    ]

    print('Test Lambda called.')
    func = random.choice(failures)
    print('Calling {}()'.format(func.__name__))
    func()

if __name__ == '__main__':
    lambda_handler({},{})
