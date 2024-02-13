import boto3
import os
from datetime import datetime as dt
from datetime import timezone


class StoragerAwsS3:
    def __init__(self, storage: str, config: dict, driver: str) -> None:
        self.storage = storage
        self.driver = driver
        self.selected_local_dir = None
        self.selected_remote_dir = None
        self.__ext = "*"
        self.__filters = []
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

    def getDir(self, dir: str = ""):
        dir = self.storage + "/" + dir + "/" if dir != "" else self.storage + "/"
        response = self.__client.list_objects_v2(Bucket=self.__bucket_name, Prefix=dir)
        if "Contents" in response:
            self.selected_local_dir = dir
            return self

        raise Exception(f"Directory not exists")

    def exists(self):
        return False if self.selected_local_dir is None else True

    def delete(self, force: bool = False):
        
        response = self.__client.list_objects_v2(Bucket=self.__bucket_name, Prefix=self.selected_local_dir)  
        for index, obj in enumerate(response.get('Contents', [])):
            if obj['Key'] == self.selected_local_dir:
                del response['Contents'][index]
        
        
        if force: 
            for obj in response.get('Contents', []):
                try:
                    self.__client.delete_object(Bucket=self.__bucket_name, Key=obj['Key'])
                except Exception as err:
                    raise Exception(err)
        else:
            
            if 'Contents' in response and response['Contents'] != []:                    
                raise Exception("A pasta não está vazia")
                
            try:               
                
                self.__client.delete_object(
                    Bucket=self.__bucket_name, Key=self.selected_local_dir
                )
            except Exception as err:
                raise Exception(err)
        return True

    def deleteFile(self, file_name: str):
        try:
            self.selected_local_dir = self.selected_local_dir + file_name
            self.__client.delete_object(
                Bucket=self.__bucket_name, Key=self.selected_local_dir
            )
            return True
        except Exception as err:
            raise Exception(err)

    def cleanDir(self):
        response = self.__client.list_objects_v2(
            Bucket=self.__bucket_name, Prefix=self.selected_local_dir
        )
        for obj in response.get("Contents", []):
            if obj["Key"][-1] != "/":
                self.__client.delete_object(Bucket=self.__bucket_name, Key=obj["Key"])
        return True

    def copyTo(self, storager):
        selected_remote_dir = storager
        return self.__copymove(
            self.selected_local_dir,
            selected_remote_dir,
            moveOrCopy="copy",
        )

    def moveTo(self, storager):
        selected_remote_dir = storager
        return self.__copymove(
            self.selected_local_dir,
            selected_remote_dir,
            moveOrCopy="move",
        )

    def getFile(self, file_name: str = None, ext="*", filters: list[str] = []):

        if file_name is not None:
            file = os.path.join(self.selected_local_dir, file_name)
            self.files_to.append(file)

        else:
            self.__filters = filters
            self.__ext = ext

            objects = self.__client.list_objects_v2(
                Bucket=self.__bucket_name, Prefix=self.selected_local_dir
            )
            if "Contents" in objects:
                for obj in objects["Contents"]:
                    self.files_to.append(obj["Key"])

        return self

    def __copymove(
        self,
        selected_local_dir: str,
        selected_remote_dir: str,
        moveOrCopy: str = "copy",
    ):
        for file in self.files_to:
            filename = os.path.basename(file)

            origin = {"Bucket": self.__bucket_name, "Key": file}

            try:
                local_filePath = self.__client.head_object(
                    Bucket=self.__bucket_name, Key=file
                )
            except:
                local_filePath = None

            if local_filePath == None:
                continue

            if not file.endswith(self.__ext) and self.__ext != "*":
                continue

            if local_filePath["ContentLength"] == 0:
                continue

            name = os.path.splitext(os.path.basename(file))[0]
            nextFilter = True
            for filter in self.__filters:
                if filter.lower() not in name.lower():
                    nextFilter = False
            if nextFilter == False:
                continue

            if selected_remote_dir.storager_instance.driver == "s3":
                destination = {
                    "Bucket": selected_remote_dir.storager_instance.__bucket_name,
                    "Key": f"{selected_remote_dir.storager_instance.selected_local_dir}{filename}",
                }

                try:
                    remote_filepath = self.__client.head_object(
                        Bucket=destination["Bucket"], Key=destination["Key"]
                    )
                except:
                    remote_filepath = None

                if remote_filepath is not None:
                    local_date_modify = (
                        local_filePath["LastModified"]
                        - dt(1970, 1, 1, tzinfo=timezone.utc)
                    ).total_seconds()

                    remote_date_modify = (
                        remote_filepath["LastModified"]
                        - dt(1970, 1, 1, tzinfo=timezone.utc)
                    ).total_seconds()

                    if local_date_modify <= remote_date_modify:
                        continue

                try:
                    self.__client.copy_object(
                        Bucket=self.__bucket_name,
                        CopySource=origin,
                        Key=destination["Key"],
                    )
                    if moveOrCopy == "move":
                        self.__client.delete_object(
                            Bucket=origin["Bucket"], Key=origin["Key"]
                        )
                except IOError as e:
                    term = "copied" if moveOrCopy == "copy" else "moved"
                    raise Exception(f"Error in {term} file '{local_filePath}': {e}")

            elif selected_remote_dir.storager_instance.driver == "os":

                remote_filepath = os.path.join(
                    selected_remote_dir.selected_local_dir, filename
                )

                if os.path.isfile(remote_filepath):
                    local_date_modify = (
                        local_filePath["LastModified"]
                        - dt(1970, 1, 1, tzinfo=timezone.utc)
                    ).total_seconds()

                    remote_date_modify = os.path.getmtime(remote_filepath)

                    if local_date_modify <= remote_date_modify:
                        continue

                try:
                    self.__client.download_file(
                        self.__bucket_name, origin["Key"], remote_filepath
                    )
                    if moveOrCopy == "move":
                        self.__client.delete_object(
                            Bucket=origin["Bucket"], Key=origin["Key"]
                        )
                except IOError as e:
                    term = "copied" if moveOrCopy == "copy" else "moved"
                    raise Exception(f"Error in {term} file '{local_filePath}': {e}")

            else:
                raise Exception("Driver not supported")
        return True
