# sdk-connector-demo

Conector custom da Strattum para a [PokeAPI](https://pokeapi.co), escrito com
o `strattum-sdk`.

## O que ele traz

| Recurso | Linhas | Colunas |
|---|---|---|
| `pokemon` | um por Pokémon (~1.350) | `id`, `name`, `height`, `weight`, `base_experience`, `types`, `primary_type`, `hp`, `attack`, `defense`, `special_attack`, `special_defense`, `speed`, `sprite_url` |
| `types` | um por tipo (~20) | `id`, `name`, `generation`, `pokemon_count` |

A API é pública e não tem credencial. O único campo do wizard é
**Limite de pokémon**, opcional: a leitura completa faz uma chamada por
Pokémon, então use um limite (por exemplo 50) para testes rápidos. Os dois
recursos são full refresh, porque a API não tem filtro por data de alteração.

## Rodar localmente

```bash
pip install /caminho/para/strattum-platform/strattum-sdk
strattum-connector validate connectors/pokedex
echo '{"max_pokemon": "5"}' > creds.json
strattum-connector check connectors/pokedex --creds creds.json
strattum-connector read pokemon connectors/pokedex --creds creds.json
strattum-connector read types connectors/pokedex --creds creds.json --limit 3
```

## Registrar na Strattum

Em **Conectores > Adicionar conector > Novo conector custom**:

- URL do repositório: `https://github.com/guijasss/sdk-connector-demo.git`
- Caminho: `connectors/pokedex`
- Ref: `main`
