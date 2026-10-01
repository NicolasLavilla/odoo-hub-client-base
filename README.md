# Hub Client Base — Conector para Odoo con Catalog & OCR Hub

![Odoo 19](https://img.shields.io/badge/Odoo-19.0-purple)
![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue)

Módulo base **gratuito** que conecta cualquier instalación de Odoo 19 con el **Catalog & OCR Hub** centralizado.

Proporciona la configuración compartida (URL + API Key `chub_...`), el cliente HTTP puro y el servicio Odoo `hub.client` del que dependen los módulos de procesamiento.

---

## ¿Qué incluye?

- Configuración en **Ajustes → Catalog & OCR Hub**: URL del Hub y clave API
- Botón **"Comprobar Conexión y Saldo"** para validar la clave y ver los créditos disponibles
- Servicio abstracto `hub.client` con métodos `is_configured()`, `get_status()`, `complete()`
- Cliente HTTP puro (`HubHttpClient`) 100% testeable sin Odoo
- Excepciones tipadas: `HubAuthenticationError`, `HubInsufficientCreditsError`, `HubClientError`
- Reutiliza la configuración de `supplier_catalog_client` si ya está instalado (sin duplicar credenciales)

---

## Instalación

### Requisitos

- Odoo 19.0
- Python `requests` (incluido en Odoo por defecto)

### Pasos

1. Copia la carpeta `hub_client_base/` dentro de tu directorio de addons de Odoo
2. Actualiza la lista de módulos y activa **Hub Client Base**
3. Ve a **Ajustes → Catalog & OCR Hub**, introduce la URL del Hub y tu clave `chub_...`
4. Pulsa **"Comprobar Conexión y Saldo"** para validar

---

## Dependencias para otros módulos

Este módulo es un **prerequisito** para:

| Módulo | Repo |
|--------|------|
| AI Document Processor | [odoo-ai-document-processor](https://github.com/NicolasLavilla/odoo-ai-document-processor) |
| Supplier Catalog Client | [odoo-supplier-catalog-client](https://github.com/NicolasLavilla/odoo-supplier-catalog-client) |

---

## Licencia

LGPL-3 — Libre para uso comercial y modificación, con atribución.
