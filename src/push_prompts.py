"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import (
    load_yaml,
    check_env_vars,
    print_section_header,
    validate_prompt_structure,
)

load_dotenv()

PROMPT_NAME = "bug_to_user_story_v2"
PROMPT_PATH = "prompts/bug_to_user_story_v2.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return False

    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data["user_prompt"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt),
    ])

    techniques = prompt_data.get("techniques_applied", [])

    # As técnicas entram nos metadados via `tags` e `description`, já que o
    # `push_prompt` (langsmith 0.13) não aceita um campo `metadata` livre.
    tags = list(dict.fromkeys(prompt_data.get("tags", []) + techniques))

    description = prompt_data.get("description", "").strip()
    if techniques:
        description = f"{description} Técnicas aplicadas: {', '.join(techniques)}."

    client = Client()

    try:
        url = client.push_prompt(
            f"{username}/{prompt_name}",
            object=prompt,
            is_public=True,
            description=description,
            tags=tags,
        )
    except Exception as e:
        print(f"\n❌ Falha ao fazer push do prompt: {e}")
        return False

    print(f"\n✓ Prompt publicado com sucesso:")
    print(f"  - Nome: {username}/{prompt_name}")
    print(f"  - Público: sim")
    print(f"  - Técnicas: {', '.join(techniques) if techniques else '(nenhuma)'}")
    print(f"  - URL: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.

    Delega para `validate_prompt_structure` (utils.py), que confere a presença
    de `description`, `system_prompt` e `version`, além de exigir `system_prompt`
    não-vazio, sem TODOs e ao menos 2 técnicas em `techniques_applied`.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DO PROMPT OTIMIZADO PARA O LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    prompt_data = load_yaml(PROMPT_PATH)
    if not prompt_data:
        print(f"❌ Falha ao carregar o prompt em {PROMPT_PATH}")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    techniques = prompt_data.get("techniques_applied", [])
    print(f"\n✓ Prompt válido ({len(techniques)} técnica(s) aplicada(s))")
    print(f"  - system_prompt: {len(prompt_data['system_prompt'])} caracteres")
    print(f"  - user_prompt: {prompt_data['user_prompt']!r}")

    success = push_prompt_to_langsmith(PROMPT_NAME, prompt_data)
    if success:
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
