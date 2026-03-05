# -*- coding: utf-8 -*-
from odoo import models


class PurchaseOrderAI(models.Model):
    _inherit = 'purchase.order'

    def action_open_ai_scanner(self):
        """Open AI Scanner wizard pre-configured for this PO → Vendor Bill + FEL."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': '📄 Escanear FEL desde OC %s' % self.name,
            'res_model': 'purchase.ai.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_purchase_id': self.id,
                'default_target_type': 'vendor_bill',
                'default_vendor_id': self.partner_id.id,
                'default_vendor_state': 'from_source',
                'default_currency_id': self.currency_id.id,
                'default_create_fel': True,
            },
        }
