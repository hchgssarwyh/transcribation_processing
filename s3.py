import boto3
import botocore
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
load_dotenv()
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')

class MinIO:
    def __init__(
        self,
        key: str,
        secret_key: str,
        endpoint_url: str,
    ) -> None:
        self.client = boto3.client(
            "s3",
            aws_access_key_id=key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
        )


    def upload_file(self, file_content, filename) -> None:
        self.client.put_object(
            Bucket=MINIO_BUCKET_NAME,
            Key=filename,
            Body=file_content
        )

    def if_file_exists(self, path, bucket_name: str) -> bool:
        try:
            self.client.head_object(Bucket=bucket_name, Key=path)
            return True
        except Exception:
            return False

    def _ensure_bucket_exists(self, bucket_name):
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            self.client.create_bucket(Bucket=bucket_name)
            # MinIO может не поддерживать установку ACL следующим образом
            # Удалите или замените следующую строку в зависимости от вашего требования
            # self.client.put_bucket_acl(Bucket=bucket_name, ACL='public-read')

    def _ensure_folder_exists(self, bucket_name, folder):
        if folder:
            result = self.client.list_objects_v2(Bucket=bucket_name, Prefix=folder, Delimiter="/")
            if "Contents" not in result:
                self.client.put_object(Bucket=bucket_name, Key=f"{folder}/")
