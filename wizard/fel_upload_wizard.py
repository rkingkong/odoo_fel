# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FelUploadWizard(models.TransientModel):
    _name = "torelo.fel.upload.wizard"
    _description = "Subir FEL (Wizard)"

    purchase_id = fields.Many2one("purchase.order", string="Pedido de Compra", readonly=True)
    move_id = fields.Many2one("account.move", string="Factura", readonly=True)

    company_id = fields.Many2one("res.company", string="Compañía", required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one("res.partner", string="Proveedor", required=True)

    fel_uuid = fields.Char(string="UUID")
    fel_series = fields.Char(string="Serie")
    fel_number = fields.Char(string="Número")
    fel_date = fields.Date(string="Fecha FEL")

    amount_total = fields.Monetary(string="Monto Total FEL", required=True, currency_field="currency_id")
    amount_tax = fields.Monetary(string="Impuestos FEL", currency_field="currency_id")
    amount_untaxed = fields.Monetary(string="Monto Sin Impuestos FEL", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", string="Moneda", default=lambda self: self.env.company.currency_id)

    fel_file = fields.Binary(string="Archivo FEL", required=True)
    fel_filename = fields.Char(string="Nombre Archivo", required=True)

    notes = fields.Text(string="Notas")
    state = fields.Selection([
        ("uploaded", "Subido"),
        ("validated", "Validado"),
        ("void", "Anulado"),
    ], string="Estado", default="uploaded")

    def action_confirm(self):
        self.ensure_one()
        if not self.purchase_id and not self.move_id:
            # In case user opens wizard outside context
            raise UserError(_("No hay documento activo (PO o Factura). Abra el wizard desde el botón 'Crear FEL'."))

        fel = self.env["torelo.fel.document"].create({
            "purchase_id": self.purchase_id.id or False,
            "move_id": self.move_id.id or False,
            "company_id": self.company_id.id,
            "partner_id": self.partner_id.id,
            "fel_uuid": self.fel_uuid,
            "fel_series": self.fel_series,
            "fel_number": self.fel_number,
            "fel_date": self.fel_date,
            "amount_total": self.amount_total,
            "amount_tax": self.amount_tax,
            "amount_untaxed": self.amount_untaxed,
            "fel_file": self.fel_file,
            "fel_filename": self.fel_filename,
            "notes": self.notes,
            "state": self.state,
        })

        # Post message in chatter
        if self.purchase_id:
            self.purchase_id.message_post(body=_("FEL creado: %s") % (fel.name,))
        if self.move_id:
            self.move_id.message_post(body=_("FEL creado: %s") % (fel.name,))

        return {"type": "ir.actions.act_window_close"}
