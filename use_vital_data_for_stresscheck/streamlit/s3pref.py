import boto3
from typing import List

def ls(bucket: str, prefix: str, recursive: bool = False) -> List[str]:
    """S3上のファイルリスト取得

    Args:
        bucket (str): バケット名
        prefix (str): バケット以降のパス
        recursive (bool): 再帰的にパスを取得するかどうか

    """
    paths: List[str] = []
    paths = __get_all_keys(
        bucket, prefix, recursive=recursive)
    return paths


def __get_all_keys(bucket: str, prefix: str, keys: List = None, marker: str = '', recursive: bool = False) -> List[str]:
    """指定した prefix のすべての key の配列を返す

    Args:
        bucket (str): バケット名
        prefix (str): バケット以降のパス
        keys (List): 全パス取得用に用いる
        marker (str): 全パス取得用に用いる
        recursive (bool): 再帰的にパスを取得するかどうか

    """
    s3 = boto3.client('s3')
    if recursive:
        response = s3.list_objects(
            Bucket=bucket, Prefix=prefix, Marker=marker)
    else:
        response = s3.list_objects(
            Bucket=bucket, Prefix=prefix, Marker=marker, Delimiter='/')

    # keyがNoneのときは初期化
    if keys is None:
        keys = []

    if 'CommonPrefixes' in response:
        # Delimiterが'/'のときはフォルダがKeyに含まれない
        keys.extend([content['Prefix']
                    for content in response['CommonPrefixes']])
    if 'Contents' in response:  # 該当する key がないと response に 'Contents' が含まれない
        keys.extend([content['Key'] for content in response['Contents']])
        if 'IsTruncated' in response:
            return __get_all_keys(bucket=bucket, prefix=prefix, keys=keys, marker=keys[-1], recursive=recursive)
    return keys
