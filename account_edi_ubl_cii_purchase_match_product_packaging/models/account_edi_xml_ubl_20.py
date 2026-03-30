# Copyright 2026 ACSONE SA/NV
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
        invoice_line.billed_quantity = float(billed_quantity_node.text)
        unit_code = billed_quantity_node.attrib.get("unitCode")
        if not unit_code:
            return res
        invoice_line.unece_unit_code = unit_code
        return res

    def _import_fill_invoice_line_packaging(self, invoice_line, unit_code, quantity):
        res = super()._import_fill_invoice_line_packaging(
            invoice_line, unit_code, quantity
        )
        # force recomputation of the quantity
        # this is needed because after a second reconciliation with a purchase line,
        # the packaging may remain the same while the underlying quantity changes
        # without this explicit call, the computed quantity may become inconsistent
        invoice_line._compute_quantity()
        return res
