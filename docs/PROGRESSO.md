# Progresso do SalesFlow

## Primeira entrega — 11/11/2026

### Escopo e entregas

- [x] Conferir o Python e o Git antes de criar os arquivos.
- [x] Verificar a vinculação com `https://github.com/felipe0-stack/salesflow`.
- [x] Criar `pyproject.toml`, `README.md`, `.gitignore`, `src/salesflow/`,
  `tests/`, `data/` e este registro.
- [x] Declarar Pandas como dependência e pytest e Ruff no extra `dev`.
- [x] Adicionar `data/exemplo_vendas.csv` com o conteúdo solicitado.
- [x] Implementar `python -m salesflow inspecionar --arquivo ...`.
- [x] Mostrar colunas, quantidade de linhas e prévia de até cinco linhas.
- [x] Preservar `id_pedido` e `id_item` como texto.
- [x] Informar arquivo inexistente em mensagem clara, sem traceback,
  com código de saída 1.
- [x] Criar a `.venv` usando Python 3.12.10.
- [x] Instalar o projeto em modo editável com o extra `dev`.
- [x] Validar o comando, os testes, o Ruff e as dependências instaladas.
- [x] Documentar instalação, uso e conceitos no README.

### Situação inicial e Git

A pasta continha apenas `.git`, sem arquivos de projeto ou commits na branch
`main`. O Git instalado é o 2.50.1.windows.1. O remoto `origin` já estava
configurado corretamente para
`https://github.com/felipe0-stack/salesflow.git`, tanto para fetch quanto push.
Não foi necessário inicializar outro repositório nem alterar essa vinculação.

`git ls-remote --heads --tags origin` terminou com código 0 e não retornou
branches ou tags. O status `main...origin/main [gone]` corresponde à configuração
local que já aponta para uma branch remota ainda não anunciada. Isso não indica
que a URL do remoto esteja incorreta.

Os arquivos e o histórico existentes foram preservados. Nenhum commit ou push
foi realizado. As alterações permanecem locais para revisão.

### Ambiente e funcionamento

Os comandos padrão `python` e `py` apontam para atalhos do WindowsApps e,
quando executados fora da restrição inicial do ambiente, informaram Python
3.15.2. Também foi encontrado o Python 3.12.10 instalado em
`C:\Users\Felipe\AppData\Local\Python\pythoncore-3.12-64\python.exe`.
Essa instalação foi usada explicitamente para criar a `.venv`, sem alterar o
Python padrão do computador. O projeto declara Python 3.12 ou superior;
a validação desta entrega usa somente a versão 3.12.10.

`__main__.py` encaminha a execução para `main()` em `cli.py`. O `argparse`
interpreta o subcomando e o caminho; `carregar_vendas()` lê o CSV em um
DataFrame. O programa usa as colunas, o tamanho e as primeiras cinco linhas
dessa tabela para montar a saída.

A leitura usa `dtype` explícito para os identificadores e
`keep_default_na=False`, preservando zeros à esquerda e valores literais como
`NA` e `NULL`. Essa opção também mantém campos vazios como texto vazio, em vez
de convertê-los automaticamente em valores ausentes. As demais colunas têm
tipos inferidos pelo Pandas. Não há conversão de datas ou regras de negócio.

### Comandos executados e resultados

Todos os caminhos relativos abaixo partem da raiz do projeto. Quando houve
bloqueio de rede ou dos atalhos do WindowsApps, a tentativa foi repetida pelo
fluxo de autorização do ambiente.

| Comando | Resultado |
| --- | --- |
| `git --version` | `git version 2.50.1.windows.1`. |
| `git status --short --branch` | Branch `main`, ainda sem commits; inicialmente sem arquivos de projeto. |
| `git remote -v` | `origin` aponta para o repositório informado, em fetch e push. |
| `git log -5 --oneline` | Git informou que `main` ainda não possui commits. |
| `git config --local --list` | Confirmou a URL do remoto e o acompanhamento de `origin/main`. |
| `git ls-remote --heads --tags origin` | Consulta bem-sucedida, sem branches ou tags anunciadas. A primeira tentativa teve bloqueio de rede. |
| `python --version` e `py --version` | Python 3.15.2 fora da restrição inicial; os atalhos ficaram inacessíveis na primeira tentativa. |
| `& 'C:\Users\Felipe\AppData\Local\Python\pythoncore-3.12-64\python.exe' --version` | Python 3.12.10. |
| `& 'C:\Users\Felipe\AppData\Local\Python\pythoncore-3.12-64\python.exe' -m pip --version` | pip 25.0.1 para Python 3.12. |
| `& 'C:\Users\Felipe\AppData\Local\Python\pythoncore-3.12-64\python.exe' -m venv .venv` | Ambiente virtual criado com sucesso. |
| `.\.venv\Scripts\python.exe --version` | Python 3.12.10. |
| `.\.venv\Scripts\python.exe -m pip install -e ".[dev]" --retries 0 --timeout 20 --disable-pip-version-check` | Instalação editável concluída após a repetição autorizada com acesso à rede. SalesFlow 0.1.0, Pandas 3.1.1, pytest 9.2.0 e Ruff 0.17.4. |
| `git check-ignore .venv .venv/Scripts/python.exe` | Confirmou que o ambiente virtual está ignorado pelo Git. |
| `.\.venv\Scripts\python.exe -m pip list --disable-pip-version-check` | Confirmou as versões e a instalação editável apontando para esta pasta. |
| `.\.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| `.\.venv\Scripts\python.exe -m salesflow inspecionar --arquivo data/exemplo_vendas.csv` | Código 0; sete colunas, quatro linhas e a prévia dos quatro itens. |
| `.\.venv\Scripts\python.exe -X utf8 -m salesflow inspecionar --arquivo data/exemplo_vendas.csv` | Mesmo resultado, com saída UTF-8 para capturar os acentos no terminal da verificação. |
| `.\.venv\Scripts\python.exe -X utf8 -m salesflow inspecionar --arquivo data/arquivo_inexistente.csv` | Código 1 e mensagem `Erro: arquivo não encontrado: data\arquivo_inexistente.csv`, sem traceback. |
| `.\.venv\Scripts\python.exe -m pytest` | Sete testes aprovados em 4,22 segundos. |
| `.\.venv\Scripts\python.exe -m ruff check .` | `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | Seis arquivos já formatados. A primeira execução concorrente avisou sobre escrita no cache; a repetição isolada passou sem avisos. |
| `git diff --check` | Nenhum erro reportado nas alterações rastreadas; os arquivos desta entrega ainda são novos e não foram adicionados ao índice. |

### Verificações

A instalação e todas as verificações desta entrega foram concluídas com
sucesso. Os sete casos de teste cobrem o CSV fornecido, identificadores com
zeros à esquerda e valores `NA`/`NULL`, execução real do módulo, limite da
prévia, contagem de todas as linhas, arquivo inexistente e argumentos
obrigatórios. Não é usado `pythonpath=src`: os testes dependem da instalação
correta do pacote.

Saída do arquivo de exemplo:

```text
Colunas: id_pedido, id_item, data, produto, categoria, quantidade, preco_unitario
Quantidade de linhas: 4
Prévia dos dados (até 5 linhas):
id_pedido id_item       data produto   categoria  quantidade  preco_unitario
     1001       1 2026-10-01   Mouse Perifericos           2            50.0
     1001       2 2026-10-01 Teclado Perifericos           1           100.0
     1002       1 2026-10-02 Monitor   Monitores           1           300.0
     1003       1 2026-10-03   Mouse Perifericos           2            50.0
```

### Pendências e limites

- Nenhuma pendência técnica da primeira entrega identificada nas verificações.
- Revisão das alterações locais pelo responsável pelo projeto.
- Primeiro commit e push ficam para uma decisão posterior do responsável.
- O CSV é lido integralmente em memória; não há processamento em blocos.
- Arquivos devem usar vírgula como separador e codificação UTF-8.
- Validações comerciais, tratamento geral de CSV inválido, cálculos, relatórios,
  interface web e automação de integração contínua não fazem parte desta entrega.

Veja no [README](../README.md) as instruções de uso e as explicações de ambiente
virtual, módulo, pacote, instalação editável e DataFrame.
