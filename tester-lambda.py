#!/usr/bin/env python3

# Generate an error message for testing LogMailer

def lambda_handler(event, context):
    print('Test Lambda called.')
    print('Event: {}'.format(event))
    print('ERROR: LogMailer Tester')

if __name__ == '__main__':
    lambda_handler({},{})
