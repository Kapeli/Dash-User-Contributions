# Arcmira API

Search YouTube and podcast transcripts, retrieve timestamped passages and look up speaker appearances, sponsors and recommendations. The docset indexes HTTP paths, operation IDs and named components. It includes the complete OpenAPI document used to build it.

[Arcmira](https://arcmira.com) · [API documentation](https://arcmira.com/docs) · [OpenAPI source](https://api.arcmira.com/v1/openapi.json)

## Build

From this directory, run `python3 generate.py` with Python 3.9 or later. No third-party packages or API key are required. To build offline, use `python3 generate.py --spec openapi.json` with a saved copy of the published specification. The script writes `Arcmira_API.tgz` and `docset.json`.

The displayed version follows the API specification. The suffix identifies changes to the specification between numbered releases. The reference works offline; sending requests to the API requires an internet connection.

Maintained by [Arcmira](https://github.com/arcmira). Report docset issues in [Arcmira integrations](https://github.com/arcmira/integrations/issues).
