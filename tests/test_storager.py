import os
import re
import pytest
import boto3
import shutil
from pathlib import Path
from pytest import mark, raises
from KassStorager.Storager import Storager


def configS3():
    return {
        "bucket": os.environ.get("AWSS3_BUCKET"),
        "access_key": os.environ.get("AWSS3_ACCESS_KEY"),
        "secret_key": os.environ.get("AWSS3_SECRET_KEY"),
    }


def conn():
    return (
        boto3.client(
            "s3",
            aws_access_key_id=configS3()["access_key"],
            aws_secret_access_key=configS3()["secret_key"],
        ),
        configS3()["bucket"],
    )


def getStorageAndDir():
    return "tests/storage", "test"


def getOtherStorageAndDir():
    return "tests/storage_other", "test_other"


def delete_storages():
    storage = "tests/storage"
    storage2 = "tests/storage_other"

    if os.path.isdir(storage):
        shutil.rmtree(storage)
    if os.path.isdir(storage2):
        shutil.rmtree(storage2)

    client, bucket = conn()
    client.delete_object(Bucket=bucket, Key=storage)
    client.delete_object(Bucket=bucket, Key=storage2)


def create_file(name):
    STORAGE, DIR = getStorageAndDir()
    filepath = STORAGE + "/" + DIR + "/" + name
    Storager(STORAGE).make(DIR)
    with open(filepath, "w") as arquivo:
        arquivo.write("Este é um exemplo de conteúdo para o arquivo de texto.\n")
        arquivo.write("Você pode adicionar mais linhas conforme necessário.\n")
    return name


@pytest.fixture(scope="module")
def reset_storage():
    yield
    delete_storages()


# tests OS


def test_criar_diretorio(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    Storager(STORAGE).make(DIR)
    path = os.path.join(STORAGE, DIR)
    assert True == os.path.isdir(path)


def test_verificar_se_diretorio_existe(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    check = Storager(STORAGE).getDir(DIR).exists()
    assert True == check


def test_verificar_se_diretorio_nao_existe(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    DIR = f"{DIR}_notexist"
    with raises(
        Exception,
        match=re.escape(f"Directory not exists"),
    ):
        Storager(STORAGE).getDir(DIR).exists()


def test_deletar_um_diretorio_vazio(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    DIR = f"{DIR}/newdir"
    Storager(STORAGE).make(DIR)
    check = Storager(STORAGE).getDir(DIR).delete()
    assert True == check


def test_deletar_um_diretorio_nao_vazio(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    with raises(
        OSError,
        match=re.escape("A pasta não está vazia"),
    ):
        dir = os.path.join(DIR, "123")
        Storager(STORAGE).make(dir)
        Storager(STORAGE).getDir(DIR).delete()


def test_deletar_um_diretorio_nao_vazio_forcado(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    dir = os.path.join(DIR, "123")
    Storager(STORAGE).make(dir)
    check = Storager(STORAGE).getDir(DIR).delete(force=True)
    assert True == check


def test_deletar_arquivo(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    name = create_file("arquivo.txt")
    check = Storager(STORAGE).getDir(DIR).deleteFile(name)
    assert True == check


def test_limpar_diretorio(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    create_file("arquivo.txt")
    create_file("arquivo2.txt")

    check = Storager(STORAGE).getDir(DIR).cleanDir()
    assert True == check


def test_copiar_arquivo_para_outro_storage(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    name = create_file("arquivo.txt")

    other_storage = Storager(OTHER_STORAGE).make(OTHER_DIR).getDir(OTHER_DIR)
    other_storage.deleteFile(name)

    check = Storager(STORAGE).getDir(DIR).getFile(name).copyTo(other_storage)

    assert True == check


def test_mover_arquivo_para_outro_storage(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    name = create_file("arquivo.txt")

    other_storage = Storager(OTHER_STORAGE).make(OTHER_DIR).getDir(OTHER_DIR)
    other_storage.deleteFile(name)

    check = Storager(STORAGE).getDir(DIR).getFile(name).moveTo(other_storage)
    assert True == check


def test_copiar_arquivo_local_para_s3(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    storager_s3 = (
        Storager(storage=STORAGE, driver="s3", config=configS3()).make(DIR).getDir(DIR)
    )
    name = create_file("arquivoLocalToS3.txt")
    check = Storager(STORAGE).getDir(DIR).getFile(name).copyTo(storager_s3)
    assert True == check


def test_mover_arquivo_local_para_s3(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    storager_s3 = (
        Storager(storage=STORAGE, driver="s3", config=configS3()).make(DIR).getDir(DIR)
    )
    name = create_file("arquivoLocalToS3.txt")
    check = Storager(STORAGE).getDir(DIR).getFile(name).moveTo(storager_s3)
    assert True == check


def test_copiar_varios_arquivos_para_s3(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    create_file("arquivo.txt")
    create_file("arquivo2.txt")
    create_file("arquivo3.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="s3", config=configS3())
        .make(OTHER_DIR)
        .getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE).getDir(DIR).getFile(ext="txt").copyTo(other_storage)
    )

    assert True == check


def test_mover_varios_arquivos_para_s3(reset_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    create_file("arquivo.txt")
    create_file("arquivo2.txt")
    create_file("arquivo3.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="s3", config=configS3())
        .make(OTHER_DIR)
        .getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE).getDir(DIR).getFile(ext="txt").moveTo(other_storage)
    )
    assert True == check
