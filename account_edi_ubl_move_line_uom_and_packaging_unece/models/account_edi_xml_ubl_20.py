# Copyright 2026 ACSONE SA/NV, BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiXmlUbl_20(models.AbstractModel):

    _inherit = "account.edi.xml.ubl_20"

    def _import_fill_invoice_line_form(
        self, journal, tree, invoice, invoice_line, qty_factor
    ):
        res = super()._import_fill_invoice_line_form(
            journal, tree, invoice, invoice_line, qty_factor
        )
        billed_quantity_node = tree.find("./{*}InvoicedQuantity")
        unit_code = billed_quantity_node.attrib.get("unitCode")
        if not unit_code:
            return res
        if not self._import_fill_invoice_line_packaging(invoice_line, unit_code):
            self._import_fill_invoice_line_uom(invoice_line, unit_code)
        return res

    def _import_fill_invoice_line_uom(self, invoice_line, unit_code):
        uom = self.env["uom.uom"].search([("unece_code", "=", unit_code)], limit=1)
        if uom:
            invoice_line.product_uom_id = uom
            return True
        return False

    def _import_fill_invoice_line_packaging(self, invoice_line, unit_code):
        product_packaging = self.env["product.packaging"].search(
            [
                ("product_id", "=", invoice_line.product_id.id),
                ("unece_code", "=", unit_code),
            ],
            limit=1,
        )
        if product_packaging:
            invoice_line.product_packaging_id = product_packaging
            invoice_line.product_packaging_qty = invoice_line.quantity
            return True
        return False
