import streamlit as st
import boto3
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime as dt
import datetime
from typing import List
import user
import s3pref
import base64

# 必要な値の準備
user_list = user.user_list
s3 = boto3.resource('s3')
AWS_S3_BUCKET_NAME = "hogehoge"
bucket = s3.Bucket(AWS_S3_BUCKET_NAME)
# day = "2022-03-09"
# day = dt.now().strftime("%Y-%m-%d")
# pref = "vital_data/{}/{}/".format(day, user_list[0])
keys = s3pref.ls(AWS_S3_BUCKET_NAME, "vital_data/", recursive=False)
DAYS = [i.replace('vital_data/', '')[:-1] for i in keys]
st.title("バイタル可視化ツール")

# サイドバー表示
st.sidebar.title('ユーザー一覧')
selector = st.sidebar.selectbox('ユーザーを選んでください',tuple(user_list), key="now_user")

st.sidebar.title('日付一覧')
day = st.sidebar.selectbox('可視化したい日付を選んでください',tuple(DAYS), key="now_day")

pref = 'vital_data/{}/{}/'.format(day, st.session_state["now_user"])

# 指定した日付、ユーザーのバイタルデータを取得
obj_name = bucket.meta.client.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=pref)
name_list = [o.get('Key') for o in obj_name.get('Contents')]
# 取得できているデータまでのファイルを取得
exit_data_list = []
for item in name_list:
    obj = s3.Object(AWS_S3_BUCKET_NAME, item)
    response = obj.get()
    body = response["Body"].read()
    json_body = json.loads(body.decode("utf-8"))
    if len(json_body) == 0:
        continue
    else:
        exit_data_list.append(json_body)

hr_list = []
datetime_index = []
step_list = []
skin_temp_list = []
ppi_list = []
ppi_datetime = []

for item in exit_data_list:
    for record in item[str(st.session_state['now_user'])]:
        if 'ppi' in record.keys():
            ppi_list.append(record['ppi'])
            tmp_time = dt.fromtimestamp(record['timestamp']) + datetime.timedelta(hours=9)
            ppi_datetime.append(tmp_time.strftime("%Y/%m/%d %H:%M:%S"))
            
        else:
            hr_list.append(record['hr'])
            step_list.append(record['steps'])
            skin_temp_list.append(record['skin_temp'] / 256.0)
            tmp_time = dt.fromtimestamp(record['timestamp']) + datetime.timedelta(hours=9)
            datetime_index.append(tmp_time.strftime("%Y/%m/%d %H:%M:%S"))

# ppiデータの可視化
final_ppi = dict()
tmp = []
count = 0

for data in ppi_list:
    sample = base64.b64decode(data)
    # バイト列→int型変換（ビッグエンディアンでなくリトルエンディアンでデコードとの事（仕様））
    num_ppi_data = int.from_bytes(sample[8:9], byteorder='little')
    
    for k in range(0, num_ppi_data * 4, 4):
        tmp.append({"offset": int.from_bytes(sample[k+10:k+12], byteorder='little') / 1000, 
            "ppi": int.from_bytes(sample[k+12:k+14], byteorder='little') / 1000})
    final_ppi[count] = tmp
    tmp = []
    count += 1


ppi_ave = []
tmp = 0.0
sampling_ave = 0.0
total_len = 0
for i in range(len(final_ppi)):
    for record in final_ppi[i]:
        tmp += record['ppi']
        total_len += len(record)
    tmp = tmp / len(final_ppi[i])
    ppi_ave.append(tmp)

st.write("表示バイタルデータ日付：{}".format(day))
st.write("最新バイタルデータ時間：{}".format(datetime_index[-1]))
# 脈拍、歩数、皮膚温度の可視化
fig = plt.figure(figsize=(30, 20))
ax = fig.add_subplot(111)
ax.set_title('user ID:{} vital ploted figure'.format(st.session_state['now_user']), size=50)
ax.plot(datetime_index, hr_list, label="hr")
ax.plot(datetime_index, step_list, label="steps")
ax.plot(datetime_index, skin_temp_list, label="skin_temp")
# plt.plot(datetime_index, ppi_ave, label='ppi')
ax.set_xlabel('time', size=50)
ax.set_ylabel('hr/min', size=50)
ax.set_xticks(np.arange(0, len(datetime_index), 50), labelsize=50)
ax.set_yticks(np.arange(0, 255, 15), labelsize=50)
for tick in ax.get_xticklabels():
    tick.set_rotation(75)

ax.legend(fontsize=30)
st.write(fig)

st.write("最新ppiデータ時間：{}".format(ppi_datetime[-1]))
fig2 = plt.figure(figsize=(30, 20))
ax2 = fig2.add_subplot(111)
ax2.set_title('user ID:{} ppi ploted figure'.format(st.session_state['now_user']), size=50)
ax2.plot(ppi_datetime, ppi_ave, label="ppi")
ax2.set_xlabel(xlabel='time', size=50)
# plt.ylabel(ylabel='hr/min', size=20)
ax2.set_xticks(np.arange(0, len(ppi_datetime), 50))
# ax2.set_yticks(size=15)
for tick2 in ax2.get_xticklabels():
    tick2.set_rotation(75)
ax2.legend(fontsize=30)
st.write(fig2)
