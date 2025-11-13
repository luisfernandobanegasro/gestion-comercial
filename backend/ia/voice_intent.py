# ia/voice_intent.py

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from catalogo.models import Producto

SPANISH_NUMBERS = {
    "un": 1,
    "uno": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
}


@dataclass
class VoiceIntent:
    raw: str
    # add | remove | clear | checkout | unknown
    action: str
    quantity: int
    product_name: str


def _parse_quantity(text: str) -> int:
    text = text.lower()

    m = re.search(r"(\d+)", text)
    if m:
        try:
            n = int(m.group(1))
            if n > 0:
                return n
        except ValueError:
            pass

    for word, value in SPANISH_NUMBERS.items():
        if word in text:
            return value

    return 1


def _clean_product_name(text: str) -> str:
    text = text.lower()

    for r in [
        "al carrito",
        "del carrito",
        "a la cesta",
        "de la cesta",
        "por favor",
        "porfa",
    ]:
        text = text.replace(r, "")

    text = re.sub(r"\d+", " ", text)

    fillers = [
        "un",
        "una",
        "uno",
        "unos",
        "unas",
        "dos",
        "tres",
        "cuatro",
        "cinco",
        "seis",
        "siete",
        "ocho",
        "nueve",
        "diez",
    ]
    for f in fillers:
        text = re.sub(rf"\b{f}\b", " ", text)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_voice_command(text: str) -> VoiceIntent:
    raw = text
    text = (text or "").lower().strip()

    if not text:
        return VoiceIntent(raw=raw, action="unknown", quantity=0, product_name="")

    # 0) Finalizar compra / pagar / crear venta
    checkout_phrases = [
        "finalizar compra",
        "finaliza la compra",
        "terminar compra",
        "termina la compra",
        "quiero pagar",
        "pagar ahora",
        "realizar pago",
        "realiza el pago",
        "cobrar la compra",
        "cobra la compra",
        "cobrar",
        "crear venta",
        "crear la venta",
        "registrar venta",
        "registrar la venta",
        "finalizar la venta",
    ]
    if any(phrase in text for phrase in checkout_phrases):
        return VoiceIntent(raw=raw, action="checkout", quantity=0, product_name="")

    # 1) Vaciar carrito
    if (
        "vaciar carrito" in text
        or "limpiar carrito" in text
        or "borrar carrito" in text
        or "borra el carrito" in text
    ):
        return VoiceIntent(raw=raw, action="clear", quantity=0, product_name="")

    # 2) Quitar / remover / eliminar / sacar
    m = re.search(
        r"(quitar|quita|remover|remueve|eliminar|elimina|sacar|saca|borrar|borra)\s+(.*)",
        text,
    )
    if m:
        resto = (m.group(2) or "").strip()
        qty = _parse_quantity(resto)
        name = _clean_product_name(resto)
        return VoiceIntent(raw=raw, action="remove", quantity=qty, product_name=name)

    # 3) Agregar / sumar / poner
    m = re.search(
        r"(agrega|agregar|añade|añadir|suma|sumar|poner|pon)\s+(.*)",
        text,
    )
    if m:
        resto = (m.group(2) or "").strip()
        qty = _parse_quantity(resto)
        name = _clean_product_name(resto)
        return VoiceIntent(raw=raw, action="add", quantity=qty, product_name=name)

    # 4) Comprar / quiero / deseo / llevar
    m = re.search(
        r"(comprar|compra|quiero|deseo|llevar|llevo)\s+(.*)",
        text,
    )
    if m:
        resto = (m.group(2) or "").strip()
        qty = _parse_quantity(resto)
        name = _clean_product_name(resto)
        return VoiceIntent(raw=raw, action="add", quantity=qty, product_name=name)

    return VoiceIntent(raw=raw, action="unknown", quantity=1, product_name=text)


def _generate_variants(name: str) -> set[str]:
    name = name.strip().lower()
    variants = {name}
    if name.endswith("es") and len(name) > 2:
        variants.add(name[:-2])
    if name.endswith("s") and len(name) > 1:
        variants.add(name[:-1])
    return variants


def find_best_product(name_fragment: str) -> Optional[Producto]:
    if not name_fragment:
        return None

    name_fragment = name_fragment.lower().strip()
    qs = Producto.objects.filter(activo=True)

    # intento directo con variantes
    variants = _generate_variants(name_fragment)
    for v in variants:
        p = qs.filter(nombre__icontains=v).first()
        if p:
            return p

    # acortar frase desde el final
    parts = [p for p in name_fragment.split(" ") if p]
    while len(parts) > 1:
        parts.pop()
        shorter = " ".join(parts).strip()
        if not shorter:
            break
        variants = _generate_variants(shorter)
        for v in variants:
            p = qs.filter(nombre__icontains=v).first()
            if p:
                return p

    return None
