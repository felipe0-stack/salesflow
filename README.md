# SalesFlow

Projeto de portfólio em Python para aprender a trabalhar com dados de vendas.
O SalesFlow inspeciona arquivos CSV e valida a qualidade dos registros,
identificando dados inválidos, repetições e conflitos de chave.

O programa lê todo o arquivo em memória. A etapa 1 oferece a inspeção e a
etapa 2 acrescenta a validação e os relatórios de qualidade em CSV e JSON.
Cálculos de faturamento e outros relatórios de negócio ficam para próximas
entregas.

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
subcomando `inspecionar` ou `validar` e suas opções. A função `carregar_vendas`,
em `leitura.py`, usa `pandas.read_csv` para carregar o CSV e devolver um
**DataFrame**.

Um DataFrame é uma tabela do Pandas, com linhas e colunas nomeadas. O programa
consulta `df.columns` para mostrar as colunas, `len(df)` para contar as linhas e
`df.head()` para obter as primeiras cinco. A leitura preserva os identificadores
como texto. No comando `inspecionar`, os tipos das demais colunas são inferidos
pelo Pandas, preservando o comportamento da etapa 1.

No comando `validar`, a mesma função de leitura recebe `como_texto=True` para
preservar a escrita original de todos os campos. Assim, um preço escrito como
`10.999` ou `1e2` não pode perder seu formato antes da validação.

A função `validar_vendas`, em `validacao.py`, recebe o DataFrame e devolve
tabelas e contagens sem ler arquivos, imprimir ou gravar relatórios. Primeiro
valida os campos; depois resolve as duplicidades entre registros com conteúdo
válido. A função `salvar_relatorios`, em `relatorios.py`, grava os resultados.
A interface em `cli.py` coordena essas funções.

## Validar a qualidade das vendas

Na raiz do projeto, execute:

```powershell
.\.venv\Scripts\python.exe -m salesflow validar --arquivo data/exemplo_com_erros.csv --saida relatorios/
```

Com a `.venv` ativada, o comando equivalente é:

```powershell
python -m salesflow validar --arquivo data/exemplo_com_erros.csv --saida relatorios/
```

A pasta de saída é criada automaticamente. Nela ficam:

| Arquivo | Conteúdo |
| --- | --- |
| `relatorios/validos.csv` | Registros aceitos, com quantidade inteira, preço padronizado e a coluna inteira `preco_unitario_centavos`. |
| `relatorios/rejeitados.csv` | Registros inválidos, duplicados ignorados e conflitantes, com arquivo e posição de origem, classificação e motivo. |
| `relatorios/resumo.json` | Contagens por categoria, arquivo de origem e lista de colunas obrigatórias ausentes. |

O exemplo controlado tem 11 registros: 3 válidos, 5 inválidos, 1 duplicado
ignorado e 2 conflitantes. Os quatro registros de `data/exemplo_vendas.csv`
atendem às regras e têm chaves distintas. Você pode validar esse arquivo
indicando outra pasta, como `--saida relatorios/original/`.

Os identificadores continuam sendo texto: o item `01` não vira `1`. O preço
usa ponto quando há parte decimal e até duas casas; sua conversão para centavos
é feita com inteiros, sem `float`. Por exemplo, `0.29` resulta exatamente em
`29` centavos. Preços inteiros, como `10`, também são aceitos.

Cada registro entra em exatamente uma categoria:

```text
lidas = validas + invalidas + duplicadas_ignoradas + conflitantes
```

As regras completas, a prioridade entre as classificações e a definição da
origem estão em [docs/REGRAS.md](docs/REGRAS.md).

Os relatórios usam nomes fixos: repetir o comando na mesma pasta substitui os
três arquivos gerados. O programa impede que um desses caminhos sobrescreva
o próprio CSV de entrada. Código de saída `0` significa que os relatórios foram
gerados, mesmo quando contêm rejeições; `1` indica erro de leitura ou gravação,
e `2` indica argumentos incorretos.

## Arquivos do projeto

| Caminho | Para que serve |
| --- | --- |
| `pyproject.toml` | Define o pacote, a versão de Python, as dependências e as configurações das ferramentas. |
| `README.md` | Explica a instalação, o uso e os conceitos das etapas implementadas. |
| `.gitignore` | Evita incluir o ambiente virtual e arquivos gerados no Git. |
| `src/salesflow/__init__.py` | Identifica a pasta como um pacote Python. |
| `src/salesflow/__main__.py` | Permite executar o pacote com `python -m salesflow`. |
| `src/salesflow/cli.py` | Interpreta os argumentos e coordena os comandos de inspeção e validação. |
| `src/salesflow/leitura.py` | Compartilha a leitura do CSV entre os dois comandos. |
| `src/salesflow/validacao.py` | Valida os campos, converte preços e classifica duplicidades. |
| `src/salesflow/relatorios.py` | Grava os CSVs e o resumo JSON da validação. |
| `tests/` | Verifica leitura, regras, duplicidades, relatórios e execução pelo terminal. |
| `data/exemplo_vendas.csv` | Contém os quatro itens de venda fornecidos para esta entrega. |
| `data/exemplo_com_erros.csv` | Reúne casos controlados de erros, repetição e conflito. |
| `docs/REGRAS.md` | Define os formatos aceitos, as classificações e os relatórios. |
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
