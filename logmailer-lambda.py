#!/usr/bin/env python3

# By Michael Ludvig (https://aws.nz/)

# Lambda function that's triggered by CloudWatch Logs filter match
# and emails the log messages to the specified address.

# Configurable environment variables
# Required:
#   SNS_TOPIC_ARN
#
# Optional:
#   EMAIL_SUBJECT_PREFIX    (default: [LogMailer])
#   LOG_MINUTES             (default: 60)
#   WAIT_SECONDS            (default: 5)

import os
import time
import base64
import gzip
import json

from datetime import datetime

import boto3

# SNS topic where error messages will be sent
sns_topic_arn = os.environ['SNS_TOPIC_ARN']

# Email Subject prefix
email_subject_prefix = os.environ.get('EMAIL_SUBJECT_PREFIX', '[LogMailer] ')

# Number of minutes to fetch from log and email, default: 60 (= 1 hour)
get_log_minutes = os.environ.get('LOG_MINUTES', 60)

# Wait this number of seconds for further log messages to arrive
wait_seconds = os.environ.get('WAIT_SECONDS', 5)


logs_client = boto3.client('logs')
sns_client = boto3.client('sns')

def despatch_message(subject, text):
    # Publish error message to SNS
    ret = sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=text,
        Subject=subject,
    )
    print('SNS Message ID: {}'.format(ret['MessageId']), flush=True)

def format_event_timestamp(log_event, output_format='%Y-%m-%d %H:%M:%S'):
    dt = datetime.fromtimestamp(log_event['timestamp']/1000).strftime(output_format)
    return dt

def format_log_event(log_event):
    dt = format_event_timestamp(log_event)
    return '[{}] {}'.format(dt, log_event['message'])

def build_url(event_decoded):
    url = 'https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logEventViewer:group={logGroup};stream={logStream};start={eventTimestamp}'
    params = {
        'region': os.environ['AWS_REGION'],
        'logGroup': event_decoded['logGroup'],
        'logStream': event_decoded['logStream'],
        'eventTimestamp': format_event_timestamp(event_decoded['logEvents'][0], '%Y-%m-%dT%H:%M:%SZ')   # ISO format
    }
    return url.format(**params)

def lambda_handler(event, context):
    email_text = []
    email_subject = email_subject_prefix

    # Decode / unzip / parse event
    event_decoded = json.loads(gzip.decompress(base64.b64decode(event['awslogs']['data'])))
    print(event_decoded, flush=True)
    email_subject += '{}: {}'.format(event_decoded['logGroup'], event_decoded['logEvents'][0]['message'])

    email_text.append('Log Group:  {}'.format(event_decoded['logGroup']))
    email_text.append('Log Stream: {}'.format(event_decoded['logStream']))
    email_text.append('')
    for log_event in event_decoded['logEvents']:
        email_text.append(format_log_event(log_event))
    email_text.append('')
    email_text.append('-------')
    email_text.append('')
    email_text.append('Previous CloudWatch Logs messages:')
    email_text.append('')

    # Timestamp in milliseconds from the epoch
    current_timestamp = int(datetime.timestamp(datetime.now())*1000)
    start_timestamp = current_timestamp - get_log_minutes * 60 * 1000

    # Wait a few seconds for more messages to arrive
    time.sleep(wait_seconds)

    # Get events
    log_events = logs_client.get_log_events(
        logGroupName=event_decoded['logGroup'],
        logStreamName=event_decoded['logStream'],
        startTime=start_timestamp,
        startFromHead=True
    )
    #print(log_events, flush=True)
    for le in log_events['events']:
        email_text.append(format_log_event(le))

    # Delimiter for signature
    email_text.append('')
    email_text.append('{}'.format(build_url(event_decoded)))

    # Despatch the message to SNS
    despatch_message(subject=email_subject, text='\n'.join(email_text))
