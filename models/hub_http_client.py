# -*- coding: utf-8 -*-
"""Cliente HTTP puro en Python para comunicarse con Catalog & OCR Hub.

Diseñado sin dependencias del ORM de Odoo para permitir pruebas unitarias
completamente aisladas con pytest y mocks de sesión.
"""
import logging
import requests

_logger = logging.getLogger(__name__)


class HubClientError(Exception):
    """Error genérico de comunicación con el Hub central."""


class HubAuthenticationError(HubClientError):
    """Clave API incorrecta o cliente inactivo."""


class HubInsufficientCreditsError(HubClientError):
    """Saldo de créditos insuficiente para procesar el documento."""

    def __init__(self, message, balance=0, required=1):
        super().__init__(message)
        self.balance = balance
        self.required = required


class HubHttpClient:
    """Cliente HTTP para Catalog & OCR Hub."""

    def __init__(self, base_url, api_key, timeout=60, session=None):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = (api_key or "").strip()
        self.timeout = timeout
        self._session = session or requests

    def _headers(self):
        if not self.api_key:
            raise HubAuthenticationError(
                "La clave API del Hub no está configurada. Introduce tu API Key (chub_...) en Ajustes."
            )
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_status(self):
        """Consulta el estado del cliente y su saldo de créditos en el Hub."""
        if not self.base_url:
            raise HubClientError("La URL del Hub no está configurada.")

        url = f"{self.base_url}/api/v1/ocr/status"
        try:
            response = self._session.get(url, headers=self._headers(), timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            _logger.error("Fallo de conexión al consultar estado del Hub: %s", exc)
            raise HubClientError(f"No se pudo conectar con el Hub en {self.base_url}: {exc}") from exc

        if response.status_code == 401:
            raise HubAuthenticationError(
                "La clave API del Hub no es válida o la cuenta del cliente está inactiva."
            )
        if response.status_code >= 400:
            raise HubClientError(f"El Hub respondió con error HTTP {response.status_code}: {response.text[:300]}")

        try:
            return response.json()
        except ValueError as exc:
            raise HubClientError("Respuesta inválida del Hub (no es JSON)") from exc

    def process_ocr(self, prompt, system=None, images=None, document_type="auto", source_platform="odoo_19"):
        """Envía un documento para extracción de datos por IA/OCR centralizado."""
        if not self.base_url:
            raise HubClientError("La URL del Hub no está configurada.")

        url = f"{self.base_url}/api/v1/ocr/process"
        payload = {
            "prompt": prompt,
            "system": system,
            "images": images or [],
            "document_type": document_type,
            "source_platform": source_platform,
        }

        try:
            response = self._session.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as exc:
            _logger.error("Timeout al procesar OCR en el Hub: %s", exc)
            raise HubClientError("El servidor del Hub tardó demasiado en responder (timeout).") from exc
        except requests.exceptions.RequestException as exc:
            _logger.error("Error de conexión al procesar OCR con el Hub: %s", exc)
            raise HubClientError(f"Error de conexión con el Hub: {exc}") from exc

        if response.status_code == 401:
            raise HubAuthenticationError(
                "La clave API del Hub es incorrecta o no tiene autorización."
            )
        if response.status_code == 402:
            detail = {}
            try:
                detail = response.json().get("detail", {})
            except Exception:
                pass
            balance = detail.get("credits_balance", 0) if isinstance(detail, dict) else 0
            required = detail.get("credits_required", 1) if isinstance(detail, dict) else 1
            raise HubInsufficientCreditsError(
                f"Has agotado tu saldo de créditos OCR. Saldo actual: {balance}, Necesarios: {required}. "
                "Recarga créditos en tu panel para continuar procesando documentos.",
                balance=balance,
                required=required,
            )
        if response.status_code >= 400:
            raise HubClientError(f"Error HTTP {response.status_code} devuelto por el Hub: {response.text[:300]}")

        try:
            data = response.json()
            return data
        except ValueError as exc:
            raise HubClientError("Respuesta del Hub no tiene formato JSON válido") from exc

    def complete(self, prompt, system=None, images=None, **kwargs):
        """Adaptador compatible con la interfaz LLMProvider.complete de Odoo."""
        res = self.process_ocr(
            prompt=prompt,
            system=system,
            images=images,
            document_type=kwargs.get("document_type", "auto"),
            source_platform=kwargs.get("source_platform", "odoo_19"),
        )
        return {
            "content": res.get("content", ""),
            "credits_remaining": res.get("credits_remaining"),
        }
