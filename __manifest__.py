# -*- coding: utf-8 -*-
{
    "name": "TORELO - FEL (Adjuntar FEL a PO y Facturas)",
    "summary": "Subir y controlar archivos FEL en Pedidos de Compra y Facturas de Proveedor",
    "version": "16.0.1.0.0",
    "category": "Purchases/Accounting",
    "author": "TORELO",
    "license": "LGPL-3",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/fel_document_views.xml",
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
        "wizard/fel_upload_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}
