#!/usr/bin/env python3

import logging
from collections.abc import Generator, Mapping

from doc2dash.parsers.intersphinx import InterSphinxParser
from doc2dash.parsers.intersphinx_inventory import InventoryEntry
from doc2dash.parsers.types import ParserEntry

log = logging.getLogger(__name__)


class InterSphinxFilter(InterSphinxParser):
    def _inv_to_entries(
        self, inv: Mapping[str, Mapping[str, InventoryEntry]]
    ) -> Generator[ParserEntry, None, None]:
        inv = dict(inv)

        # Filter out labels that point to objects
        obj_types = [typ for typ in inv.keys() if typ.startswith("py:")]

        remove = []
        for type_key in obj_types:
            for key in inv[type_key]:
                for ignore_type in ["std:doc", "std:label"]:
                    for ignore_key, (_, name) in inv[ignore_type].items():
                        if (
                            ignore_key.endswith(key)
                            or ignore_key.endswith(key.lower())
                            or ignore_key.endswith(key.replace(".", "-").lower())
                            or ignore_key.endswith(key + ".rst")
                            or ignore_key.endswith(key.lower() + ".rst")
                            or ignore_key == name
                        ):
                            remove.append((ignore_type, ignore_key))

        # Filter out labels that point to the title section
        type_key = "std:label"
        for key, (_, name) in inv[type_key].items():
            if key.find(".rst#") > 0 and key.endswith(
                "#" + name.lower().replace(" ", "-").replace(".", "-")
            ):
                remove.append((type_key, key))

        # Filter out whats new labels (except versions sections)
        type_key = "std:label"
        for key in inv[type_key]:
            if key.startswith("/waths-new.rst#") and not key.startswith(
                "/whats-new.rst#v"
            ):
                remove.append((type_key, key))

        for typ, key in remove:
            inv[typ].pop(key, None)

        yield from super()._inv_to_entries(inv)
