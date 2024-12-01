import boto3

def insert_performance_data(performances):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('MusicFestivalLineup')
    with table.batch_writer() as writer:
        for performance in performances:
            writer.put_item(Item=performance)