import json
# 実行日の日時及び曜日情報を取得
from datetime import datetime as dt
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    # 店舗DB
    store_id_table = dynamodb.Table('hogehoge')
    # 休日管理DB
    holiday_table = dynamodb.Table('hogehoge')
    GSI_NAME = 'hogehoge'
    # 休日DB曜日変換対応表
    DAYS = {'Sunday': 'Su', 'Monday': 'Mo', 'Tuesday': 'Tu', 'Wednesday': 'We', 'Thursday': 'Th', 'Friday': 'Fr', 'Saturday': 'Sa'}
    
    # 実行日の日時取得
    TODAY = dt.today().strftime('%Y_%m_%d')
    # 実行日の曜日取得
    S_DOW = DAYS[dt.strptime(TODAY, '%Y_%m_%d').strftime('%A')]
    
    # 店舗DBから登録店舗の店舗IDを取得
    ready_response = store_id_table.query(IndexName=GSI_NAME, KeyConditionExpression=Key('status').eq('ready'))
    ready_store_id = [ready_response['Items'][i]['id'] for i in range(len(ready_response['Items']))]
    
    holiday_response = store_id_table.query(IndexName=GSI_NAME, KeyConditionExpression=Key('status').eq('holiday'))
    holiday_store_id = [holiday_response['Items'][i]['id'] for i in range(len(holiday_response['Items']))]
    
    # 休日店舗DBからTODAYの日時を休日にしている店舗の取得
    today_is_holiday = holiday_table.get_item(Key={'day': S_DOW})['Item']['stores']
    
    for store in ready_store_id:
        if store in today_is_holiday:
            # 店舗DBのstatus情報をholidayに変更する処理
            option = {'Key': {'id': store,'usage': 'status'},
                      'UpdateExpression': 'set #status = :new_status',
                      'ExpressionAttributeNames':{'#status': 'status'},
                      'ExpressionAttributeValues': {':new_status': 'holiday'}
                     }
            store_id_table.update_item(**option)
        else:
            pass
        
    for store in holiday_store_id:
        if store in today_is_holiday:
            pass
        else:
            # 店舗DBのstatus情報をreadyに変更する処理
            option = {'Key': {'id': store,'usage': 'status'},
                      'UpdateExpression': 'set #status = :new_status',
                      'ExpressionAttributeNames':{'#status': 'status'},
                      'ExpressionAttributeValues': {':new_status': 'holiday'}
                     }
            store_id_table.update_item(**option)