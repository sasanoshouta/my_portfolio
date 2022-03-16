import json
import requests
import boto3
from boto3.dynamodb.conditions import Key
import decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('hogehoge')
store_id_table = dynamodb.Table('hogehoge')

def lambda_handler(event, context):
    POSTCODE = ''
    STORE_ID = ''
    for record in event['Records']:	# Record要素分Loop
        print(record['eventID'])	# eventIDを表示
        print(record['eventName'])	# DynamoDBの操作種別を表示
        if record['eventName'] == 'INSERT':	# 操作種別が”追加”か、判定
            newimage = record['dynamodb']['NewImage']	# 追加レコード情報を抽出
            print(newimage)
            USAGE = newimage['usage']['S']
            if USAGE == 'info':
                POSTCODE = newimage['postcode']['S']
            
            if USAGE == 'web':
                STORE_ID = newimage['id']['S']
                print(STORE_ID)
            # 追加レコード内の緯度経度情報がない場合に郵便番号から検索してDBに(dev-digivege-store-table)
                if (newimage['lat']['N'] == '0') and (newimage['long']['N'] == '0'):
                    res_dict_x, res_dict_y = HeartRails_Geo_API(POSTCODE)
                    print(res_dict_x, res_dict_y)
                    # この段階ではDBにレコード登録が出来ていないので、update_itemではなくput_itemが正解
                    # option = {'Key': {'store_id': STORE_ID, 'usage': 'web'},
                    #   'UpdateExpression': 'set #long = :long, #lat = :lat',
                    #   'ExpressionAttributeNames':{'#long': 'long', '#lat': 'lat'},
                    #   'ExpressionAttributeValues': {':long': decimal.Decimal(res_dict_x), ':lat': decimal.Decimal(res_dict_y)}
                    #  }
                    # store_id_table.update_item(**option)
                    web_item = {
                        'id': STORE_ID,
                        'usage': 'web',
                        'lat': decimal.Decimal(res_dict_y),
                        'long': decimal.Decimal(res_dict_x),
                        'live_msg': newimage['live_msg']['S']
                        
                    }
                    store_id_table.put_item(Item=web_item)
                    print("FINISH UPSERT!")
                else:
                    pass
                
            else:
                pass
                
        elif record['eventName'] == 'MODIFY':	# 操作種別が”変更”か、判定
            olditem = record['dynamodb']['OldImage']	# 変更前レコード情報を抽出
            newitem = record['dynamodb']['NewImage']	# 変更後レコード情報を抽出
            print("olditem: " +  json.dumps(olditem))	# 変更前レコード情報を表示
            print("newitem: " +  json.dumps(newitem))	# 変更後レコード情報を表示
        elif record['eventName'] == 'REMOVE':	# 操作種別が”削除”か、判定
            deletedItem = record['dynamodb']['OldImage']	# 削除対象レコード情報を抽出
            print("deleteimage: " +  json.dumps(deletedItem))	# 削除対象レコード情報を表示
            
    return print("FINISH")
            
def HeartRails_Geo_API(postal: str):
    POSTAL = postal #調べたい郵便番号
    
    url = 'http://geoapi.heartrails.com/api/json?method=searchByPostal&postal='
    res_dict = requests.get(url+POSTAL).json()['response']['location'][0]
      
    return res_dict['x'], res_dict['y']