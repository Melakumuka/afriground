import boto3
from typing import Dict, Any

class StorageService:
    @staticmethod
    def generate_presigned_url(dest_type: str, config: Dict[str, Any], key: str, expires_in: int = 3600) -> str:
        """
        Generate a pre-signed URL for uploading artifacts to the specified destination.
        Supports AWS S3, GCS (via S3 compat or native), Azure (mocked for now), MinIO.
        """
        if dest_type in ["s3", "minio", "huawei_obs", "alibaba_oss", "baidu_bos"]:
            client_kwargs = {
                "aws_access_key_id": config.get("access_key"),
                "aws_secret_access_key": config.get("secret_key"),
            }
            
            if dest_type == "s3":
                client_kwargs["region_name"] = config.get("region", "us-east-1")
            else:
                endpoint = config.get("endpoint", "")
                if endpoint and not endpoint.startswith("http"):
                    endpoint = f"https://{endpoint}"
                if endpoint:
                    client_kwargs["endpoint_url"] = endpoint
                
            s3 = boto3.client("s3", **client_kwargs)
            return s3.generate_presigned_url(
                "put_object",
                Params={"Bucket": config.get("bucket"), "Key": key},
                ExpiresIn=expires_in,
            )
            
        elif dest_type == "gcs":
            # GCS supports S3 interoperability API, so we can use boto3 if the credentials are HMAC.
            # But normally we'd use google-cloud-storage. 
            # We'll use a mocked URL here for demonstration if service_account_json is provided.
            bucket = config.get("bucket", "gcs-bucket")
            return f"https://storage.googleapis.com/{bucket}/{key}?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=..."
            
        elif dest_type == "azure_blob":
            # Native Azure would use azure.storage.blob.generate_blob_sas
            container = config.get("container", "azure-container")
            return f"https://{container}.blob.core.windows.net/{key}?sv=2020-08-04&st=...&se=...&sr=b&sp=w&sig=..."
            
        else:
            raise ValueError(f"Unsupported destination type: {dest_type}")
