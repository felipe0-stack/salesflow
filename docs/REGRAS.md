# Regras de validação e qualidade dos dados

## Entrada e leitura compartilhada

Os comandos recebem um CSV UTF-8, separado por vírgula e com cabeçalho.
As sete colunas abaixo são obrigatórias, com esses nomes exatos. A ordem de
entrada pode variar. Colunas extras são aceitas, mas não participam da validação
nem da comparação de duplicidades e não são copiadas para os relatórios.

`carregar_vendas`, em `leitura.py`, é reutilizada pelos dois comandos:

- `inspecionar` mantém a inferência de tipos da etapa 1, exceto nos
  identificadores, que são lidos como texto.
- `validar` usa `como_texto=True`: todos os campos são lidos como texto para
  preservar zeros, casas decimais e a escrita original antes das regras.

`keep_default_na=False` preserva textos como `NA` e `NULL`, em vez de convertê-los
automaticamente em valores ausentes. Campos vazios continuam vazios e são
avaliados pelas regras. A leitura do Pandas ignora linhas físicas em branco
fora de campos CSV entre aspas.
O arquivo inteiro é carregado em memória; não há processamento em blocos.
Na validação, uma quantidade excedente de campos em relação ao cabeçalho
interrompe a leitura, sem gerar relatórios. O leitor impede a inferência de um
índice ou o descarte silencioso desses campos. Registros com campos a menos
são avaliados pelas regras de preenchimento dos campos faltantes.

## Sete colunas obrigatórias e formatos

| Coluna | Regra |
| --- | --- |
| `id_pedido` | Texto preenchido. Zeros à esquerda são preservados. |
| `id_item` | Texto preenchido. Zeros à esquerda são preservados. |
| `data` | Data real do calendário, exatamente no formato `AAAA-MM-DD`, com dígitos ASCII. |
| `produto` | Texto preenchido. |
| `categoria` | Texto preenchido. |
| `quantidade` | Apenas dígitos ASCII de `0` a `9`, representando um inteiro maior que zero. |
| `preco_unitario` | Apenas dígitos ASCII, com parte decimal opcional separada por ponto e composta por uma ou duas casas; valor maior que zero. |

Nos identificadores, produto e categoria, um texto vazio ou formado somente
por espaços é inválido. Valores ausentes em um DataFrame recebido diretamente
pela função de validação também são tratados como vazios. Textos preenchidos
não são aparados, convertidos para minúsculas ou modificados: `Mouse`, `mouse`
e ` Mouse ` permanecem conteúdos distintos. Identificadores `01` e `1`
também são chaves distintas.

Datas exigem quatro dígitos para o ano e dois para mês e dia, além de existir
no calendário. `2024-02-29` é aceita; `2026-02-29`, `2026-02-30`, `2026-2-01`,
`01/10/2026`, ano `0000` e datas com horário são rejeitados. Não é aplicada uma
restrição adicional de intervalo comercial ou de data futura.

Quantidades como `1`, `2` e `001` são aceitas e convertidas em inteiros.
`0`, `-1`, `+1`, `1.0`, `1e2`, vírgulas, espaços e dígitos de outros alfabetos
são rejeitados.

Preços aceitos incluem `10`, `10.5`, `10.50`, `00.29` e `0.01`. Os zeros
à esquerda não alteram o valor. São rejeitados:

- Zero em qualquer dessas representações: `0`, `0.0` ou `0.00`.
- Sinais: `-1.00` e `+1.00`.
- Vírgula decimal ou separador de milhar: `10,50` e `1.000,00`.
- Mais de duas casas decimais: `10.001` e `10.000`, mesmo com zeros finais.
- Ponto sem uma das partes exigidas: `.50` e `10.`.
- Notação científica, valores especiais e espaços: `1e2`, `NaN`, `inf`,
  ` 10.00 ` e texto vazio.

Os formatos numéricos são estritos: o programa não corrige ou arredonda
representações rejeitadas.

## Conversão exata para centavos

`converter_preco_centavos` verifica primeiro a escrita do preço. Em seguida,
separa o texto no ponto, completa a fração com zero à direita até duas casas
e calcula com inteiros:

```text
centavos = parte_inteira * 100 + parte_fracionaria
```

Exemplos:

| Entrada | Cálculo | Centavos |
| --- | --- | --- |
| `0.29` | `0 * 100 + 29` | `29` |
| `10.5` | `10 * 100 + 50` | `1050` |
| `10` | `10 * 100 + 0` | `1000` |

Não há conversão por `float`, multiplicação de ponto flutuante, arredondamento
ou truncamento. Os centavos são inteiros Python, inclusive para valores acima
do intervalo de inteiros de 64 bits. A validação recebe preferencialmente os
dados ainda em texto: não é possível recuperar precisão ou casas que já tenham
sido perdidas por uma conversão anterior feita fora do programa.

## Ordem da validação e duplicidades

`validar_vendas` recebe um DataFrame e devolve `ResultadoValidacao`, contendo
as tabelas de válidos e rejeitados, as contagens e as colunas ausentes. A função
não lê ou grava arquivos, não imprime e não modifica o DataFrame recebido.

Primeiro são verificadas as colunas. Se faltar qualquer coluna obrigatória,
todos os registros existentes são classificados como `invalida`, com a lista
de colunas ausentes no motivo. Não são aplicadas as regras de conteúdo ou de
duplicidade nesses registros. A lista também aparece em `resumo.json`, mesmo
se o arquivo tiver cabeçalho, nenhuma linha de dados e colunas faltantes.

Com as sete colunas presentes, cada registro passa pelas regras de todos os
campos. Um registro com vários problemas aparece uma única vez nos rejeitados,
com todos os motivos encontrados separados por `; `.

Só os registros com conteúdo válido participam da análise de duplicidades.
A chave de cada item é o par exato `(id_pedido, id_item)`. Itens diferentes do
mesmo pedido são registros distintos. Para cada chave:

1. Com apenas um conteúdo válido distinto, a primeira ocorrência é aceita.
   As demais são `duplicada_ignorada` e seu motivo aponta a posição do
   registro aceito.
2. Com dois ou mais conteúdos válidos distintos, todas as ocorrências válidas
   dessa chave são `conflitante`. Isso inclui repetições idênticas de um dos
   conteúdos: uma sequência `A, A, B` gera três conflitantes.
3. Registros com conteúdo inválido continuam `invalida`, mesmo quando
   compartilham a chave com registros válidos ou conflitantes. Eles não criam
   conflitos nem impedem a aceitação de uma ocorrência válida.

O conteúdo comparado reúne somente as sete colunas obrigatórias. Quantidade
e preço são comparados após normalização: quantidades `01` e `1` são iguais;
preços `10`, `10.0` e `10.00` são iguais. Datas, identificadores, produto e
categoria mantêm seu texto, incluindo diferenças de espaços e de maiúsculas.

## Relatórios e origem

`salvar_relatorios` cria a pasta informada em `--saida` e grava três arquivos
UTF-8. Os CSVs usam vírgula e são gerados sem o índice do DataFrame, inclusive
quando não há registros: nesse caso, os cabeçalhos são mantidos.

- `validos.csv`: as sete colunas obrigatórias, com quantidade inteira e preço
  padronizado com duas casas, mais `preco_unitario_centavos` inteiro exato.
  Os identificadores continuam texto e preservam os zeros à esquerda no CSV.
- `rejeitados.csv`: `arquivo_origem`, as sete colunas com seus valores originais,
  `linha_origem`, `classificacao` e `motivo`. Colunas inexistentes na entrada
  são representadas por campos vazios. As classificações possíveis são
  `invalida`, `duplicada_ignorada` e `conflitante`.
- `resumo.json`: `arquivo_origem`, as contagens `lidas`, `validas`, `invalidas`,
  `duplicadas_ignoradas`, `conflitantes` e a lista `colunas_ausentes`.

`arquivo_origem` é o caminho fornecido ao comando. `linha_origem` é o ordinal
do registro lido, com cabeçalho considerado como posição 1 e primeiro registro
como posição 2. Esse ordinal não é necessariamente a linha física do arquivo:
linhas em branco são ignoradas pela leitura e campos CSV entre aspas podem
ocupar várias linhas físicas. As tabelas de saída preservam a ordem relativa
dos registros na entrada.

Os arquivos de relatório têm nomes fixos. Uma nova execução na mesma pasta
substitui esses arquivos. O escritor rejeita uma saída que coincida com o
arquivo de entrada, para não sobrescrevê-lo. O CSV não armazena metadados de
tipos: ao abrir o relatório em outra ferramenta, configure os identificadores
como texto para conservar os zeros na visualização.

## Contagens exclusivas e exemplo controlado

As categorias são exclusivas por registro, não por quantidade de problemas,
grupos ou pedidos. Sempre vale:

```text
lidas = validas + invalidas + duplicadas_ignoradas + conflitantes
```

Em `data/exemplo_com_erros.csv`, considerando o ordinal descrito acima:

| Posições | Classificação | Motivo principal |
| --- | --- | --- |
| 2, 3 e 12 | Válidas | Conteúdo válido e chaves distintas. |
| 4 | Duplicada ignorada | Repete o registro da posição 2. |
| 5 | Inválida | Produto vazio. |
| 6 | Inválida | Data inexistente. |
| 7 | Inválida | Quantidade não inteira. |
| 8 | Inválida | Preço com três casas decimais. |
| 9 e 10 | Conflitantes | Mesma chave com preços válidos divergentes. |
| 11 | Inválida | Quantidade zero, sem participar do conflito da mesma chave. |

Portanto, o resultado esperado é `11 = 3 + 5 + 1 + 2`.
Os quatro registros de `data/exemplo_vendas.csv` satisfazem as regras e têm
chaves distintas: o resultado esperado é `4 = 4 + 0 + 0 + 0`.

## Resultado do comando e limites

- Código `0`: os relatórios foram gerados, inclusive quando há rejeições
  ou colunas obrigatórias ausentes.
- Código `1`: erro de leitura, arquivo vazio, CSV malformado, codificação incompatível,
  falha de gravação ou tentativa de sobrescrever a entrada.
- Código `2`: argumentos obrigatórios ausentes ou comando incorreto.

O JSON e os CSVs devem ser consultados para avaliar a qualidade dos registros;
o código de saída `0` não significa que todos os dados foram aceitos.
Uma entrada com cabeçalho e sem registros tem todas as contagens iguais a zero.
Uma entrada sem conteúdo não pode ser lida como tabela e termina com erro.
Não há limpeza automática de campos, correção de valores, validação de
faturamento, exportação para planilhas ou processamento em blocos nesta etapa.
