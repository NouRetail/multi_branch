# See LICENSE file for full copyright and licensing details.
"""Account Invoice (Move) Model."""

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    """Sale Advance Payment Inv."""

    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, sale_orders):
        """Overridden method to update branch in invoice(move)."""
        invoices = super(SaleAdvancePaymentInv, self)._create_invoices(
            sale_orders
        )
        for invoice in invoices:
            order = invoice.line_ids.sale_line_ids.order_id
            if order and order.branch_id:
                invoice.write({"branch_id": order.branch_id.id})
                if invoice.invoice_line_ids:
                    invoice.invoice_line_ids.write({"branch_id": order.branch_id.id})
        return invoices


class AccountInvoiceReport(models.Model):
    """Account Invoice Report."""

    _inherit = "account.invoice.report"

    branch_id = fields.Many2one("multi.branch", string="Branch Name")

    def _select(self):
        return (
            super(AccountInvoiceReport, self)._select()
            + ", move.branch_id as branch_id"
        )

    """Method is not in use from Odoo version 14."""
    # def _group_by(self):
    #     return super(AccountInvoiceReport, self)._group_by() + ", move.branch_id"
