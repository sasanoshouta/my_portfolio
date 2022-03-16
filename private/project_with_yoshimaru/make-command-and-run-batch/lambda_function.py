import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime as dt

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('hogehoge')
GSI_NAME = 'hogehoge'

# 各関数実行
def lambda_handler(event, context):
    ready_storeid, no_mail_storeid = get_store_id(GSI_NAME)
    ready_response, no_mail_response = get_status(ready_storeid, no_mail_storeid)
    make_command_and_run_job(ready_response, no_mail_response)
    print('run')

# statusの取りうる値：ready, no_mail, not_ready
# グローバルセカンダリーインデックスからidを抜き取るクエリ
def get_store_id(gsi_name: str):
    ready_store_id = list()
    no_mail_store_id = list()
    # status:ready時の店舗ID取得
    try:
        ready_response = table.query(IndexName=gsi_name, KeyConditionExpression=Key('status').eq('ready'))
        ready_store_id = [ready_response['Items'][i]['id'] for i in range(len(ready_response['Items']))]
    except "Can't get ready_store_ID":
        print('ready_store_id is none')
        
    # status:no_mailの時の店舗ID取得
    try:
        no_mail_response = table.query(IndexName=gsi_name, KeyConditionExpression=Key('status').eq('no_mail'))
        no_mail_store_id = [no_mail_response['Items'][i]['id'] for i in range(len(no_mail_response['Items']))]
    except "Can't get ready_store_ID":
        print('no_mail_store_id is none')
    return ready_store_id, no_mail_store_id

# store_id毎に「推論yamlのconfig名」と「通知を実施するか否かの判別フラグ」と「センサーID一覧」を取得する関数
def get_status(ready_store_id: list, no_mail_store_id: list):
    ready_response = dict()
    no_mail_response = dict()
    for store in ready_store_id:
        ready_response[store] = {'detection': table.get_item(Key={'id': store, 'usage': 'detection'})['Item'], \
                           'sensors': table.get_item(Key={'id': store, 'usage': 'sensors'})['Item'],
                          'main': table.get_item(Key={'id': store, 'usage': 'main'})['Item']}
        
    for store in no_mail_store_id:
        no_mail_response[store] = {'detection': table.get_item(Key={'id': store, 'usage': 'detection'})['Item'], \
                           'sensors': table.get_item(Key={'id': store, 'usage': 'sensors'})['Item'],
                          'main': table.get_item(Key={'id': store, 'usage': 'main'})['Item']}
    return ready_response, no_mail_response

# 指定したジョブ定義の名前のリビジョンを決定する関数（例：~~/job_definition:○の、○部分）
def get_revision(client, job_definition_name):
    job_definitions = \
        client.describe_job_definitions()['jobDefinitions']

    revision_num = 1

    for job in job_definitions:
        if job["jobDefinitionName"] == job_definition_name:
            if job["revision"] > revision_num:
                revision_num = job["revision"]

    return revision_num

def make_command_and_run_job(ready_response: dict, no_mail_response: dict):
    TODAY = dt.today().strftime('%Y_%m_%d')
    
    client = boto3.client('batch')
    ARN = "arn:aws:batch:ap-northeast-1:hogehoge:job-definition/"
    JOB_QUEUE = "arn:aws:batch:ap-northeast-1:hogehoge:job-queue/hogehoge"
    # 上書き対象のジョブ定義の名前
    job_definition = client.register_job_definition(jobDefinitionName='detection_on_batch_{}'.format(TODAY),
                                                type='container',
                                                containerProperties={
                                                    'image': 'hogehoge.dkr.ecr.ap-northeast-1.amazonaws.com/degivege:dev-20211227',
                                                    'vcpus': 2,
                                                    'memory': 14000})
    job_definition_arn = job_definition.get('jobDefinitionArn')
    print(job_definition_arn)
    # status=readyの時、何もしないように設定
    if len(ready_response) == 0:
        pass
    else:
        for ready_store in ready_response:
            JOB_NAME = ready_store+'_'+TODAY
            ready_store_command = 'write command here'\
                                .format(ready_store, 
                                        ready_response[ready_store]['main']['store_name'], 
                                       ",".join(ready_response[ready_store]['sensors']['sensors']), 
                                       ready_response[ready_store]['detection']['detect_config'])
            # DBの空白対策
            a = ready_store_command.split(" ")
            a = [i for i in a if len(i) != 0]
            
            ready_batch_response = client.submit_job(
                                        jobName = JOB_NAME,
                                        jobQueue = JOB_QUEUE,
                                        jobDefinition = job_definition_arn,
                                        containerOverrides={'command': a}
                                    )
    # status=no_mailの時、何もしないように設定
    if len(no_mail_response) == 0:
        pass
    
    else:
        for no_mail_store in no_mail_response:
            JOB_NAME = no_mail_store+'_'+TODAY
            no_mail_store_command = 'write command here'\
                                .format(no_mail_store, 
                                        ready_response[no_mail_store]['main']['store_name'], 
                                        ",".join(ready_response[no_mail_store]['sensors']['sensors']), 
                                        ready_response[no_mail_store]['detection']['detect_config'])

            b = no_mail_store_command.split(" ")
            b = [i for i in b if len(i) != 0]
            no_mail_batch_response = client.submit_job(
                                        jobName = JOB_NAME,
                                        jobQueue = JOB_QUEUE,
                                        jobDefinition = job_definition_arn,
                                        containerOverrides={'command': b}
                                    )