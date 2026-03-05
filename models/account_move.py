# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    fel_ids = fields.One2many("torelo.fel.document", "move_id", string="FELs")
    fel_count = fields.Integer(string="FELs", compute="_compute_fel_stats")
    fel_total_amount = fields.Monetary(string="Total FEL", compute="_compute_fel_stats", currency_field="currency_id")
    fel_ok = fields.Boolean(string="FEL OK", compute="_compute_fel_stats")

    @api.depends("fel_ids.amount_total", "fel_ids.state", "amount_total", "move_type")
    def _compute_fel_stats(self):
        for mv in self:
            if mv.move_type not in ("in_invoice", "in_refund"):
                mv.fel_total_amount = 0.0
                mv.fel_count = 0
                mv.fel_ok = False
                continue
            total = sum(mv.fel_ids.filtered(lambda r: r.state != "void").mapped("amount_total"))
            mv.fel_total_amount = total
            mv.fel_count = len(mv.fel_ids)
            mv.fel_ok = bool(mv.fel_ids and abs((total or 0.0) - (mv.amount_total or 0.0)) < 0.01)

    def action_open_fel_wizard(self):
        self.ensure_one()
        if self.move_type not in ("in_invoice", "in_refund"):
            raise UserError(_("Este botón solo aplica a Facturas de Proveedor / Reembolsos."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Crear FEL"),
            "res_model": "torelo.fel.upload.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_id": self.id,
                "active_model": "account.move",
                "active_id": self.id,
                "default_company_id": self.company_id.id,
                "default_partner_id": self.partner_id.id,
                "default_currency_id": self.currency_id.id,
            },
        }

    def action_view_fel_documents(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": _("FELs"),
            "res_model": "torelo.fel.document",
            "view_mode": "tree,form",
            "domain": [("move_id", "=", self.id)],
            "context": {"default_move_id": self.id, "default_partner_id": self.partner_id.id},
        }
        return action
