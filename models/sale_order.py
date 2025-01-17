# See LICENSE file for full copyright and licensing details.
"""Res Partner Model."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """Sale Order Model."""

    _inherit = "sale.order"

    branch_id = fields.Many2one(
        "multi.branch",
        string="Branch Name",
        default=lambda self: self.env.user.branch_id,
        ondelete="restrict",
    )

    @api.model
    def default_get(self, fields):
        """Method to set default warehouse of user branch."""
        result = super(SaleOrder, self).default_get(fields)
        company = self.env.company.id

        warehouse_id = self.env["stock.warehouse"].search(
            ['|', ("branch_id", "=", self.branch_id.id), ("company_id", "=", company)],
            limit=1,
        )
        print("\n\n\nwarehouse_id warehouse_id warehouse_id",warehouse_id)
        result.update({"warehouse_id": warehouse_id and warehouse_id.id})
        return result

    @api.onchange("opportunity_id")
    def opportunity_branch_id(self):
        if self.opportunity_id:
            self.branch_id = self.opportunity_id.branch_id

    @api.onchange("branch_id")
    def _onchange_branch_id(self):
        """Onchange method to update the warehouse_id in sale order."""
        company = self.env.company.id or False
        for sale in self:
            branch_id = sale.branch_id.id
            company = sale.company_id.id or company
            warehouse_id = self.env["stock.warehouse"].search(
                [("branch_id", "=", branch_id), ("company_id", "=", company)], limit=1
            )
            sale.warehouse_id = warehouse_id and warehouse_id.id or False

    def _prepare_invoice(self):
        """Overridden this method to update branch_id in move(Invoice Vals)."""
        self.ensure_one()
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if invoice_vals and self.branch_id:
            invoice_vals.update(
                {"branch_id": self.branch_id and self.branch_id.id or False}
            )
        return invoice_vals


class SaleOrderLine(models.Model):
    """Sale Order Line."""

    _inherit = "sale.order.line"

    branch_id = fields.Many2one(
        "multi.branch", string="Branch Name", related="order_id.branch_id", store=True
    )

    def _prepare_invoice_line(self, **optional_values):
        """Overridden method to add branch in move line (invoice line)."""
        self.ensure_one()
        line_vals = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self and self.order_id and self.order_id.branch_id:
            line_vals.update({"branch_id": self.order_id.branch_id.id})
        return line_vals


class SaleReport(models.Model):
    """Sale Report."""

    _inherit = "sale.report"

    branch_id = fields.Many2one("multi.branch", string="Branch Name")

    def _group_by_sale(self):
        groupby_ = super(SaleReport, self)._group_by_sale()
        groupby_ += ", s.branch_id"
        return groupby_

    def _select_sale(self):
        select_ = super(SaleReport, self)._select_sale()
        select_ += ", s.branch_id as branch_id"
        return select_
