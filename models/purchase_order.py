# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    fel_ids = fields.One2many("torelo.fel.document", "purchase_id", string="FELs")
    fel_count = fields.Integer(string="FELs", compute="_compute_fel_stats")
    fel_total_amount = fields.Monetary(string="Total FEL", compute="_compute_fel_stats", currency_field="currency_id")
    fel_ok = fields.Boolean(string="FEL OK", compute="_compute_fel_stats")

    @api.depends("fel_ids.amount_total", "fel_ids.state", "amount_total")
    def _compute_fel_stats(self):
        for po in self:
            total = sum(po.fel_ids.filtered(lambda r: r.state != "void").mapped("amount_total"))
            po.fel_total_amount = total
            po.fel_count = len(po.fel_ids)
            po.fel_ok = bool(po.fel_ids and abs((total or 0.0) - (po.amount_total or 0.0)) < 0.01)

    def action_open_fel_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Crear FEL"),
            "res_model": "torelo.fel.upload.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_purchase_id": self.id,
                "active_model": "purchase.order",
                "active_id": self.id,
                "default_company_id": self.company_id.id,
                "default_partner_id": self.partner_id.id,
            },
        }

    def action_view_fel_documents(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": _("FELs"),
            "res_model": "torelo.fel.document",
            "view_mode": "tree,form",
            "domain": [("purchase_id", "=", self.id)],
            "context": {"default_purchase_id": self.id, "default_partner_id": self.partner_id.id},
        }
        return action
