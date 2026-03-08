"""
Endpoint de webhook para procesar eventos de Stripe.
"""

import os
import stripe
from fastapi import FastAPI, Request, Header, HTTPException

app = FastAPI(title="Ecdotica — Pagos")

STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

stripe.api_key = STRIPE_SECRET_KEY


def _verificar_firma(payload: bytes, stripe_signature: str) -> stripe.Event:
    """Verifica la firma del webhook y retorna el evento de Stripe."""
    try:
        return stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma inválida")
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload inválido")


def _manejar_pago_exitoso(evento: stripe.Event) -> None:
    """Procesa un pago completado exitosamente."""
    intencion = evento["data"]["object"]
    print(f"[PAGO EXITOSO] id={intencion['id']} monto={intencion['amount']} moneda={intencion['currency']}")
    # TODO: actualizar estado de pedido en base de datos


def _manejar_pago_fallido(evento: stripe.Event) -> None:
    """Procesa un intento de pago fallido."""
    intencion = evento["data"]["object"]
    motivo = intencion.get("last_payment_error", {}).get("message", "desconocido")
    print(f"[PAGO FALLIDO] id={intencion['id']} motivo={motivo}")
    # TODO: notificar al usuario y actualizar estado de pedido


def _manejar_sesion_completada(evento: stripe.Event) -> None:
    """Procesa una sesión de Stripe Checkout completada."""
    sesion = evento["data"]["object"]
    print(f"[SESIÓN COMPLETADA] id={sesion['id']} cliente={sesion.get('customer')}")
    # TODO: aprovisionar acceso o producto al cliente


def _manejar_factura_pagada(evento: stripe.Event) -> None:
    """Procesa el pago de una factura o suscripción."""
    factura = evento["data"]["object"]
    print(f"[FACTURA PAGADA] id={factura['id']} suscripción={factura.get('subscription')}")
    # TODO: renovar suscripción o entregar contenido


MANEJADORES_DE_EVENTOS = {
    "payment_intent.succeeded": _manejar_pago_exitoso,
    "payment_intent.payment_failed": _manejar_pago_fallido,
    "checkout.session.completed": _manejar_sesion_completada,
    "invoice.paid": _manejar_factura_pagada,
}


@app.post("/webhook/stripe")
async def webhook_stripe(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
) -> dict:
    """Recibe y procesa eventos enviados por Stripe."""
    payload = await request.body()
    evento = _verificar_firma(payload, stripe_signature)

    manejador = MANEJADORES_DE_EVENTOS.get(evento["type"])
    if manejador:
        manejador(evento)
    else:
        print(f"[WEBHOOK] Evento no manejado: {evento['type']}")

    return {"estado": "recibido"}
