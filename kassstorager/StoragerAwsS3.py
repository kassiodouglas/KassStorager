import os
import shutil
from datetime import datetime as dt
from pathlib import Path

import boto3


class StoragerAwsS3:
    def __init__(self, storage: str, config: dict) -> None:
        self.storage = storage
        self.selected_local_dir = None
        self.selected_remote_dir = None

        self.files_to = []
        self.__client = boto3.client(
            "s3",
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_key"],
        )
        self.__bucket_name = config["bucket"]

    def make(self, dir: str) -> None:
        dir = self.storage + "/" + dir + "/"
        self.__client.put_object(Bucket=self.__bucket_name, Key=dir)
        return self

    def getDir(self, dir: str):
        dir = self.storage + "/" + dir + "/"
        response = self.__client.list_objects_v2(Bucket=self.__bucket_name, Prefix=dir)
        if "Contents" in response:
            self.selected_local_dir = dir
            return self

        raise Exception(f"Directory not exists")

    def exists(self):
        return False if self.selected_local_dir is None else True

    def delete(self, force: bool = False):

        if not self.selected_local_dir.endswith("/"):
            self.selected_local_dir += "/"

        print(self.selected_local_dir)
        try:
            self.__client.delete_object(
                Bucket=self.__bucket_name, Key=self.selected_local_dir
            )
            return True
        except Exception as err:
            raise Exception(err)

        # try:
        #     if force == False:
        #         if "Contents" in response:
        #             for obj in response.get("Contents", []):
        #                 if obj["Key"][-1] != "/":
        #                     raise OSError(
        #                         f"Error to delete '{self.selected_local_dir}', directory not empty!"
        #                     )

        #         self.__client.delete_object(
        #             Bucket=self.__bucket_name, Key=f"{self.selected_local_dir}/"
        #         )

        #     else:
        #         for obj in response.get("Contents", []):
        #             self.__client.delete_object(
        #                 Bucket=self.__bucket_name, Key=obj["Key"]
        #             )
        # except OSError as err:
        #     raise OSError(err)

    def deleteFile(self, file_name: str):
        file = self.selected_local_dir + "/" + file_name
        self.__client.delete_object(Bucket=self.__bucket_name, Key=file)

    def cleanDir(self):
        response = self.__client.list_objects_v2(
            Bucket=self.__bucket_name, Prefix=f"{self.selected_local_dir}/"
        )
        for obj in response.get("Contents", []):
            if obj["Key"][-1] != "/":
                self.__client.delete_object(Bucket=self.__bucket_name, Key=obj["Key"])

    def copyTo(self, storager: "Storager", ext="*", filters: list[str] = []):
        pass

    def moveTo(self, storager: "Storager", ext="*", filters: list[str] = []):
        pass

    def getFile(self, file_name: str):
        pass

    def __copymove(
        self,
        selected_local_dir: str,
        selected_remote_dir: str,
        ext="*",
        filters: list[str] = [],
        moveOrCopy: str = "copy",
    ):
        pass
