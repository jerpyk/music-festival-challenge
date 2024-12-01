import boto3
from csv_parser import parse_csv
from dynamodb_schema import insert_performance_data
from sns_notification import send_sns_notification

s3Client = boto3.client('s3')


def lambda_handler(event, context):
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    try:
        # Fetch the CSV file from S3
        response = s3Client.get_object(Bucket=bucket_name, Key=object_key)
        data = response['Body'].read().decode('utf-8')
        
        # Parse the CSV content
        performances = parse_csv(data)

        # Insert data into DynamoDB
        insert_performance_data(performances)
        
        # Send success notification
        send_sns_notification("CSV processing succeeded", f"Successfully processed {len(performances)} performances from {object_key}.")
        
    except Exception as e:
        # Send failure notification
        send_sns_notification("CSV processing failed", str(e))
        raise(e)
