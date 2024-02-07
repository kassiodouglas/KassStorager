import os
import pdb
import re
from pathlib import Path

import boto3
from pytest import mark, raises

from kassstorager.Storager import Storager

STORAGE = "STORAGER"
OTHER_STORAGE = "tests/storage_other"
DIR = "test"


configs3 = {
    "bucket": os.environ.get("AWSS3_BUCKET"),
    "access_key": os.environ.get("AWSS3_ACCESS_KEY"),
    "secret_key": os.environ.get("AWSS3_SECRET_KEY"),
}


# auxiliar
def conn():
    return (
        boto3.client(
            "s3",
            aws_access_key_id=configs3["access_key"],
            aws_secret_access_key=configs3["secret_key"],
        ),
        configs3["bucket"],
    )


# tests
def test_criar_diretorio():
    Storager(storage=STORAGE, driver="s3", config=configs3).make(DIR)

    client, bucket = conn()
    response = client.list_objects_v2(Bucket=bucket, Prefix=f"{STORAGE}/{DIR}/")
    assert True == (True if "Contents" in response else False)


def test_verificar_se_diretorio_existe():

    check = Storager(storage=STORAGE, driver="s3", config=configs3).getDir(DIR).exists()
    assert True == check


def test_verificar_se_diretorio_nao_existe():
    path = f"{STORAGE}/{DIR}--"
    message = f"Directory not exists"

    with raises(
        Exception,
        match=re.escape(message),
    ):
        Storager(storage=STORAGE, driver="s3", config=configs3).getDir(
            DIR + "--"
        ).exists()


# sem permissao
# def test_deletar_um_diretorio_vazio():

#     newdir = DIR + "/" + "new"
#     storage = Storager(storage=STORAGE, driver="s3", config=configs3)
#     storage.make(newdir)
#     check = storage.getDir(newdir).delete()
#     assert True == check


# def test_deletar_um_diretorio_nao_vazio():

#     with raises(
#         OSError,
#         match=re.escape("A pasta não está vazia"),
#     ):
#         dir = os.path.join(DIR, "123")
#         Storager(STORAGE).make(dir)
#         Storager(STORAGE).getDir(DIR).delete()


# def test_deletar_um_diretorio_nao_vazio_forcado():

#     dir = os.path.join(DIR, "123")
#     Storager(STORAGE).make(dir)
#     check = Storager(STORAGE).getDir(DIR).delete(force=True)
#     assert True == check


# def test_deletar_arquivo():

#     name = create_file("arquivo.txt")
#     check = Storager(STORAGE).getDir(DIR).deleteFile(name)
#     assert True == check


# def test_limpar_diretorio():
#     create_file("arquivo.txt")
#     create_file("arquivo2.txt")

#     check = Storager(STORAGE).getDir(DIR).cleanDir()
#     assert True == check


# def test_copiar_arquivo_para_outro_storage():
#     name = create_file("arquivo.txt")

#     other_storage = Storager(OTHER_STORAGE)
#     other_storage.make("other").getDir("other").deleteFile(name)

#     check = (
#         Storager(STORAGE)
#         .getDir(DIR)
#         .getFile(name)
#         .copyTo(other_storage.getDir("other"))
#     )

#     assert True == check


# def test_mover_arquivo_para_outro_storage():
#     name = "arquivo.txt"

#     other_storage = Storager(OTHER_STORAGE)
#     other_storage.make("other").getDir("other").deleteFile(name)

#     check = (
#         Storager(STORAGE)
#         .getDir(DIR)
#         .getFile(name)
#         .moveTo(other_storage.getDir("other"))
#     )

#     assert True == check
