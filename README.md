# Pull, Otimização e Avaliação de Prompts — Bug → User Story

Desafio de Prompt Engineering em Python + LangChain que faz **pull** de um prompt de baixa qualidade do LangSmith Prompt Hub, **otimiza** esse prompt com técnicas avançadas de prompting e faz **push** de volta, avaliando a qualidade via **LangSmith** com 5 métricas customizadas (`helpfulness`, `correctness`, `f1_score`, `clarity`, `precision`).

O objetivo é transformar relatos de bug em User Stories (`bug_to_user_story`) atingindo **todas as 5 métricas >= 0.8** (não apenas a média).

---

## Técnicas Aplicadas (Fase 2)

O prompt otimizado (`prompts/bug_to_user_story_v2.yml`) aplica **4 técnicas** combinadas. A escolha de cada uma foi guiada pelas métricas de avaliação: `f1_score`, `clarity` e `precision`, sendo que `precision` entra no cálculo de `helpfulness` **e** de `correctness`, ou seja, é a métrica mais puxada pelo peso.

### 1. Few-shot Learning — `few-shot`

**Por quê:** o ground truth do dataset segue um formato muito específico, que escala com a complexidade do bug (simples → story + critérios; médio → + Contexto Técnico; complexo → seções `=== USER STORY PRINCIPAL ===`, `=== CRITÉRIOS DE ACEITAÇÃO ===`, `=== CRITÉRIOS TÉCNICOS ===`, `=== CONTEXTO DO BUG ===`, `=== TAREFAS TÉCNICAS ===`). Nenhuma instrução abstrata ensina esse formato tão bem quanto exemplos concretos de entrada/saída.

**Como foi aplicado:** foram incluídos **3 exemplos**: um bug simples (validação de e-mail), um médio (webhook de pagamento com logs/endpoint) e um complexo (checkout com múltiplas falhas), cobrindo todo o espectro do dataset (5 simples, 7 médios, 3 complexos).

### 2. Role Prompting — `role-prompting`

**Por quê:** definir a persona de um *Product Manager sênior* orienta o tom (profissional, centrado no usuário e no valor de negócio) e o padrão de qualidade da documentação ágil, que é justamente o que o avaliador de `clarity` e `precision` espera.

**Como foi aplicado:** a primeira linha do `system_prompt` define a persona: *"Você é um Product Manager sênior com experiência em metodologias ágeis"* e a tarefa de converter bugs em User Stories.

### 3. Skeleton of Thought — `skeleton-of-thought`

**Por quê:** a tarefa é fundamentalmente **estruturar** informação. O Skeleton of Thought encoraja o modelo a montar a resposta em seções explícitas, o que melhora diretamente `clarity` (organização) e `f1_score` (recall, lembra o modelo de incluir todas as seções/informações presentes na referência). É a técnica principal desta otimização.

**Como foi aplicado:** o prompt traz uma **estrutura de resposta explícita** com 3 níveis, sendo eles: bug simples, médio e complexo, indicando exatamente quais seções usar em cada caso (Critérios de Aceitação no formato `Dado que / Quando / Então / E`, Contexto Técnico, Critérios Técnicos, Contexto do Bug, Tarefas Técnicas).

### 4. Chain of Thought — `chain-of-thought`

**Por quê:** bugs complexos exigem decompor o relato em partes (usuário afetado, problema central, benefício, detalhes técnicos, complexidade) antes de escrever. Porém, se esse raciocínio "vazar" para a saída, vira informação redundante e derruba `precision` e `clarity`, por isso o CoT foi usado de forma **controlada**.

**Como foi aplicado:** foi adicionada a seção *"Como analisar o bug (raciocínio interno)"* com os 5 passos de análise, mais a **regra explícita** de *"não escreva na saída"* e de *"não expor o seu raciocínio"*. Assim o modelo ganha a qualidade de análise do CoT sem poluir a resposta final.

---

## Resultados Finais

O prompt otimizado (`bug_to_user_story_v2`) atingiu **todas as 5 métricas >= 0.8**, sendo **APROVADO**. Já o seed prompt (prompt ruim) (`bug_to_user_story_v1`) foi **REPROVADO**: F1-Score e Correctness ficaram abaixo do limiar.

### Resumo das notas

| Métrica | v1 (semente) | v2 (otimizado) | Meta |
|---|---|---|---|
| helpfulness | 0.85 | 0.86 | >= 0.8 |
| correctness | 0.77 ❌ | 0.82 ✅ | >= 0.8 |
| f1_score | 0.72 ❌ | 0.80 ✅ | >= 0.8 |
| clarity | 0.86 | 0.89 | >= 0.8 |
| precision | 0.83 | 0.83 | >= 0.8 |
| **Status** | **REPROVADO** | **APROVADO** | — |

### Links

- **Dataset de avaliação (público):** https://smith.langchain.com/public/6c83fd00-96b9-4fd9-a460-c572aba9425f/d
- **Experimento v1 (seed):** https://smith.langchain.com/o/069de491-6d0b-422c-b7ce-09e2c9c973b4/projects/p/14ca4f60-5310-404c-853a-e81730b7cb47
- **Experimento v2 (otimizado):** https://smith.langchain.com/o/069de491-6d0b-422c-b7ce-09e2c9c973b4/projects/p/065bb8e1-b5c6-4ee9-8a7c-53ca74cd070a
- **Experimento v3 (iteração F1):** https://smith.langchain.com/o/069de491-6d0b-422c-b7ce-09e2c9c973b4/projects/p/1574a194-6f0a-43df-8189-405a2394b982

> ℹ️ O link do dataset é público; os links dos experimentos apontam para o workspace do LangSmith (exigem acesso à organização).

### Screenshots

#### v1: seed (REPROVADO: F1-Score 0.72, Correctness 0.77)

**Notas médias:**

![Notas médias — v1](<img/Screenshot from 2026-10-11 22-52-36.png>)

**Todas as notas do experimento:**

<img src="img/Screenshot from 2026-10-11 22-53-22.png" alt="Todas as notas — v1" width="700">

**Traces detalhados (linhas 1, 6 e 15 do dataset):**

**Linha 1:**

![Trace — v1, linha 1](<img/Screenshot from 2026-10-11 23-28-05.png>)

**Linha 6:**

![Trace — v1, linha 6](<img/Screenshot from 2026-10-11 23-28-31.png>)

**Linha 15:**

![Trace — v1, linha 15](<img/Screenshot from 2026-10-11 22-57-26.png>)

#### v2: otimizado (APROVADO: todas as 5 métricas >= 0.8)

**Notas médias:**

![Notas médias — v2](<img/Screenshot from 2026-10-11 23-03-16.png>)

**Todas as notas do experimento:**

<img src="img/Screenshot from 2026-10-11 23-04-52.png" alt="Todas as notas — v2" width="700">

**Traces detalhados (linhas 1, 6 e 15 do dataset):**

**Linha 1:**

![Trace — v2, linha 1](<img/Screenshot from 2026-10-11 23-29-02.png>)

**Linha 6:**

![Trace — v2, linha 6](<img/Screenshot from 2026-10-11 23-29-09.png>)

**Linha 15:**

![Trace — v2, linha 15](<img/Screenshot from 2026-10-11 23-05-40.png>)

#### v3: iteração F1 (experimental)

**Notas médias:**

![Notas médias — v3](<img/Screenshot from 2026-10-11 23-07-05.png>)

**Todas as notas do experimento:**

<img src="img/Screenshot from 2026-10-11 23-07-20.png" alt="Todas as notas — v3" width="700">

**Traces detalhados (linhas 1, 6 e 15 do dataset):**

**Linha 1:**

![Trace — v3, linha 1](<img/Screenshot from 2026-10-11 23-29-22.png>)

**Linha 6:**

![Trace — v3, linha 6](<img/Screenshot from 2026-10-11 23-29-31.png>)

**Linha 15:**

![Trace — v3, linha 15](<img/Screenshot from 2026-10-11 23-08-02.png>)

### Comparação v1 vs v2: o que mudou e por quê

O v1 era um prompt "genérico" e pouco estruturado: dizia apenas *"transforme este bug em user story"*, sem persona, sem formato exigido e sem exemplos. O resultado era inconsistente em bugs médios/complexos, pois o modelo omitia seções inteiras (Contexto Técnico, Critérios de Aceitação no formato Dado/Quando/Então) e às vezes inventava detalhes que não estavam no relato. Isso derrubava o **F1-Score (recall)** (informações da referência ficavam de fora) e a **Correctness** (informação inventada ou ausente).

O v2 atacou exatamente esses dois pontos:

| Deficiência do v1 | Correção no v2 | Métrica beneficiada |
|---|---|---|
| Sem persona / tom inconsistente | **Role Prompting**: Product Manager sênior, tom profissional e centrado no usuário | `clarity`, `precision` |
| Sem formato explícito de saída | **Skeleton of Thought**: estrutura por nível de complexidade (simples/médio/complexo), com seções obrigatórias | `f1_score` (recall), `clarity` |
| Resposta "rasa" em bugs complexos | **Chain of Thought** controlado: 5 passos de análise internos, sem vazar raciocínio | `f1_score`, `precision` |
| Não sabia o formato esperado do ground truth | **Few-shot**: 3 exemplos cobrindo simples/médio/complexo | `f1_score`, `precision` |
| Inventava informação ausente | Regra explícita *"não invente informações ausentes no relato"* + edge cases | `precision`, `correctness` |

Com isso o F1-Score saltou de **0.72 → 0.80** e a Correctness de **0.77 → 0.82**, levando o prompt ao estado **APROVADO** em todas as métricas.

### Experimento de melhoria do F1-Score (iteração extra)

Mesmo com o v2 já aprovado, o F1-Score ficou em **0.80**, apenas `0.0006` acima do limiar. Por isso foi tentada uma iteração extra focada em subir o *recall*, a componente que o juiz penaliza quando fatos concretos da referência ficam de fora da resposta.

**Hipótese:** o F1-Score era limitado pelo recall, ou seja: detalhes factuais (números, percentuais, endpoints, códigos HTTP, mensagens de erro, steps to reproduce) estavam sendo omitidos nas respostas.

**O que foi mudado na versão experimental:**
- **Regra 4 reforçada**: passou a exigir "preservar fielmente cada fato concreto do relato" (valores numéricos, percentuais, endpoints, logs, mensagens de erro, steps to reproduce) *exatamente como aparecem*.
- **Nova regra de "Exemplo de Cálculo"**: pedir uma seção com o cálculo quando o bug envolve valores/desconto/pipeline.
- **Skeleton of Thought ajustado**: mais itens nos critérios de aceitação e, para bugs médios, "subseção por aspecto distinto + Exemplo de Cálculo".
- **CoT com passo extra**: enumerar os "detalhes factuais a preservar" antes de escrever.
- **+2 edge cases** e um **4º exemplo few-shot** (bug de desconto em pipeline, com "Exemplo de Cálculo" e "Contexto Técnico").

**Resultado:** o F1-Score subiu de `0.8006` → `0.8041`, um ganho baixo. O ganho de recall nos casos numéricos foi compensado por quedas de `precision`: as seções extras de cálculo às vezes eram lidas pelo juiz como informação redundante ou alucinada.

**Conclusão:** como a melhoria foi mínima e trouxe o risco de piorar `precision`/`clarity`, a versão original do v2 foi restaurada, pois já passava em todas as métricas.

> 🔗 **Prompt no Hub (`bug_to_user_story_v2`):** https://smith.langchain.com/prompts/bug_to_user_story_v2/eabf000c?organizationId=069de491-6d0b-422c-b7ce-09e2c9c973b4&tab=0 — o 1º commit é a versão v2 (original) e o 2º commit é a versão v3 (experimental).

---

## Como Executar

### Pré-requisitos

- Python 3.10+
- Chave da OpenAI (`OPENAI_API_KEY`)
- Chave do LangSmith (`LANGSMITH_API_KEY`) + `LANGSMITH_PROJECT` + `USERNAME_LANGSMITH_HUB` (handle público do Prompt Hub)

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Lembrar de preencher variáveis de ambiente no arquivo **.env** seguindo o formato do arquivo **.env.example**.

### Pipeline

```bash
python src/pull_prompts.py        # 1. pull do prompt semente (v1)
python src/push_prompts.py        # 2. push público do prompt otimizado (v2)
pytest tests/test_prompts.py      # 3. validar o prompt
python src/evaluate.py            # 4. avaliar contra o dataset
```