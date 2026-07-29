"""FieldAdapter protocol + registry.

Adding a product is one class and one import — no pack_writer edit, no chrome
edit (G-EXT). Mirrors the `*Reader` Lego pattern already used offline.

    @register
    class PressureFort64Adapter:
        name = "pressure"
        products = ("pressure",)
        def available(self, ctx): ...
        def export(self, ctx): ...
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol, Sequence, runtime_checkable


@runtime_checkable
class FieldAdapter(Protocol):
    #: adapter id, used in --products and logs
    name: str
    #: product keys this adapter can satisfy
    products: Sequence[str]

    def available(self, ctx: Any) -> bool:
        """True when this adapter's inputs exist for the run."""
        ...

    def export(self, ctx: Any) -> List[Dict[str, Any]]:
        """Write binaries via ctx.writer; return the meta field rows added."""
        ...


REGISTRY: List[FieldAdapter] = []


def register(adapter_cls):
    """Class decorator: instantiate once and add to the registry."""
    REGISTRY.append(adapter_cls())
    return adapter_cls


def adapters_for(products: Sequence[str]) -> List[FieldAdapter]:
    """Registry entries that satisfy at least one requested product."""
    wanted = set(products)
    return [a for a in REGISTRY if wanted.intersection(a.products)]


def all_products() -> List[str]:
    seen: List[str] = []
    for a in REGISTRY:
        for p in a.products:
            if p not in seen:
                seen.append(p)
    return seen
