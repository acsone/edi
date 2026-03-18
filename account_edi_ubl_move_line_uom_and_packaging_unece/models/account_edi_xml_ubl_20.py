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
        if not self._import_fill_invoice_line_packaging(
            invoice_line, unit_code, invoice_line.quantity
        ):
            self._import_fill_invoice_line_uom(invoice_line, unit_code)
        if (
            invoice_line.product_packaging_id
            and invoice_line.product_packaging_id.qty > 0
        ):
            price_unit_node = tree.find("./{*}Price/{*}PriceAmount")
            if price_unit_node is None:
                return res
            price_unit = float(price_unit_node.text)
            invoice_line.price_unit = price_unit / invoice_line.product_packaging_id.qty
        return res

    def _import_fill_invoice_line_uom(self, invoice_line, unit_code):
        uom_id = self.env["uom.uom"].get_uom_id_by_unece_code(unit_code)
        if uom_id:
            invoice_line.product_uom_id = uom_id
            return True
        return False

    def _import_fill_invoice_line_packaging(self, invoice_line, unit_code, quantity):
        # the unitCode attr is based on UNECE Rec 20 (UoM)
        # when Rec 21 (packaging) codes are used, they may be prefixed with "X"
        # we therefore check both formats (e.g. "8A" and "X8A")
        pl_model = self.env["product.packaging.level"]
        packaging_level_ids = pl_model.get_packaging_level_ids_by_unece_code(
            unit_code, unit_code.lstrip("X")
        )
        if not packaging_level_ids:
            return False
        product_packaging = self.env["product.packaging"].search(
            [
                ("product_id", "=", invoice_line.product_id.id),
                ("packaging_level_id", "in", packaging_level_ids),
            ],
            limit=1,
        )
        if product_packaging:
            invoice_line.product_packaging_id = product_packaging
            invoice_line.product_packaging_qty = quantity
            return True
        return False
