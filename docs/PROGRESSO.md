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

## Etapa 2 — Validação e qualidade dos dados — 11/11/2026

### Entregas

- [x] Ler o README e este histórico e procurar instruções `AGENTS.md` na pasta
  e nos ancestrais; nenhuma instrução adicional foi encontrada.
- [x] Preservar o comando `inspecionar` e os sete testes originais da etapa 1.
- [x] Reutilizar `carregar_vendas`, agora em `leitura.py`, com a opção
  `como_texto=True` para a validação. O modo padrão mantém a inferência usada
  pela inspeção; o import antigo por `salesflow.cli` continua funcionando.
- [x] Implementar `validar --arquivo ... --saida ...`.
- [x] Separar as regras em `validacao.py`, sem acesso a arquivos ou ao terminal.
- [x] Validar as sete colunas, preenchimento, datas reais, quantidade inteira
  positiva e preço positivo com formato decimal controlado.
- [x] Converter preços diretamente do texto para centavos inteiros exatos.
- [x] Classificar duplicidades por `(id_pedido, id_item)` após validar os campos.
- [x] Manter inválidos, duplicados ignorados e conflitantes em categorias exclusivas,
  com todos os motivos de um registro inválido reunidos numa ocorrência.
- [x] Separar a escrita em `relatorios.py`: `validos.csv`, `rejeitados.csv`
  e `resumo.json`, criando a pasta de saída automaticamente.
- [x] Incluir arquivo e posição de origem, classificação e motivo nos rejeitados.
- [x] Adicionar `data/exemplo_com_erros.csv` com casos controlados.
- [x] Documentar as regras em [REGRAS.md](REGRAS.md) e atualizar o README.
- [x] Acrescentar testes unitários e de integração e executá-los.
- [x] Conferir que os quatro registros originais continuam válidos.
- [x] Ignorar `/relatorios/` no Git, mantendo os arquivos gerados disponíveis localmente.

### Organização e decisões

`carregar_vendas` é a única função de leitura. No comando `validar`, todos os
campos são preservados como texto: isso permite rejeitar `10.000` ou `1e2` antes
que uma inferência numérica esconda a escrita original. Não houve mudança de
dependências nem necessidade de reinstalar o projeto em modo editável.

`converter_preco_centavos` valida o formato, separa a parte inteira da fração,
completa a fração até duas casas e calcula `inteiros * 100 + fração`, sem `float`.
Preços inteiros também são aceitos; quando há parte decimal, o separador deve
ser ponto. Não são aceitos sinais, vírgulas, expoentes ou mais de duas casas.

`validar_vendas` primeiro verifica o esquema e todos os campos de cada registro.
Somente os registros com conteúdo válido são agrupados por chave. Conteúdos
normalizados idênticos aceitam a primeira ocorrência e ignoram as demais;
conteúdos válidos divergentes tornam todas as ocorrências válidas daquela chave
conflitantes, inclusive repetições de um deles. Inválidos não mudam de categoria.
Quantidades e preços são normalizados na comparação; identificadores, produtos
e categorias mantêm seu texto. Os detalhes estão em `REGRAS.md`.

`ResultadoValidacao` reúne as tabelas, as contagens e as colunas ausentes.
`salvar_relatorios` escreve esse resultado; `main` coordena as chamadas e mostra
um resumo no terminal. O DataFrame de entrada não é alterado pela validação.

O campo `linha_origem` é a posição ordinal entre os registros CSV lidos,
considerando o cabeçalho como 1, e não necessariamente uma linha física do arquivo.
Ausência de coluna obrigatória torna todos os registros existentes inválidos e
é informada no JSON, inclusive quando não há registros. CSVs de saída vazios
mantêm seus cabeçalhos.

### Comandos executados e verificações

O estado inicial desta etapa estava limpo, na branch `main` acompanhando
`origin/main`, com o commit `d7fce4c` da estrutura inicial já existente.
O Python da `.venv` continuou sendo o 3.12.10. Nenhum commit, push ou alteração
na configuração do Git foi realizado nesta etapa.

| Comando | Resultado |
| --- | --- |
| `git status --short --branch` | Estado inicial limpo, `main...origin/main`. |
| `git log -1 --oneline` | `d7fce4c Adiciona estrutura inicial do projeto SalesFlow com leitura de CSV e CLI`. |
| `.\.venv\Scripts\python.exe --version` | Python 3.12.10. |
| `.\.venv\Scripts\python.exe -m pytest` | 89 testes aprovados em 12,45 segundos, incluindo os sete originais e os dois novos casos de CSV com campos excedentes. |
| `.\.venv\Scripts\python.exe -m ruff check .` | `All checks passed!` após os ajustes de imports e formatação. |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | 12 arquivos já formatados. |
| `git diff --check` | Sem erros de whitespace; apenas avisos da configuração existente de conversão LF/CRLF. |
| `.\.venv\Scripts\python.exe -X utf8 -m salesflow validar --arquivo data/exemplo_com_erros.csv --saida relatorios/` | Código 0, três relatórios gerados, contagem `11 = 3 + 5 + 1 + 2`. |
| `.\.venv\Scripts\python.exe -m salesflow validar --arquivo data/exemplo_com_erros.csv --saida relatorios/` | Repetição final sem a opção UTF-8: código 0 e as mesmas contagens e relatórios. |
| `.\.venv\Scripts\python.exe -X utf8 -m salesflow validar --arquivo data/exemplo_vendas.csv --saida relatorios/original/` | Código 0, quatro válidos e nenhuma rejeição ou ocorrência ignorada. |

A opção `-X utf8` nas verificações manuais garante a captura dos acentos pelo
terminal da ferramenta. O comando também foi executado sem essa opção,
com o mesmo resultado, como documentado no README.

Os testes cobrem preenchimento, colunas ausentes, datas impossíveis e anos
bissextos, formatos numéricos inválidos, zeros à esquerda, centavos exatos acima
de 64 bits, contagem exclusiva, vários erros na mesma linha, duplicatas
idênticas, sequência conflitante `A, A, B`, inválidos na mesma chave de válidos,
índice do DataFrame repetido, preservação da entrada e execução real do módulo.
Também verificam relatórios vazios, origem e motivos, arquivo inexistente,
CSV vazio ou com aspas malformadas, argumentos ausentes e falhas de saída,
incluindo impedir que os relatórios sobrescrevam a própria entrada.

A revisão final identificou que o Pandas poderia inferir um índice e descartar
o primeiro campo de registros com campos excedentes. No modo de validação,
`index_col=False` e a promoção de `ParserWarning` a erro impedem essa perda
silenciosa. Foram acrescentados dois casos de regressão, com campo excedente
no primeiro registro e em um registro posterior. A leitura é interrompida
sem gerar relatórios nesses casos.

### Relatórios conferidos

| Entrada | Lidas | Válidas | Inválidas | Duplicadas ignoradas | Conflitantes |
| --- | ---: | ---: | ---: | ---: | ---: |
| `data/exemplo_com_erros.csv` | 11 | 3 | 5 | 1 | 2 |
| `data/exemplo_vendas.csv` | 4 | 4 | 0 | 0 | 0 |

Os três arquivos do exemplo com erros estão em `relatorios/`. Os do exemplo
original estão em `relatorios/original/`. Os CSVs e o JSON foram abertos e
conferidos: identificadores como `01` permanecem escritos dessa forma,
`0.29` gerou `29` centavos e o preço inválido `10.999` permaneceu no rejeitado
com seu conteúdo original e motivo. Uma nova execução substitui os três
relatórios da mesma pasta; o CSV de entrada é protegido contra essa substituição.

### Pendências e limites atuais

- Nenhuma pendência técnica identificada nas verificações desta etapa.
- As alterações permanecem locais para revisão; commit e push não foram realizados.
- Código de saída 0 significa que os relatórios foram gerados, mesmo contendo
  rejeições. As contagens e `colunas_ausentes` no JSON informam a qualidade.
- O CSV continua sendo lido integralmente em memória, em UTF-8 e separado por vírgula.
- Não há correção automática de valores, cálculos de faturamento, interface web
  ou integração contínua nesta etapa.
