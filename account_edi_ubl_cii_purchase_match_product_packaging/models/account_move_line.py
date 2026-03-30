# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    unece_unit_code = fields.Char(
        readonly=True,
        help=(
            "Technical field storing the UNECE unit code from UBL import. "
            "Used during purchase reconciliation to identify the corresponding "
            "packaging when a purchase order line is manually selected."
        ),
    )

    def _set_product(self, product):
        self.ensure_one()
        res = super()._set_product(product)

        if self.unece_unit_code:
            if not self.env[
                "account.edi.xml.ubl_20"
            ]._import_fill_invoice_line_packaging(self, self.unece_unit_code):
                self.env["account.edi.xml.ubl_20"]._import_fill_invoice_line_uom(
                    self, self.unece_unit_code
                )
        return res
