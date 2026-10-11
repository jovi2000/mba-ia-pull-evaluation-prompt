"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import save_yaml, print_section_header

load_dotenv()

SEED_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """
    Faz pull do seed prompt do LangSmith Prompt Hub e salva localmente.

    Returns:
        Dicionário com o conteúdo do prompt salvo (mesma estrutura do v1.yml).
    """
    client = Client()

    prompt = client.pull_prompt(
        SEED_PROMPT,
        dangerously_pull_public_prompt=True,
    )

    system_prompt = ""
    user_prompt = ""

    # prompt.messages contém as mensagens do ChatPromptTemplate. O conteúdo do
    # template fica em `message.prompt.template`; o tipo da mensagem é
    # distinguido via SystemMessagePromptTemplate / HumanMessagePromptTemplate.
    for message in prompt.messages:
        template = message.prompt.template

        if isinstance(message, SystemMessagePromptTemplate):
            system_prompt = template
        elif isinstance(message, HumanMessagePromptTemplate):
            user_prompt = template

    if not system_prompt and not user_prompt:
        raise ValueError(
            f"Nenhuma mensagem system/human encontrada no prompt '{SEED_PROMPT}'."
        )

    # Os campos description, version, created_at e tags ficaram hard coded, pois
    # houve uma tentativa de obte-los via pull, mas os campos voltaram vazios
    # (com exceção do created_at, que veio com valor 2025-11-19, mas optei por manter
    # o valor do placeholder original).
    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(prompt_data, OUTPUT_PATH):
        raise RuntimeError(f"Falha ao salvar o prompt em {OUTPUT_PATH}")

    return prompt_data


def main():
    """Função principal"""
    print_section_header("PULL DO SEED PROMPT DO LANGSMITH")

    print(f"Pull do seed prompt: {SEED_PROMPT}")

    try:
        prompt_data = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"\n❌ Falha ao fazer pull do prompt: {e}")
        return 1

    content = prompt_data["bug_to_user_story_v1"]

    print(f"\n✓ Prompt salvo em {OUTPUT_PATH}")
    print(f"  - description: {content['description']}")
    print(f"  - version: {content['version']}")
    print(f"  - tags: {', '.join(content['tags'])}")
    print(f"  - system_prompt: {len(content['system_prompt'])} caracteres")
    print(f"  - user_prompt: {content['user_prompt']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
