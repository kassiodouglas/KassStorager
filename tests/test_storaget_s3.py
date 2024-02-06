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
    "bucket": "dados-servicos-clientes",
    "access_key": "AKIAZL7QYCDCNNHOMANV",
    "secret_key": "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",
}


def conn():
    return (
        boto3.client(
            "s3",
            aws_access_key_id=configs3["access_key"],
            aws_secret_access_key=configs3["secret_key"],
        ),
        configs3["bucket"],
    )


def test_criar_diretorio():
    Storager(storage=STORAGE, driver="s3", config=configs3).make(DIR)

    client, bucket = conn()
    response = client.list_objects_v2(Bucket=bucket, Prefix=f"{STORAGE}/{DIR}/")
    assert True == (True if "Contents" in response else False)
