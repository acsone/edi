# Copyright 2026 ACSONE SA/NV, BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountEdiUblMoveLinePackaging(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Locations and leasing",
                "type": "consu",
                "uom_id": cls.uom_unit.id,
            }
        )
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "pallet 72",
                "product_id": cls.product.id,
                "qty": 72.0,
                "unece_code": "X8A",
            }
        )

    def _import_invoice(self, journal, file_path):
        with file_open(file_path, "rb") as file:
            xml_attachment = self.env["ir.attachment"].create(
                {
                    "mimetype": "application/xml",
                    "name": "test_invoice.xml",
                    "raw": file.read(),
                }
            )
        move = (
            self.env["account.journal"]
            .with_context(default_journal_id=journal.id)
            ._create_document_from_attachment(xml_attachment.id)
        )
        return move

    def test_0(self):
        """uom dozen"""
        file_path = (
            "account_edi_ubl_move_line_packaging/tests/test_files/"
            "bis3_bill_example_uom_dozen.xml"
        )
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"], file_path
        )
        line = bill.invoice_line_ids
        self.assertEqual(line.product_uom_id.name, "Dozens")
        self.assertFalse(line.product_packaging_qty)
        self.assertFalse(line.product_packaging_id)

    def test_1(self):
        """uom unit"""
        file_path = (
            "account_edi_ubl_move_line_packaging/tests/test_files/"
            "bis3_bill_example_uom_unit.xml"
        )
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"], file_path
        )
        line = bill.invoice_line_ids
        self.assertEqual(line.product_uom_id.name, "Units")
        self.assertFalse(line.product_packaging_qty)
        self.assertFalse(line.product_packaging_id)

    def test_2(self):
        """no uom"""
        file_path = (
            "account_edi_ubl_move_line_packaging/tests/test_files/"
            "bis3_bill_example_no_uom.xml"
        )
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"], file_path
        )
        line = bill.invoice_line_ids
        self.assertEqual(line.product_uom_id.name, "Units")
        self.assertFalse(line.product_packaging_qty)
        self.assertFalse(line.product_packaging_id)

    def test_3(self):
        """packaging pallet"""
        file_path = (
            "account_edi_ubl_move_line_packaging/tests/test_files/"
            "bis3_bill_example_packaging_pallet.xml"
        )
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"], file_path
        )
        line = bill.invoice_line_ids
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.product_uom_id.name, "Units")
        self.assertEqual(line.quantity, 72)
        self.assertEqual(line.product_packaging_qty, 1)
        self.assertEqual(line.product_packaging_id, self.packaging)

    def test_4(self):
        """packaging unkown"""
        self.packaging.unece_code = False
        file_path = (
            "account_edi_ubl_move_line_packaging/tests/test_files/"
            "bis3_bill_example_packaging_pallet.xml"
        )
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"], file_path
        )
        line = bill.invoice_line_ids
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.product_uom_id.name, "Units")
        self.assertEqual(line.quantity, 1)
        self.assertFalse(line.product_packaging_qty)
        self.assertFalse(line.product_packaging_id)
