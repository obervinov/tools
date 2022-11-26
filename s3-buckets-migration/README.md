# S3 Buckets migration
This set of scripts was used to transfer bucket objects from one s3 to another.

## Requirements
- [boto3 1.26.16](https://pypi.org/project/boto3/)
- [botocore 1.29.16](https://pypi.org/project/botocore/)


## Example
```sh
# Script for unloading objects from src s3 and further loading into dst s3
python3 s3_upload_content.py
# Unloading objects from s3 with date filtering
python3 s3_download_by_date.py
# Unloading objects from s3 with filtering by file path
python3 s3_download_by_path.py
```