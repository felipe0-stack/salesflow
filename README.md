# SalesFlow

Projeto de portfólio em Python para aprender a trabalhar com dados de vendas.
Nesta primeira entrega, o SalesFlow lê um CSV e mostra suas colunas, a quantidade
de linhas e uma prévia de até cinco linhas.

O programa lê todo o arquivo em memória. Validações de regras de negócio,
cálculos de vendas e relatórios ficam para próximas entregas.

## Preparar o ambiente no Windows

Execute os comandos no terminal PowerShell, a partir da pasta do projeto.
O ambiente desta entrega usa Python 3.12. Para criar a pasta `.venv`, caso ainda
não exista:

```powershell
py -3.12 -m venv .venv
```

Instale o projeto e as ferramentas de desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

O Pandas é a dependência usada para ler os dados. O extra `dev` adiciona pytest,
para executar os testes, e Ruff, para verificar o código e sua formatação.
A instalação editável (`-e`) permite alterar os arquivos em `src/` e executar
essas alterações sem reinstalar o projeto. Mudanças nas dependências do
`pyproject.toml` exigem executar a instalação novamente.

Um **ambiente virtual** é uma pasta com um interpretador Python e dependências
próprias para o projeto. Isso permite manter as bibliotecas do SalesFlow
separadas das usadas por outros projetos. A pasta `.venv` é local e não deve
entrar no Git.

Os comandos deste README usam o Python da `.venv` diretamente; não é necessário
ativar o ambiente. Se preferir a ativação e ela for permitida no seu PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Com o ambiente ativado, o comando de instalação equivalente é:

```powershell
pip install -e ".[dev]"
```

Se a ativação for bloqueada, continue usando o caminho completo do executável,
sem alterar a política de execução do PowerShell. No VS Code, abra a paleta de
comandos, escolha **Python: Select Interpreter** e selecione
`.venv\Scripts\python.exe`.

## Inspecionar as vendas

```powershell
.\.venv\Scripts\python.exe -m salesflow inspecionar --arquivo data/exemplo_vendas.csv
```

Com a `.venv` ativada, você também pode usar o comando solicitado para a entrega:

```powershell
python -m salesflow inspecionar --arquivo data/exemplo_vendas.csv
```

O arquivo de exemplo contém estas sete colunas:

```text
id_pedido, id_item, data, produto, categoria, quantidade, preco_unitario
```

O programa informa quatro linhas e exibe as quatro na prévia. São quatro itens
de venda; um mesmo pedido pode aparecer em mais de uma linha. A prévia é
limitada a cinco linhas, mesmo quando o arquivo tem mais registros.

`id_pedido` e `id_item` são lidos como texto. Assim, um identificador como
`001001` mantém os zeros iniciais. A leitura também preserva identificadores
literais como `NA`, sem convertê-los automaticamente em valores ausentes.
Se o caminho informado não existir, o programa mostra uma mensagem clara e
termina com código de erro.

## Como o programa funciona

Um **módulo** é um arquivo Python que pode conter funções e outros objetos.
Um **pacote** organiza módulos em uma pasta; neste projeto, o pacote é
`src/salesflow/`. O comando `python -m salesflow` executa o arquivo
`__main__.py` desse pacote.

O `__main__.py` chama a função principal em `cli.py`. Ela interpreta o
subcomando `inspecionar` e a opção `--arquivo`. A função `carregar_vendas` usa
`pandas.read_csv` para carregar o CSV e devolver um **DataFrame**.

Um DataFrame é uma tabela do Pandas, com linhas e colunas nomeadas. O programa
consulta `df.columns` para mostrar as colunas, `len(df)` para contar as linhas e
`df.head()` para obter as primeiras cinco. A leitura preserva os identificadores
como texto; os tipos das demais colunas são inferidos pelo Pandas.

## Arquivos do projeto

| Caminho | Para que serve |
| --- | --- |
| `pyproject.toml` | Define o pacote, a versão de Python, as dependências e as configurações das ferramentas. |
| `README.md` | Explica a instalação, o uso e os conceitos da primeira entrega. |
| `.gitignore` | Evita incluir o ambiente virtual e arquivos gerados no Git. |
| `src/salesflow/__init__.py` | Identifica a pasta como um pacote Python. |
| `src/salesflow/__main__.py` | Permite executar o pacote com `python -m salesflow`. |
| `src/salesflow/cli.py` | Interpreta os argumentos, lê o CSV e apresenta a inspeção. |
| `tests/test_cli.py` | Verifica o comportamento da leitura e do comando. |
| `data/exemplo_vendas.csv` | Contém os quatro itens de venda fornecidos para esta entrega. |
| `docs/PROGRESSO.md` | Registra entregas, comandos executados, resultados e pendências. |

## Verificar o projeto

Depois de instalar o extra `dev`, execute:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

O pytest executa os testes. O Ruff verifica problemas no código; o último
comando confere a formatação sem modificar arquivos. Os resultados das
verificações realizadas estão em [docs/PROGRESSO.md](docs/PROGRESSO.md).

Referências oficiais para continuar o estudo:
[leitura de CSV com Pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
e [configuração de um pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).
