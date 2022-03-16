# ウェアラブル端末が測定したデータを可視化

## 概要
AWSを活用し、他社環境のDBへアクセスしてウェアラブル端末から<br>
バイタルデータを取得し、そのデータをstreamlit上で可視化する。<br>

## アプリアーキテクト図
![vital1](https://user-images.githubusercontent.com/99741475/158331531-473c960f-ae5a-4829-9783-7e0a4a5c070e.png)

## アプリ起動イメージ
![vital2](https://user-images.githubusercontent.com/99741475/158331542-5c9ada4b-820b-4085-86d0-0f69ff5eb585.png)

## 各フォルダについて
### apiacsess
<hr>
get_data_and_upload_to_s3.py:<br>
    *  提供されたAPIからデータを取得し、json形式で指定のS3環境に保存する.pyファイル<br>

### streamlit
<hr>
s3pref.py:<br>
    *  指定したS3の指定したPREFIXの階層の一覧を取得する.pyファ>イル<br>
vital_streamlit.py:<br>
    *  EC2上に配置し、指定したユーザーの指定した日時のバイタルデータを可視化するWEBアプリを表示する.pyファ>イル<br>

