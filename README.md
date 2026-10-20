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

# Conector TMDB

Conector para a [The Movie Database API v3](https://developer.themoviedb.org),
em `connectors/tmdb`. Exercita o caminho com credencial do SDK.

| Recurso | Linhas | Colunas |
|---|---|---|
| `genres` | ~19 gêneros de filme | `id`, `name` |
| `popular_movies` | 20 por página, até 500 páginas | `id`, `title`, `original_title`, `original_language`, `release_date`, `popularity`, `vote_average`, `vote_count`, `genre_ids`, `adult`, `overview`, `poster_path` |

Campos do wizard:

- **Token de leitura da API (v4)**, obrigatório: em themoviedb.org, Settings >
  API, o "API Read Access Token" (não a "API Key" v3). Vai como
  `Authorization: Bearer`.
- **Idioma dos dados**, opcional (`pt-BR`, `en-US`...).
- **Limite de páginas de filmes**, opcional. Sem limite, a leitura vai até 500
  páginas (10.000 filmes).

O teste de conexão chama `/authentication`: token inválido vira "A API recusou
as credenciais". Os dois recursos são full refresh.

Rodar localmente:

```bash
# creds.tmdb.json (ignorado pelo git): {"api_token": "<token>", "language": "pt-BR", "max_pages": "2"}
strattum-connector check connectors/tmdb --creds creds.tmdb.json
strattum-connector read genres connectors/tmdb --creds creds.tmdb.json
strattum-connector read popular_movies connectors/tmdb --creds creds.tmdb.json --limit 5
```

Registro na Strattum: mesmo repositório, caminho `connectors/tmdb`, ref `main`.
