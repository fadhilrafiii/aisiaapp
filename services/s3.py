from django.conf import settings
import boto3
import botocore
from utils.parse import get_s3_file_endpoint


class S3Service:
    # botocore config to enable concurrent partial file upload
    botocore_config = botocore.config.Config(max_pool_connections=20)
    s3 = boto3.client(
        service_name="s3",
        region_name=getattr(settings, "AWS_ACCESS_REGION", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
    )
    bucket_name = getattr(settings, "AWS_BUCKET_NAME", None)
    aws_s3_url = getattr(settings, "AWS_S3_URL", None)

    def get_buckets(self):
        buckets = []
        for bucket in self.s3.list_buckets():
            buckets.append(bucket)

        return buckets

    def get_file(self, file_path):
        file = self.s3.get_object(Bucket=self.bucket_name, Key=file_path)

        return {"url": file_path, "data": file["Body"]}

    def upload_file(self, file, folder_name=None):
        file_path = f"{folder_name}/{file.name}" if (folder_name) else file.name

        self.s3.upload_fileobj(file, self.bucket_name, file_path)

        return f"https://{self.bucket_name}.{self.aws_s3_url}/{file_path}"

    def delete_file(self, file_path):
        endpoint = get_s3_file_endpoint(file_path)
        return self.s3.delete_object(Bucket=self.bucket_name, Key=endpoint)
