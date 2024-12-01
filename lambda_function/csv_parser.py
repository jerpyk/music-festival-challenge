import csv
from io import StringIO


def parse_csv(file_content):

    performances = []
    csv_reader = csv.reader(StringIO(file_content))
    next(csv_reader)  # Skip header row

    for row in csv_reader:
        if len(row) != 5:
            continue  # Skip invalid rows
        performer, stage, start, end, date = row
        performances.append({
            'Performer': performer,
            'Stage': stage,
            'Start': start.zfill(5),
            'End': end.zfill(5),
            'Date': date,
            'Date#Start': date + '#' + start.zfill(5)
        })

    return performances

def validate_performance(performance):
    # Placeholder for any validation logic if needed
    return True

def format_for_dynamodb(performances):
    formatted_data = []
    for performance in performances:
        if validate_performance(performance):
            formatted_data.append({
                'PK': f"PERFORMER#{performance['performer']}",
                'SK': f"STAGE#{performance['stage']}#DATE#{performance['date']}",
                'start': performance['start'],
                'end': performance['end']
            })
    return formatted_data