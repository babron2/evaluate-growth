import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account


def get_credentials():
    if "gcp_service_account" in st.secrets:
        return service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
    else:
        return None


class Gcs_client:
    def __init__(self) -> None:
        self.credentials = get_credentials()
        self.client = storage.Client(
            credentials=self.credentials,
            project=self.credentials.project_id,
        )

    def create_bucket(self, bucket_name):
        """GCSにバケットがなければ作成する。

        Args:
            bucket_name (_type_): _description_
        """

        if self.client.bucket(bucket_name).exists():
            print(f"already exists {bucket_name}")
        else:
            print(f"create {bucket_name}")
            self.client.create_bucket(bucket_name, location="US-WEST1")

    def list_all_objects(self, bucket_name):
        """バケットの中身をリストで出力する。

        Args:
            bucket_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        blobs = self.client.list_blobs(bucket_name)
        all_objects = [blob.name for blob in blobs]
        return all_objects

    def upload_gcs(self, bucket_name, from_path, to_path, dry_run=False):
        """GSCにファイルをアップロードする。

        Args:
            bucket_name (_type_): _description_
            from_path (_type_): _description_
            to_path (_type_): _description_
            dry_run (bool, optional): _description_. Defaults to False.
        """
        print(f"{from_path} to {bucket_name}/{to_path}")
        if dry_run:
            pass
        else:
            bucket = self.client.get_bucket(bucket_name)
            blob_gcs = bucket.blob(to_path)
            # ローカルのファイルパスを指定
            blob_gcs.upload_from_string(from_path)
