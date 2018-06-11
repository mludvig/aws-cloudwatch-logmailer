# CloudWatch LogMailer

The purpose of **LogMailer Lambda** is to email *CloudWatch Logs* to a specified 
Email address using *AWS SNS* (Simple Notification Service) 
when a *matching pattern* is encountered in one of the log streams.

Email recipients should subscribe as `email` (not `email-json`) to the SNS Topic.

## Templates

The [`logmailer-cloudformation.yml`](logmailer-cloudformation.yml) template creates:

* **LogMailer Lambda** function
* **SNS Topic** for notifications
* Lambda IAM Role with the required permissions

This stack *doesn't* create the *Subscription Filters*. These are to be created in the *consumer* templates. One such example consumer is [`tester-cloudformation.yml`](tester-cloudformation.yml). The tester stack creates:

* **Tester Lambda and Scheduler** - Lambda runs every 5 minutes and every time fails with an error
* **Tester Log Group** - that's what we are *watching for Errors*
* **Log Group *Subscription Filter*** - that's what actually triggers the LogMailer Lambda
* Some required IAM roles and Permissions

## Usage

*LogMailer Lambda* can be used from any other stack
by adding these two resources into their respective templates:

```yaml
Parameters:
  [...]

  LogMailerLambdaArn:
    Type: String
    Description: ARN of the LogMailer Lambda function

Resources:
  [...]

  LogMailerTriggerPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref LogMailerLambdaArn
      Action: lambda:InvokeFunction
      Principal: logs.amazonaws.com
      SourceArn: !GetAtt LogGroup.Arn

  LogMailerFilter:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      FilterPattern: "?ERROR ?Error ?error ?FAIL ?Fail ?fail ?FATAL ?Fatal ?fatal ?Traceback"
      LogGroupName: !Ref LogGroup
      DestinationArn: !Ref LogMailerLambdaArn
```

Update the `FilterPattern` as required for each stack.

## Author

Michael Ludvig @ https://aws.nz
