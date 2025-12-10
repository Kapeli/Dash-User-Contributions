#!/usr/bin/env python3

import logging
import re
from collections.abc import Generator, Mapping

from doc2dash.parsers.intersphinx import InterSphinxParser
from doc2dash.parsers.intersphinx_inventory import InventoryEntry
from doc2dash.parsers.types import ParserEntry

log = logging.getLogger(__name__)


label_re = re.compile("[ _.]")


class InterSphinxFilter(InterSphinxParser):
    def _inv_to_entries(
        self, inv: Mapping[str, Mapping[str, InventoryEntry]]
    ) -> Generator[ParserEntry, None, None]:
        inv = {k: dict(v) for k, v in inv.items()}

        remove = []

        # Filter out labels and docs that point to existing objects entries
        obj_types = [typ for typ in inv.keys() if typ.startswith("py:")]
        for type_key in obj_types:
            for key in inv[type_key]:
                # remove doc that point to entry
                remove.append(("std:doc", f"generated/{key}"))
                # remove the 3 labels that point to entry
                label_doc = f"/generated/{key.lower()}.rst"
                for remove_key in [
                    label_doc,
                    f"{label_doc}#{key.lower()}",
                    f"{label_doc}#{label_re.sub('-', key.lower())}",
                ]:
                    remove.append(("std:label", remove_key))

        # Remove labels that just point to a document (redundant with std:doc)
        for key in inv["std:label"]:
            if key.endswith((".rst", ".ipynb")):
                remove.append(("std:label", key))

        # Filter out whats new labels (except versions sections)
        for key in inv["std:label"]:
            if key.startswith("/whats-new.rst#") and not key.startswith(
                "/whats-new.rst#v"
            ):
                remove.append(("std:label", key))

        for type_key, key in remove:
            inv[type_key].pop(key, None)

        yield from super()._inv_to_entries(inv)
