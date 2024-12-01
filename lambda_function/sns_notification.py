import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-1:739275441861:MusicFestivalSuccessNotifications'
    
    response = sns_client.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message
    )