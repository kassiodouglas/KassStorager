# KassStorager

## Instalação
```
pip install KassStorager
```

## Suporte
Ha suporte para uso local e para uso com Aws S3.

## Como usar?

#### Diretórios
Criar um diretório em um storage especifico. Ex: "./storage_root".
```
from KassStorager import Storager

Storager('storage_root').make('src')
# ira criar um diretorio '/src' em '/storage_root'
```


Selecionar um diretorio dentro do storage.
```
from KassStorager import Storager

Storager('storage_root').getDir('src')
```

Para verificar se  um diretorio existe.
```
from KassStorager import Storager

result = Storager('storage_root').getDir('src').exists()
# result = False ou True
```

Para excluir um diretorio.
```
from KassStorager import Storager

Storager('storage_root').getDir('src').delete()
```

Caso o diretório não esteja vazio, e mesmo assim ainda queira forçar, passe o parametro 'force';
```
from KassStorager import Storager

Storager('storage_root').getDir('src').delete(force=True)
```

Limpar um diretório mantendo ele.
```
from KassStorager import Storager

Storager('storage_root').getDir('src').cleanDir()
```


<br>
<br>

#### Arquivos
Deletar um arquivo especifico de um diretorio
```
from KassStorager import Storager

Storager('storage_root').getDir('src').deleteFile('arquivo.txt')
```


Copiar todos os arquivos de um diretório para outro. Ex: "./storage_root/src" => "./storage_root_2".
```
from KassStorager import Storager

storage2 = Storager('storage_root_2').getDir()

Storager('storage_root').getDir('src').getFile(ext="*").copyTo(storage2)

```

Copiar somente um tipo de arquivo de um diretório para outro. Ex: "./storage_root/src" => "./storage_root_2".
```
from KassStorager import Storager

storage2 = Storager('storage_root_2').getDir()

Storager('storage_root').getDir('src').getFile(ext="csv").copyTo(storage2)
```

Copiar somente os arquivos com nome que atendam  todos os filtros informados de um diretório para outro. Ex: "./storage_root/src" => "./storage_root_2".
```
from KassStorager import Storager

storage2 = Storager('storage_root_2').getDir()

Storager('storage_root').getDir('src').getFile(filters=["01-02","2024","file"]).copyTo(storage2)
```

Para mover arquivos utilize o metodo 'moveTo' no lugar de 'copyTo'.
```
from KassStorager import Storager

storage2 = Storager('storage_root_2').getDir()

Storager('storage_root').getDir('src').getFile(ext="csv", filters=["01-02","2024","file"]).moveTo(storage2)
```


## Como usar? (S3)

Para uso com AWS S3, basta informar na criação do storage os dados de conexao com bucket e o driver 's3', como abaixo.
```
from KassStorager import Storager

conns3 =  {
    "bucket": 'seu_bucket',
    "access_key": 'sua_chave_de_acesso'
    "secret_key": 'sua_senha',
}

driver = 's3'

storage = 'dir_no_s3'

Storager(storage=storage, driver=driver, config=conns3)
```

Demais métodos de manipulação de diretórios e arquivos seguem como dito na sessão [Como usar?](#como-usar?)


<br>
<br>

## Envio 'LOCAL' para 'S3' e 'S3' para 'LOCAL'

Pasta informar o storage local e o de destino.

```
from KassStorager import Storager

# conexão com S3
conns3 =  {
    "bucket": 'seu_bucket',
    "access_key": 'sua_chave_de_acesso'
    "secret_key": 'sua_senha',
}
driver = 's3'
storagerS3 = 'dir_no_s3'
```

Envio local para S3:
```
storageS3 = Storager(storage=storage, driver=driver, config=conns3).get_dir()

Storager('storage_root').getDir('src').getFile(filters=["01-02","2024","file"]).copyTo(storageS3)
```

E ao contrario:
```
storageLocal = Storager('storage_root').get_dir()

Storager(storage=storagerS3, driver=driver, config=conns3).getDir().getFile(ext="*").copyTo(storageLocal)
```