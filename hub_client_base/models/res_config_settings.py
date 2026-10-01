# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hub_url = fields.Char(
        string="URL del Hub",
        config_parameter="hub_client_base.hub_url",
        default="http://localhost:8000",
        help="URL base del servidor central Catalog & OCR Hub (ej: https://hub.example.com).",
    )
    hub_api_key = fields.Char(
        string="Clave API del Hub",
        config_parameter="hub_client_base.api_key",
        help="Clave API única asignada a esta instalación (empieza por chub_...). "
        "Autoriza tanto la descarga de catálogos como el procesamiento OCR.",
    )

    def action_test_hub_connection(self):
        """Comprueba la conexión con el Hub y muestra los datos del cliente y saldo."""
        self.ensure_one()
        status_data = self.env["hub.client"].get_status()
        client_name = status_data.get("name", "Desconocido")
        sector = status_data.get("sector", "general")
        credits_balance = status_data.get("credits_balance", 0)

        message = (
            f"Conexión con el Hub confirmada.\n"
            f"Empresa: {client_name}\n"
            f"Sector: {sector.capitalize()}\n"
            f"Saldo disponible: {credits_balance} documentos."
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Hub Central Conectado",
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }
