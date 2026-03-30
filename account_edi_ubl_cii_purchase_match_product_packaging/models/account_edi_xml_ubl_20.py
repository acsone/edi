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
        unit_code = billed_quantity_node.attrib.get("unitCode")
        if not unit_code:
            return res
        invoice_line.unece_unit_code = unit_code
        return res

    def test_0(self):
        """unitCode is stored into move.line"""
        file_path = (
            "account_edi_ubl_cii_purchase_match_product_packaging/tests/test_files/"
            "bis3_bill_example_uom_dozen.xml"
        )
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"], file_path
        )
        line = bill.invoice_line_ids
        self.assertEqual(line.product_uom_id.name, "Dozens")
        self.assertFalse(line.product_packaging_qty)
        self.assertFalse(line.product_packaging_id)
