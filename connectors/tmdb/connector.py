"""TMDB connector for Strattum, built on The Movie Database API v3.

Authentication uses the account's "API Read Access Token" (Settings > API on
themoviedb.org), sent as ``Authorization: Bearer <token>``.

Resources:
- ``genres``: the movie genres (id and name).
- ``popular_movies``: the current popular movies list, page by page. TMDB
  serves at most 500 pages of 20 movies, so the read stops at the smaller of
  the API's ``total_pages``, 500 and the optional page limit.

Neither endpoint has an "updated since" filter, so both are full refresh.
"""

from strattum_sdk import BearerAuth, CheckFailed, Connector, Secret, Text, resource

MAX_API_PAGES = 500


class TMDB(Connector):
    credentials = {
        "api_token": Secret(
            {"pt-BR": "Token de leitura da API (v4)", "en": "API read access token (v4)"}
        ),
        "language": Text(
            {"pt-BR": "Idioma dos dados (opcional)", "en": "Data language (optional)"},
            placeholder={"pt-BR": "Ex.: pt-BR", "en": "E.g. en-US"},
            required=False,
        ),
        "max_pages": Text(
            {
                "pt-BR": "Limite de páginas de filmes (opcional, 20 por página)",
                "en": "Movie page limit (optional, 20 per page)",
            },
            placeholder={"pt-BR": "Ex.: 5", "en": "E.g. 5"},
            required=False,
        ),
    }
    base_url = "https://api.themoviedb.org/3"
    auth = BearerAuth(token="{api_token}")

    @resource("genres", primary_key="id", fields={"id": "integer", "name": "string"})
    def genres(self, client, cursor):
        data = self._get_json(client, "/genre/movie/list", params=self._language_param())
        yield from data.get("genres") or []

    @resource(
        "popular_movies",
        primary_key="id",
        fields={
            "id": "integer",
            "title": "string",
            "original_title": "string",
            "original_language": "string",
            "release_date": "date",
            "popularity": "number",
            "vote_average": "number",
            "vote_count": "integer",
            "genre_ids": "string",
            "adult": "boolean",
            "overview": "string",
            "poster_path": "string",
        },
    )
    def popular_movies(self, client, cursor):
        limit = self._max_pages()
        page, last_page = 1, MAX_API_PAGES
        while page <= last_page:
            data = self._get_json(
                client, "/movie/popular", params={"page": page, **self._language_param()}
            )
            last_page = min(data.get("total_pages") or 1, MAX_API_PAGES, limit or MAX_API_PAGES)
            for movie in data.get("results") or []:
                yield {
                    "id": movie["id"],
                    "title": movie.get("title"),
                    "original_title": movie.get("original_title"),
                    "original_language": movie.get("original_language"),
                    # TMDB sends "" for an unknown date; a date column wants null.
                    "release_date": movie.get("release_date") or None,
                    "popularity": movie.get("popularity"),
                    "vote_average": movie.get("vote_average"),
                    "vote_count": movie.get("vote_count"),
                    "genre_ids": ",".join(str(g) for g in movie.get("genre_ids") or []),
                    "adult": movie.get("adult"),
                    "overview": movie.get("overview"),
                    "poster_path": movie.get("poster_path"),
                }
            page += 1

    def check(self, client):
        # /authentication answers 200 for a valid read token and 401 otherwise;
        # the SDK turns the 401 into its "credentials rejected" message.
        data = self._get_json(client, "/authentication")
        if not data.get("success"):
            raise CheckFailed(
                {
                    "pt-BR": "O TMDB não validou o token. Use o token de leitura (v4), não a chave v3.",
                    "en": "TMDB did not accept the token. Use the read access token (v4), not the v3 key.",
                }
            )

    def _get_json(self, client, path, params=None):
        response = client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def _language_param(self):
        language = (self._values.get("language") or "").strip()
        return {"language": language} if language else {}

    def _max_pages(self):
        raw = (self._values.get("max_pages") or "").strip()
        if not raw:
            return None
        limit = int(raw)
        if limit <= 0:
            raise ValueError("max_pages must be a positive integer")
        return limit
