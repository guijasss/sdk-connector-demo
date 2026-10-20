"""Pokedex connector for Strattum, built on the PokeAPI (https://pokeapi.co).

The API is public and needs no credentials. The only setting is an optional
cap on how many Pokémon to read, useful to keep test syncs short: a full
read makes one request per Pokémon (about 1,350).

Resources:
- ``pokemon``: one row per Pokémon, with types and base stats flattened into
  columns. List call plus one detail call per Pokémon.
- ``types``: the elemental types (fire, water, ...), with the generation that
  introduced each one.

The API has no "updated since" filter, so both resources are full refresh.
"""

from strattum_sdk import Connector, Offset, Text, resource

PAGE_SIZE = 100

STAT_COLUMNS = {
    "hp": "hp",
    "attack": "attack",
    "defense": "defense",
    "special-attack": "special_attack",
    "special-defense": "special_defense",
    "speed": "speed",
}


class Pokedex(Connector):
    credentials = {
        "max_pokemon": Text(
            {
                "pt-BR": "Limite de pokémon (opcional, para testes)",
                "en": "Pokémon limit (optional, for tests)",
            },
            placeholder={"pt-BR": "Ex.: 50", "en": "E.g. 50"},
            required=False,
        ),
    }
    base_url = "https://pokeapi.co/api/v2"

    @resource(
        "pokemon",
        primary_key="id",
        fields={
            "id": "integer",
            "name": "string",
            "height": "integer",
            "weight": "integer",
            "base_experience": "integer",
            "types": "string",
            "primary_type": "string",
            "hp": "integer",
            "attack": "integer",
            "defense": "integer",
            "special_attack": "integer",
            "special_defense": "integer",
            "speed": "integer",
            "sprite_url": "string",
        },
    )
    def pokemon(self, client, cursor):
        limit = self._max_pokemon()
        listing = client.paginate("/pokemon", records="results", paginate=Offset(PAGE_SIZE))
        for count, entry in enumerate(listing, start=1):
            if limit is not None and count > limit:
                return
            yield self._pokemon_row(client, entry["name"])

    @resource(
        "types",
        primary_key="id",
        fields={
            "id": "integer",
            "name": "string",
            "generation": "string",
            "pokemon_count": "integer",
        },
    )
    def types(self, client, cursor):
        for entry in client.paginate("/type", records="results", paginate=Offset(PAGE_SIZE)):
            detail = self._get_json(client, f"/type/{entry['name']}")
            yield {
                "id": detail["id"],
                "name": detail["name"],
                "generation": (detail.get("generation") or {}).get("name"),
                "pokemon_count": len(detail.get("pokemon") or []),
            }

    def check(self, client):
        # One cheap call proves the API is reachable; the default check would
        # also fetch a Pokémon detail.
        self._get_json(client, "/type", params={"limit": 1})

    def _pokemon_row(self, client, name):
        detail = self._get_json(client, f"/pokemon/{name}")
        slots = sorted(detail.get("types") or [], key=lambda t: t["slot"])
        type_names = [t["type"]["name"] for t in slots]
        row = {
            "id": detail["id"],
            "name": detail["name"],
            "height": detail.get("height"),
            "weight": detail.get("weight"),
            "base_experience": detail.get("base_experience"),
            "types": ",".join(type_names),
            "primary_type": type_names[0] if type_names else None,
            "sprite_url": (detail.get("sprites") or {}).get("front_default"),
        }
        for stat in detail.get("stats") or []:
            column = STAT_COLUMNS.get(stat["stat"]["name"])
            if column:
                row[column] = stat["base_stat"]
        return row

    def _get_json(self, client, path, params=None):
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def _max_pokemon(self):
        raw = (self._values.get("max_pokemon") or "").strip()
        if not raw:
            return None
        limit = int(raw)
        if limit <= 0:
            raise ValueError("max_pokemon must be a positive integer")
        return limit
