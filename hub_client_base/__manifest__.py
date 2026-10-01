# -*- coding: utf-8 -*-
{
    "name": "Hub Client Base",
    "version": "19.0.1.0.0",
    "summary": "Conector base con Catalog & OCR Hub para autenticación y consumo centralizado",
    "description": """
Módulo base gratuito que gestiona la conexión y autenticación con el Hub central
(Catalog & OCR Hub). Proporciona la configuración de la clave API unificada (chub_...),
la consulta de saldo de créditos universales y el cliente para procesamiento OCR/IA.
    """,
    "category": "Technical",
    "author": "Ataraxial",
    "license": "LGPL-3",
    "depends": ["base"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
