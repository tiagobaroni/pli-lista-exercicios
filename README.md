# lista_mma — Soluções Computacionais de PLIM

Implementações dos exercícios computacionais da lista de Programação Linear Inteira Mista,
organizadas por parte. Cada parte é independente e pode ser executada de forma autônoma.

**Autor:** Tiago H. França Baroni

---

## Contexto acadêmico

Esta lista é parte da disciplina de Programação Linear Inteira Mista (PLIM) da
especialização em Métodos Matemáticos Aplicados (MMA). Está dividida em quatro partes:

| Parte | Conteúdo | Código |
|-------|----------|--------|
| 1 | Árvore de Branch-and-Bound | Neste repositório |
| 2 | Formulação matemática de problemas | Apenas documento LaTeX — sem código |
| 3 | Transporte, designação e investimento | Neste repositório |
| 4 | Árvore geradora mínima e fluxo máximo | Neste repositório |

A Parte 2 consiste exclusivamente de formulação matemática e não gera código executável.

---

## Metodologia

Cada parte segue o mesmo princípio: implementar o algoritmo do zero e, ao final, confrontar
o resultado com uma fonte independente.

| Parte | Algoritmo implementado | Verificação independente |
|-------|----------------------|--------------------------|
| 1 | Branch-and-Bound; relaxação LP via `scipy.optimize.linprog` (backend HiGHS) | `scipy.optimize.milp` |
| 3 | Formulação LP/PLIM via `scipy.optimize.linprog` e `scipy.optimize.milp` | `scipy.optimize.linear_sum_assignment` (Exercício 5) |
| 4 | Prim e Kruskal (AGM); Edmonds-Karp (fluxo máximo) | `networkx` |

---

## Estrutura do repositório

```
lista_mma/
├── parte1/                    # Branch-and-Bound (Exercícios 1, 2 e 4)
│   ├── bb/
│   │   ├── formatting.py      # formatação de nós e exportação JSON
│   │   ├── model.py           # dataclasses e construtores de cada exercício
│   │   ├── relaxation.py      # relaxação LP e verificação MILP
│   │   └── solver.py          # motor Branch-and-Bound
│   ├── tests/
│   ├── output/
│   └── run.py
├── parte3/                    # Transporte, Designação e Investimento (Exercícios 4, 5 e 6)
│   ├── tests/
│   ├── output/
│   ├── designacao.py
│   ├── formatting.py
│   ├── investimento.py
│   ├── transporte.py
│   └── run.py
├── parte4/                    # AGM e Fluxo Máximo (Exercícios 1, 2 e 3)
│   ├── tests/
│   ├── output/
│   ├── formatting.py
│   ├── graphs.py              # dados dos grafos G1, G2 e G3
│   ├── maxflow.py             # Edmonds-Karp
│   ├── mst.py                 # Prim, Kruskal e Union-Find
│   └── run.py
├── requirements.txt
└── README.md
```

---

## Requisitos

- Python 3.13
- `numpy >= 1.26`
- `scipy >= 1.12`
- `networkx >= 3.0` (Parte 4 — apenas para verificação cruzada)

---

## Preparação do ambiente

```bash
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Parte 1 — Branch-and-Bound

Resolve três problemas de Programação Linear Inteira Mista usando um Branch-and-Bound
construído sobre `scipy.optimize.linprog` (backend HiGHS). Todos os nós são impressos
ao final, depois que a árvore inteira é explorada, de modo que o nó incumbente exibe o
status correto (`Solução Ótima`).

### Exercícios

| Exercício | Tipo | Sentido | Variáveis inteiras |
|-----------|------|---------|-------------------|
| 1 | Inteiro puro | Maximização | x1, x2, x3, x4 |
| 2 | Misto | Maximização | x1, x2, x4 (x3 contínua) |
| 4 | Misto | Minimização | x1, x3 (x2 contínua) |

### Argumentos

| Argumento | Obrigatório | Padrão | Descrição |
|-----------|-------------|--------|-----------|
| `--exercicio` | sim | — | Número do exercício: `1`, `2` ou `4` |
| `--strategy` | não | `dfs` | Estratégia de busca: `dfs` (pilha LIFO) ou `bfs` (fila FIFO) |
| `--max-nodes` | não | ilimitado | Parar após processar N nós |
| `--json-out` | não | — | Caminho para exportação da árvore em JSON |

### Uso

```bash
cd parte1
python run.py --exercicio 1
python run.py --exercicio 2 --strategy bfs
python run.py --exercicio 4 --json-out output/arvore_ex4.json
```

### Formato de saída

Cada nó é exibido como um bloco de texto após a árvore inteira ser explorada. Nós podados
(`Solução Infactível`, `Inferior a melhor já obtida`) exibem apenas o status. Os demais
exibem também o valor de Z e das variáveis.

```
Subproblema 0
  Z  = 22,33
  x1 = 0
  x2 = 3,1667
  x3 = 0,7222
  x4 = 0
  Status: Ramificado
----------------------------------------
Subproblema 1
  Ramo: x3 <= 0
  Z  = 15,83
  x1 = 0
  x2 = 3,1667
  x3 = 0
  x4 = 0
  Status: Ramificado
----------------------------------------
...
```

Status possíveis: `Ramificado`, `Solução Candidata`, `Solução Ótima`, `Solução Infactível`,
`Inferior a melhor já obtida`.

Ao final, o bloco de resultado resume a solução e confirma a verificação:

```
=== Resultado - Exercício 1 ===
Nós resolvidos: 11
Solução ótima: x1=1,  x2=2,  x3=1,  x4=0  |  Z = 20,00
Verificação milp: Z = 20,00  ✓
```

---

## Parte 3 — Transporte, Designação e Investimento

### Exercícios

| Exercício | Tipo | Modelo |
|-----------|------|--------|
| 4 | Transporte desequilibrado (Deise–Luzia) | PL com restrições de igualdade |
| 5 | Designação trabalhador–tarefa (6×6) | PLIM binária |
| 6 | Seleção de projetos de investimento (10 projetos) | PLIM binária com restrições lógicas |

### Argumentos

| Argumento | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--exercicio` | sim | Número do exercício: `4`, `5` ou `6` |
| `--json-out` | não | Caminho para exportação da solução em JSON |

### Uso

```bash
cd parte3
python run.py --exercicio 4
python run.py --exercicio 5 --json-out output/designacao_ex5.json
python run.py --exercicio 6 --json-out output/investimento_ex6.json
```

### Formato de saída

**Exercício 4 — Transporte** (trecho final):

```
  Balanco: TODAS as restricoes satisfeitas

  Custo total otimo: 16678,50
```

**Exercício 5 — Designação** (trecho final):

```
  Tempo total (milp):                  99 min
  Verificacao (linear_sum_assignment): 99 min
  Resultado: OK - valores coincidem
```

**Exercício 6 — Investimento** (trecho final):

```
  Projetos selecionados: ['Proj 1', 'Proj 2', 'Proj 3', 'Proj 7', 'Proj 10']
  Numero de projetos:    5 / 5
  Investimento total:    $ 395,000 / $ 400,000
  Valor presente total:  $ 475,000
```

---

## Parte 4 — Árvore Geradora Mínima e Fluxo Máximo

Os Exercícios 1 e 2 calculam a Árvore Geradora Mínima em grafos não orientados usando
Kruskal e Prim. O Exercício 3 calcula o fluxo máximo em um grafo orientado usando
Edmonds-Karp. A cada execução são exibidos a sequência completa de decisões, o resultado
e a verificação cruzada com o NetworkX.

### Exercícios

| Exercício | Algoritmos | Grafo | Nós | Arestas/Arcos |
|-----------|-----------|-------|-----|---------------|
| 1 | Prim + Kruskal | G1 — não orientado | 12 | 19 |
| 2 | Prim + Kruskal | G2 — não orientado | 15 | 28 |
| 3 | Edmonds-Karp | G3 — orientado (fonte: 1, sumidouro: 12) | 12 | 19 |

### Argumentos

| Argumento | Obrigatório | Padrão | Descrição |
|-----------|-------------|--------|-----------|
| `--exercicio` | sim | — | Número do exercício: `1`, `2` ou `3` |
| `--prim-start` | não | `1` | Nó inicial do Prim (exercícios 1 e 2) |
| `--json-out` | não | — | Caminho para exportação da solução em JSON |

### Uso

```bash
cd parte4
python run.py --exercicio 1
python run.py --exercicio 2 --prim-start 8
python run.py --exercicio 3 --json-out output/maxflow_ex3.json
```

### Formato de saída

**Exercício 1 — AGM** (trechos representativos):

```
--- Kruskal - Sequencia de decisoes ---
     #     Aresta     Peso  Decisao
  ----  ------------  ----  ----------
     1     (2, 4)        4  Aceita
     2    (8, 10)        4  Aceita
  ...
    19     (6, 7)       22  Rejeitada

  Arestas da arvore (Kruskal): (2,4), (8,10), (3,6), (3,4), (7,11), (1,3), (5,6), (8,9), (4,9), (7,10), (11,12)
  Peso total: 74
```

```
--- Verificacao ---
  Kruskal:  74
  Prim:     74
  NetworkX: 74  [OK]
```

**Exercício 3 — Fluxo máximo** (trechos representativos):

```
--- Caminhos aumentadores ---
  Iter  Caminho aumentador            Gargalo  Fluxo acumulado
  ------------------------------------------------------------
     1  1 -> 2 -> 4 -> 9 -> 10 -> 12        4                4
     2  1 -> 3 -> 4 -> 9 -> 10 -> 12        3                7
     3  1 -> 3 -> 5 -> 8 -> 10 -> 12        4               11

--- Fluxo maximo ---
  11
```

```
  Soma das capacidades: 11  [OK]  (fluxo maximo = 11)

--- Verificacao NetworkX ---
  Fluxo maximo NetworkX: 11  [OK]
```

---

## Resultados consolidados

| Parte | Exercício | Resultado |
|-------|-----------|-----------|
| 1 | 1 | Z = 20,00 — x1=1, x2=2, x3=1, x4=0 |
| 1 | 2 | Z = 48,17 — x1=0, x2=2, x3=0,1667, x4=5 |
| 1 | 4 | Z = 11,50 — x1=2, x2=2,5, x3=0 |
| 3 | 4 | Custo mínimo de transporte = 16.678,50 |
| 3 | 5 | Tempo mínimo de designação = 99 min |
| 3 | 6 | Valor presente máximo = R$ 475.000; projetos 1, 2, 3, 7 e 10; investimento = R$ 395.000 |
| 4 | 1 | Peso da AGM (G1) = 74 |
| 4 | 2 | Peso da AGM (G2) = 86 |
| 4 | 3 | Fluxo máximo (G3) = 11 |

---

## Testes automatizados

```bash
# Parte 1
cd parte1
python -m pytest tests/ -v

# Parte 3
cd parte3
python -m pytest tests/ -v

# Parte 4
cd parte4
python -m pytest tests/ -v
```

| Parte | Testes | O que cobrem |
|-------|--------|--------------|
| 1 | 25 | Verificação de integralidade, seleção de variável de ramificação, formatação numérica, testes fim a fim com verificação por `scipy.optimize.milp` |
| 3 | 18 | Balanço oferta/demanda, validade de atribuição, satisfação de restrições lógicas, orçamento e limite de gerentes |
| 4 | 25 | Union-Find (compressão de caminho, union by rank), contagem e peso da AGM, conservação de fluxo, capacidade do corte mínimo, limites de capacidade dos arcos |

---

## Licença

MIT License. Consulte o arquivo [LICENSE](LICENSE) na raiz do repositório.

---

## Citação

Se este trabalho for útil, utilize os metadados em [CITATION.cff](CITATION.cff) ou a referência abaixo:

```
Baroni, T. H. F. (2026). lista_mma: soluções computacionais de Programação
Linear Inteira Mista. GitHub. https://github.com/tiagobaroni/pli-lista-exercicios
```
