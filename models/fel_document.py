# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FelDocument(models.Model):
    _name = "torelo.fel.document"
    _description = "Documento FEL"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="FEL", required=True, copy=False, readonly=True, default=lambda self: _("New"))

    # Link to PO or Vendor Bill
    purchase_id = fields.Many2one("purchase.order", string="Pedido de Compra", index=True, tracking=True)
    move_id = fields.Many2one("account.move", string="Factura de Proveedor", index=True, tracking=True,
                              domain="[('move_type','in',('in_invoice','in_refund'))]")

    company_id = fields.Many2one("res.company", string="Compañía", required=True, default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one("res.partner", string="Proveedor", index=True)
    currency_id = fields.Many2one("res.currency", string="Moneda", related="company_id.currency_id", readonly=True)

    fel_uuid = fields.Char(string="UUID", tracking=True)
    fel_series = fields.Char(string="Serie")
    fel_number = fields.Char(string="Número")
    fel_date = fields.Date(string="Fecha FEL")

    amount_total = fields.Monetary(string="Monto Total FEL", tracking=True, currency_field="currency_id")
    amount_tax = fields.Monetary(string="Impuestos FEL", currency_field="currency_id")
    amount_untaxed = fields.Monetary(string="Monto Sin Impuestos FEL", currency_field="currency_id")

    state = fields.Selection([
        ("draft", "Borrador"),
        ("uploaded", "Subido"),
        ("validated", "Validado"),
        ("void", "Anulado"),
    ], string="Estado FEL", default="uploaded", tracking=True)

    fel_file = fields.Binary(string="Archivo FEL", attachment=True, tracking=True)
    fel_filename = fields.Char(string="Nombre Archivo")

    notes = fields.Text(string="Notas")

    matches_total = fields.Boolean(string="Monto coincide", compute="_compute_matches_total", store=True)

    @api.depends("amount_total", "purchase_id.amount_total", "move_id.amount_total", "purchase_id.currency_id", "move_id.currency_id")
    def _compute_matches_total(self):
        for rec in self:
            target_total = 0.0
            if rec.move_id:
                target_total = rec.move_id.amount_total or 0.0
            elif rec.purchase_id:
                target_total = rec.purchase_id.amount_total or 0.0
            rec.matches_total = bool(rec.amount_total and abs((rec.amount_total or 0.0) - (target_total or 0.0)) < 0.01)

    @api.constrains("purchase_id", "move_id")
    def _check_link(self):
        for rec in self:
            if not rec.purchase_id and not rec.move_id:
                raise ValidationError(_("El documento FEL debe estar ligado a un Pedido de Compra o a una Factura."))
            if rec.purchase_id and rec.move_id:
                raise ValidationError(_("El documento FEL no puede estar ligado a ambos (PO y Factura) al mismo tiempo."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("torelo.fel.document") or _("New")
        records = super().create(vals_list)
        # Auto-fill partner based on linked doc
        for rec in records:
            if not rec.partner_id:
                if rec.move_id and rec.move_id.partner_id:
                    rec.partner_id = rec.move_id.partner_id.id
                elif rec.purchase_id and rec.purchase_id.partner_id:
                    rec.partner_id = rec.purchase_id.partner_id.id
        return records
