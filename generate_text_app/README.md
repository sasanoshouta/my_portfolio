# 文章生成補助アプリ

## 概要
AWSを活用し、特定分野の文章から人が過去に作成した文章を学習し、入力される<br>
文章から人が期待する文章を生成し、業務支援を行う事を目的とする。<br>

## アプリイメージ図
![app_image](https://user-images.githubusercontent.com/99741475/158192103-1e2251d8-ff3d-40d7-b4a0-4fd941ae77c0.png)

## 各フォルダについて
### text_preprocessing_for_T5Model
<hr>
過去に人が作成した文章と生成文章（正解データ）の前処理を実行する為の.pyファイル郡<br>
extract_text_and_create_train_data_japanese.py:<br>
    *　日本語の文章データを前処理する.pyファイル<br>
extract_text_and_create_train_data_ver_eng.py:<br>
    *　英語の文章データを前処理する.pyファイル<br>

### T5Model_on_jupyter_notebook
<hr>
settings.py:<br>
    *　T5モデルの設定が記述された.pyファイル<br>
train.py:<br>
    *　T5モデルの学習フェイズが記述された.pyファイル<br>
predictor.py:<br>
    *　T5モデルの推論フェイズが記述された.pyファイル<br>
train_and_create_endpoint.py:<br>
    *　学習したT5モデルをAWS上にデプロイし、エンドポイント化するフェイズが記述された.pyファイル<br>

### custom_container
<hr>
T5Model_on_jupyter_notebook内のtrain.py, predictor.pyファイルをDocker image内に配置し、AWS SageMaker上でエンドポイント化し推論が実行できるようにする為のファイル郡<br>

### streamlit
<hr>
generate_text_app.py:<br>
    *　EC2上に配置し、指定したエンドポイントにテキストリクエストを送り推論結果を取得・表示するWEBアプリを表示する.pyファイル<br>

アプリ起動イメージ：<br>

