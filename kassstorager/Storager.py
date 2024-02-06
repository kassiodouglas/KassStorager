from datetime import datetime as dt

from kassstorager.StoragerAwsS3 import StoragerAwsS3
from kassstorager.StoragerOs import StoragerOs


class Storager:
    def __init__(self, storage: str, driver: str = "os", config: dict = None) -> None:
        self.storage = storage
        self.selected_local_dir = None
        self.selected_remote_dir = None

        self.files_to = []

        if driver.lower() == "os":
            self.storager_instance = StoragerOs(storage, config)
        elif driver.lower() == "s3":
            self.storager_instance = StoragerAwsS3(storage, config)
        else:
            raise Exception(f'Driver "{driver}" not supported')

    def make(self, dir: str):
        self.storager_instance.make(dir)
        return self

    def getDir(self, dir: str):
        x = self.storager_instance.getDir(dir)
        self.selected_local_dir = x.selected_local_dir
        return self

    def exists(self):
        return self.storager_instance.exists()

    def delete(self, force: bool = False):
        return self.storager_instance.delete(force)

    def deleteFile(self, file_name: str):
        return self.storager_instance.deleteFile(file_name)

    def cleanDir(self):
        return self.storager_instance.cleanDir()

    def copyTo(self, storager: "Storager", ext="*", filters: list[str] = []):
        return self.storager_instance.copyTo(storager, ext, filters)

    def moveTo(self, storager: "Storager", ext="*", filters: list[str] = []):
        return self.storager_instance.moveTo(storager, ext, filters)

    def getFile(self, file_name: str):
        self.storager_instance.getFile(file_name)
        return self
