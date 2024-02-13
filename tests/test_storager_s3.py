import boto3
import os
import re
import pytest
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
    res = client.list_objects_v2(Bucket=bucket, Prefix='tests/')  
    for obj in res.get('Contents', []):
        try:
            client.delete_object(Bucket=bucket, Key=obj['Key'])
        except Exception as err:
            raise Exception(err)


def create_file(name):
    STORAGE, DIR = getStorageAndDir()
    filepath = STORAGE + "/" + DIR + "/" + name
    file_content = "Hello, this is your file content!"
    s3_client, bucket = conn()
    s3_client.put_object(Body=file_content, Bucket=bucket, Key=filepath)
    return name


@pytest.fixture(scope="session")
def reset_s3_storage():
    yield
    delete_storages()


# tests S3


def test_s3_criar_diretorio(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    Storager(storage=STORAGE, driver="s3", config=configS3()).make(DIR)
    client, bucket = conn()
    response = client.list_objects_v2(Bucket=bucket, Prefix=f"{STORAGE}/{DIR}/")
    assert True == (True if "Contents" in response else False)


def test_s3_verificar_se_diretorio_existe(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3()).getDir(DIR).exists()
    )
    assert True == check


def test_s3_verificar_se_diretorio_nao_existe(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    DIR = f"{DIR}_notexist"
    with raises(
        Exception,
        match=re.escape(f"Directory not exists"),
    ):
        Storager(storage=STORAGE, driver="s3", config=configS3()).getDir(DIR).exists()


def test_s3_deletar_diretorio_vazio(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    DIR = f"{DIR}/newdir"
    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .make(DIR)
        .getDir(DIR)
        .delete()
    )
    assert True == check


def test_s3_deletar_um_diretorio_nao_vazio(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()  
    with raises(
        Exception,
        match=re.escape("A pasta não está vazia"),
    ):
        dir = os.path.join(DIR, "123")
        Storager(storage=STORAGE, driver="s3", config=configS3()).make(dir)
        Storager(storage=STORAGE, driver="s3", config=configS3()).make(DIR).getDir(DIR).delete()


def test_deletar_um_diretorio_nao_vazio_forcado(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    
    dir = os.path.join(DIR, "123")
    Storager(storage=STORAGE, driver="s3", config=configS3()).make(dir)
    
    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .make(DIR)
        .getDir(DIR)
        .delete(force=True)
    )
    assert True == check


def test_s3_deletar_arquivo(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    name = create_file("arquivo.txt")
    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .deleteFile(name)
    )
    assert True == check


def test_s3_limpar_diretorio(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    create_file("arquivo.txt")
    create_file("arquivo2.txt")

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3()).getDir(DIR).cleanDir()
    )
    assert True == check


def test_s3_copiar_arquivo_para_outro_storage(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    name = create_file("arquivo.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="s3", config=configS3())
        .make(OTHER_DIR)
        .getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .getFile(name)
        .copyTo(other_storage)
    )

    assert True == check


def test_s3_mover_arquivo_para_outro_storage(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    name = create_file("arquivo.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="s3", config=configS3())
        .make(OTHER_DIR)
        .getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .getFile(name)
        .moveTo(other_storage)
    )

    assert True == check


def test_s3_copiar_arquivo_para_local(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    name = create_file("arquivo.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="os").make(OTHER_DIR).getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .getFile(name)
        .copyTo(other_storage)
    )

    assert True == check


def test_s3_mover_arquivo_para_local(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    name = create_file("arquivo.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="os").make(OTHER_DIR).getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .getFile(name)
        .moveTo(other_storage)
    )
    assert True == check


def test_s3_copiar_varios_arquivos_para_local(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    create_file("arquivo.txt")
    create_file("arquivo2.txt")
    create_file("arquivo3.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="os").make(OTHER_DIR).getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .getFile(ext="txt")
        .copyTo(other_storage)
    )
    assert True == check


def test_s3_mover_varios_arquivos_para_local(reset_s3_storage):
    STORAGE, DIR = getStorageAndDir()
    OTHER_STORAGE, OTHER_DIR = getOtherStorageAndDir()
    create_file("arquivo.txt")
    create_file("arquivo2.txt")
    create_file("arquivo3.txt")
    other_storage = (
        Storager(storage=OTHER_STORAGE, driver="os").make(OTHER_DIR).getDir(OTHER_DIR)
    )

    check = (
        Storager(storage=STORAGE, driver="s3", config=configS3())
        .getDir(DIR)
        .getFile(ext="txt")
        .moveTo(other_storage)
    )
    assert True == check
