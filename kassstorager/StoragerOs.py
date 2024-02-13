import os
import shutil
from datetime import datetime as dt
from datetime import timezone
from pathlib import Path


class StoragerOs:
    def __init__(self, storage: str, config: dict, driver: str) -> None:
        self.storage = storage
        self.driver = driver
        self.selected_local_dir = None
        self.selected_remote_dir = None
        self.__ext = "*"
        self.__filters = []

        self.files_to = []

    def make(self, dir: str) -> None:
        """Cria um diretório dentro do storage

        Args:
            dir (str | list[str]): caminho para o diretório a ser criado
        """
        dir = Path(f"{self.storage}/{dir}")
        os.makedirs(dir, exist_ok=True)
        return self

    def getDir(self, dir: str):
        """Seleciona um diretório dentro do storage

        Args:
            dir (str): caminho para o diretório intero dentro do storage

        Raises:
            Exception: caso não houver um diretório valido

        Returns:
            (Storager): retorna o proprio storage
        """
        dir = Path(f"{self.storage}/{dir}")
        if os.path.exists(dir):
            self.selected_local_dir = dir
            return self

        raise Exception(f"Directory not exists")

    def exists(self):
        """Retorna se um diretório existe ou não no storage

        Returns:
            bool: valor booleano indicando se é verdadeiro ou falso
        """
        return False if self.selected_local_dir is None else True

    def delete(self, force: bool = False):
        """Deleta um diretório no storage, user force=True para deletar mesmo o diretório não estando vazio

        Args:
            force (bool, optional): como True permite deletar um diretório não vazio. Defaults to False.

        Raises:
            OSError: ao tentar excluir um diretorio não vazio sem forçar

        Returns:
            bool: verdadeiro se sucesso na exclusão
        """
        try:
            if force:
                shutil.rmtree(self.selected_local_dir)
            else:
                os.rmdir(self.selected_local_dir)
            return True
        except OSError as err:
            raise OSError(err)

    def deleteFile(self, file_name: str):
        """Deleta um arquivo do diretório selecionado

        Args:
            file_name (str): nome do arquivo ser deletedo

        Raises:
            OSError: em caso de falha ao escluir, será lançado uma exceção

        Returns:
            bool: em caso de sucesso, retorna verdadeiro
        """
        try:
            file = os.path.join(self.selected_local_dir, file_name)
            if os.path.isfile(file):
                os.remove(file)
            return True
        except OSError as err:
            raise OSError(err)

    def cleanDir(self):
        """Excluir todo o conteudo de um diretório

        Raises:
            OSError: em caso de falha, uma exceção será lançada

        Returns:
            bool: em caso de sucesso, retorna verdadeiro
        """

        files = os.listdir(self.selected_local_dir)

        for file in files:
            pathFile = os.path.join(self.selected_local_dir, file)

            try:
                os.remove(pathFile)
            except OSError as err:
                raise OSError(err)

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

    def getFile(self, file_name: str, ext="*", filters: list[str] = []):

        if file_name is not None:
            file = os.path.join(self.selected_local_dir, file_name)
            self.files_to.append(file)
        else:
            self.__filters = filters
            self.__ext = ext

            for file in os.listdir(self.selected_local_dir):
                self.files_to.append(file)

        return self

    def __copymove(
        self,
        selected_local_dir: str,
        selected_remote_dir: str,
        moveOrCopy: str = "copy",
    ):
        for file in self.files_to:
            filename = os.path.basename(file)
            local_filePath = os.path.join(selected_local_dir, filename)

            if os.path.exists(local_filePath) == False:
                continue

            if os.path.getsize(local_filePath) == 0:
                continue

            if not file.endswith(self.__ext) and self.__ext != "*":
                continue

            name = os.path.splitext(os.path.basename(file))[0]
            nextFilter = True
            for filter in self.__filters:
                if filter.lower() not in name.lower():
                    nextFilter = False
            if nextFilter == False:
                continue

            if selected_remote_dir.storager_instance.driver == "s3":
                clientS3 = selected_remote_dir.storager_instance._StoragerAwsS3__client
                bucket = (
                    selected_remote_dir.storager_instance._StoragerAwsS3__bucket_name
                )
                remote_filepath = selected_remote_dir.selected_local_dir + filename

                try:
                    object = clientS3.head_object(Bucket=bucket, Key=remote_filepath)

                    isremote = True
                except Exception as e:
                    isremote = False

                if isremote:
                    local_date_modify = os.path.getmtime(local_filePath)
                    remote_date_modify = (
                        object["LastModified"] - dt(1970, 1, 1, tzinfo=timezone.utc)
                    ).total_seconds()
                    if local_date_modify <= remote_date_modify:
                        continue

                clientS3.upload_file(local_filePath, bucket, remote_filepath)

                if moveOrCopy == "move":
                    os.unlink(local_filePath)

            elif selected_remote_dir.storager_instance.driver == "os":
                remote_filepath = os.path.join(
                    selected_remote_dir.selected_local_dir, filename
                )
                if os.path.isfile(remote_filepath):
                    local_date_modify = dt.fromtimestamp(
                        os.path.getmtime(local_filePath)
                    )
                    remote_date_modify = dt.fromtimestamp(
                        os.path.getmtime(remote_filepath)
                    )

                    if local_date_modify <= remote_date_modify:
                        continue

                try:

                    if moveOrCopy == "copy":
                        shutil.copy2(local_filePath, remote_filepath)
                        term = "copied"
                    else:
                        shutil.move(local_filePath, remote_filepath)
                        term = "moved"

                except IOError as e:
                    term = "copied" if moveOrCopy == "copy" else "moved"
                    raise Exception(f"Error in {term} file '{local_filePath}': {e}")

            else:
                raise Exception("Driver not supported")
        return True
