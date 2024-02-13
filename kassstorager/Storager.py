from KassStorager.StoragerAwsS3 import StoragerAwsS3
from KassStorager.StoragerOs import StoragerOs


class Storager:
    def __init__(self, storage: str, driver: str = "os", config: dict = None) -> None:
        self.storage = storage
        self.selected_local_dir = None
        self.selected_remote_dir = None

        self.files_to = []

        if driver.lower() == "os":
            self.storager_instance = StoragerOs(storage, config, driver)
        elif driver.lower() == "s3":
            self.storager_instance = StoragerAwsS3(storage, config, driver)
        else:
            raise Exception(f'Driver "{driver}" not supported')

    def make(self, dir: str):
        """Cria um diretorio no Storager configurado

        Args:
            dir (str): nome do novo diretorio

        Returns:
           Storager: propria classe para encadeamento de metodos
        """
        self.storager_instance.make(dir)
        return self

    def getDir(self, dir: str):
        x = self.storager_instance.getDir(dir)
        self.selected_local_dir = x.selected_local_dir
        return self

    def exists(self):
        """Verifica se o diretorio selecionado existe ou não  

        Returns:
            bool: Retorna se o diretorio selecionado existe ou não  
        """
        return self.storager_instance.exists()

    def delete(self, force: bool = False):
        """Exclui um diretorio vazio ou com force=true, exclui um não vazio

        Args:
            force (bool, optional): Define se pode excluir um diretorio não vazio. Defaults to False.

        Returns:
            bool: Retorna se a execução foi ou não bem sucedida
        """
        return self.storager_instance.delete(force)

    def deleteFile(self, file_name: str):
        """Exclui um arquivo no diretorio selecionado

        Args:
            file_name (str): Nome do arquivo com a extensão

        Returns:
            bool: Retorna se a execução foi ou não bem sucedida
        """
        return self.storager_instance.deleteFile(file_name)

    def cleanDir(self):
        """Deleta todo o conteudo de um diretorio selecionado      

        Returns:
            bool: Retorna se a execução foi ou não bem sucedida
        """
        return self.storager_instance.cleanDir()

    def copyTo(self, storager: "Storager"):
        """Copia os arquivos selecioandos para outro Storager

        Args:
            storager (Storager): Instância de um Storager()

        Returns:
            bool: Retorna se a execução foi ou não bem sucedida
        """
        return self.storager_instance.copyTo(storager)

    def moveTo(self, storager: "Storager"):
        """Move os arquivos selecioandos para outro Storager

        Args:
            storager (Storager): Instância de um Storager()

        Returns:
            bool: Retorna se a execução foi ou não bem sucedida
        """
        return self.storager_instance.moveTo(storager)

    def getFile(self, file_name: str = None, ext="*", filters: list[str] = []):
        """Busca arquivos de acordo com as configurações no diretorio selecionado

        Args:
            file_name (str, optional): Nomde de um arquivo especifico. Defaults to None.
            ext (str, optional): Extensão dos arquivos a serem selecionados. Defaults to "*".
            filters (list[str], optional): Filtros que verificam se há os termos passados nos nomes dos arquivos. Defaults to [].

        Returns:
            Storager: propria classe para encadeamento de metodos
        """
        self.storager_instance.getFile(file_name, ext, filters)
        return self
