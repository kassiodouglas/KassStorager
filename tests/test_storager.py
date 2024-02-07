import os
import pdb
import re
from pathlib import Path

from pytest import mark, raises

from kassstorager.Storager import Storager

STORAGE = "tests/storage"
OTHER_STORAGE = "tests/storage_other"
DIR = "test"


# auxiliar
def create_file(name):
    filepath = STORAGE + "/" + DIR + "/" + name
    Storager(STORAGE).make(DIR)
    with open(filepath, "w") as arquivo:
        arquivo.write("Este é um exemplo de conteúdo para o arquivo de texto.\n")
        arquivo.write("Você pode adicionar mais linhas conforme necessário.\n")
    return name


# tests
def test_criar_diretorio():

    Storager(STORAGE).make(DIR)

    path = os.path.join(STORAGE, DIR)
    assert True == os.path.exists(path)


def test_verificar_se_diretorio_existe():

    check = Storager(STORAGE).getDir(DIR).exists()
    assert True == check


def test_verificar_se_diretorio_nao_existe():
    path = Path(f"{STORAGE}/{DIR}--")
    message = f"Directory not exists"

    with raises(
        Exception,
        match=re.escape(message),
    ):
        Storager(STORAGE).getDir(DIR + "--").exists()


def test_deletar_um_diretorio_vazio():

    newdir = DIR + "/" + "new"
    Storager(STORAGE).make(newdir)
    check = Storager(STORAGE).getDir(newdir).delete()
    assert True == check


def test_deletar_um_diretorio_nao_vazio():

    with raises(
        OSError,
        match=re.escape("A pasta não está vazia"),
    ):
        dir = os.path.join(DIR, "123")
        Storager(STORAGE).make(dir)
        Storager(STORAGE).getDir(DIR).delete()


def test_deletar_um_diretorio_nao_vazio_forcado():

    dir = os.path.join(DIR, "123")
    Storager(STORAGE).make(dir)
    check = Storager(STORAGE).getDir(DIR).delete(force=True)
    assert True == check


def test_deletar_arquivo():

    name = create_file("arquivo.txt")
    check = Storager(STORAGE).getDir(DIR).deleteFile(name)
    assert True == check


def test_limpar_diretorio():
    create_file("arquivo.txt")
    create_file("arquivo2.txt")

    check = Storager(STORAGE).getDir(DIR).cleanDir()
    assert True == check


def test_copiar_arquivo_para_outro_storage():
    name = create_file("arquivo.txt")

    other_storage = Storager(OTHER_STORAGE)
    other_storage.make("other").getDir("other").deleteFile(name)

    check = (
        Storager(STORAGE)
        .getDir(DIR)
        .getFile(name)
        .copyTo(other_storage.getDir("other"))
    )

    assert True == check


def test_mover_arquivo_para_outro_storage():
    name = "arquivo.txt"

    other_storage = Storager(OTHER_STORAGE)
    other_storage.make("other").getDir("other").deleteFile(name)

    check = (
        Storager(STORAGE)
        .getDir(DIR)
        .getFile(name)
        .moveTo(other_storage.getDir("other"))
    )

    assert True == check
