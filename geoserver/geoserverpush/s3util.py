from urllib.parse import urlparse
import boto3
from botocore.errorfactory import ClientError


class S3Util(object):
    @staticmethod
    def s3_exists(url):
        o = urlparse(url)
        bucket = o.netloc
        key = o.path.lstrip('/')
        client = boto3.client('s3', region_name='ap-southeast-2')
        try:
            client.head_object(Bucket=bucket, Key=key)
        except ClientError:
            return False
        return True
