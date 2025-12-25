# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiXmlUBL20(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_20"

    def _import_fill_invoice_line_form(
        self, journal, tree, invoice, invoice_line, qty_factor
    ):
        res = super()._import_fill_invoice_line_form(
            journal, tree, invoice, invoice_line, qty_factor
        )
        if journal.type != "purchase" or len(invoice_line.tax_ids) > 1:
            # this addon targets purchase imports only
            # UBL are expected to produce a single tax per line, if multiple taxes
            # were already assigned, keep the standard result to avoid unexpected
            # changes
            return res
        tax_amount_node = tree.find(".//{*}Item/{*}ClassifiedTaxCategory/{*}Percent")
        tax_unece_code_node = tree.find(".//{*}Item/{*}ClassifiedTaxCategory/{*}ID")
        if tax_amount_node is None or tax_unece_code_node is None:
            # stop if the file doesn't provide the UNECE tax code
            return res
        amount = float(tax_amount_node.text)
        tax_unece_code = tax_unece_code_node.text
        if (
            invoice_line.tax_ids.amount == amount
            and invoice_line.tax_ids.unece_categ_id.code == tax_unece_code
        ):
            # stop if the result already matches the UNECE code
            return res
        tax = self.env["account.tax"].search(
            self._get_tax_by_amount_and_unece_code_domain(
                journal, amount, tax_unece_code
            )
        )
        if tax:
            invoice_line.tax_ids = tax
        return res

    def _get_tax_by_amount_and_unece_code_domain(self, journal, amount, tax_unece_code):
        return [
            ("company_id", "=", journal.company_id.id),
            ("amount_type", "=", "percent"),
            ("type_tax_use", "=", journal.type),
            ("amount", "=", amount),
            ("unece_categ_id.code", "=", tax_unece_code),
        ]
