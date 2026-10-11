# Pull, Otimização e Avaliação de Prompts — Bug → User Story

Desafio de Prompt Engineering em Python + LangChain que faz **pull** de um prompt de baixa qualidade do LangSmith Prompt Hub, **otimiza** esse prompt com técnicas avançadas de prompting e faz **push** de volta, avaliando a qualidade via **LangSmith** com 5 métricas customizadas (`helpfulness`, `correctness`, `f1_score`, `clarity`, `precision`).

O objetivo é transformar relatos de bug em User Stories (`bug_to_user_story`) atingindo **todas as 5 métricas >= 0.8** (não apenas a média).

---

## Técnicas Aplicadas (Fase 2)

O prompt otimizado (`prompts/bug_to_user_story_v2.yml`) aplica **4 técnicas** combinadas. A escolha de cada uma foi guiada pelas métricas de avaliação: `f1_score`, `clarity` e `precision`, sendo que `precision` entra no cálculo de `helpfulness` **e** de `correctness`, ou seja, é a métrica mais puxada pelo peso.

### 1. Few-shot Learning — `few-shot`

**Por quê:** o ground truth do dataset segue um formato muito específico, que escala com a complexidade do bug (simples → story + critérios; médio → + Contexto Técnico; complexo → seções `=== USER STORY PRINCIPAL ===`, `=== CRITÉRIOS DE ACEITAÇÃO ===`, `=== CRITÉRIOS TÉCNICOS ===`, `=== CONTEXTO DO BUG ===`, `=== TAREFAS TÉCNICAS ===`). Nenhuma instrução abstrata ensina esse formato tão bem quanto exemplos concretos de entrada/saída.

**Como foi aplicado:** foram incluidos **3 exemplos**: um bug simples (validação de e-mail), um médio (webhook de pagamento com logs/endpoint) e um complexo (checkout com múltiplas falhas), cobrindo todo o espectro do dataset (5 simples, 7 médios, 3 complexos).

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

> ⏳ A preencher após executar `src/evaluate.py` (Fase 3/4).

- Link público do dataset de avaliação: *(a gerar com `Client().share_dataset(...)`)*
- Screenshots das notas >= 0.8: *(a anexar)*
- Comparação v1 vs v2: *(a documentar)*

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
python src/evaluate.py            # 3. avaliar contra o dataset
pytest tests/test_prompts.py      # 4. validar o prompt
```