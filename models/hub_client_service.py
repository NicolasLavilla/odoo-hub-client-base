# -*- coding: utf-8 -*-
import os
from odoo import models
from odoo.exceptions import UserError
from .hub_http_client import (
    HubAuthenticationError,
    HubClientError,
    HubHttpClient,
    HubInsufficientCreditsError,
)


class HubClientService(models.AbstractModel):
    _name = "hub.client"
    _description = "Servicio de Conexión con Catalog & OCR Hub"

    def _get_hub_config(self):
        """Lee la configuración del Hub desde parámetros del sistema o entorno.
        
        Permite compartir la misma clave API y URL con supplier_catalog_client.
        """
        params = self.env["ir.config_parameter"].sudo()

        hub_url = (
            os.environ.get("HUB_URL")
            or params.get_param("hub_client_base.hub_url")
            or params.get_param("supplier_catalog_client.hub_url")
            or "http://localhost:8000"
        ).strip()

        api_key = (
            os.environ.get("HUB_API_KEY")
            or params.get_param("hub_client_base.api_key")
            or params.get_param("supplier_catalog_client.api_key")
            or ""
        ).strip()

        return hub_url, api_key

    def get_client(self):
        """Retorna una instancia configurada de HubHttpClient."""
        hub_url, api_key = self._get_hub_config()
        return HubHttpClient(base_url=hub_url, api_key=api_key)

    def is_configured(self):
        """Indica si el Hub tiene configurada una clave API."""
        _, api_key = self._get_hub_config()
        return bool(api_key)

    def get_status(self):
        """Consulta el estado del cliente y saldo en el Hub con control de errores."""
        client = self.get_client()
        try:
            return client.get_status()
        except HubAuthenticationError as exc:
            raise UserError(str(exc)) from exc
        except HubClientError as exc:
            raise UserError(str(exc)) from exc

    def complete(self, prompt, system=None, images=None, **kwargs):
        """Procesa una petición OCR a través del Hub central con manejo de errores."""
        client = self.get_client()
        try:
            return client.complete(prompt=prompt, system=system, images=images, **kwargs)
        except HubInsufficientCreditsError as exc:
            raise UserError(str(exc)) from exc
        except HubAuthenticationError as exc:
            raise UserError(str(exc)) from exc
        except HubClientError as exc:
            raise UserError(f"Error en el servicio de IA/OCR central: {exc}") from exc
