import boto3
from botocore.config import Config
from os import getenv
import os

def get_s3_client():
    endpoint_url = getenv("CLOUDFLARE_R2_API")
    if not endpoint_url:
        raise ValueError("CLOUDFLARE_R2_API not set in environment")
    
    # R2 endpoint should be the base URL without the bucket name
    # If it's something like https://<accountid>.r2.cloudflarestorage.com/linkinbio
    # we want to strip the /linkinbio
    bucket_name = getenv("BUCKET_NAME", "linkinbio")
    
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv("R2_SECRET_ACCESS_KEY"),
        config=Config(s3={"addressing_style": "virtual"}),
        region_name="auto",
    )

def upload_file_to_r2(file_obj, filename, content_type):
    s3 = get_s3_client()
    bucket_name = getenv("BUCKET_NAME", "linkinbio")
    
    s3.upload_fileobj(
        file_obj,
        bucket_name,
        filename,
        ExtraArgs={"ContentType": content_type}
    )
    
    return filename
