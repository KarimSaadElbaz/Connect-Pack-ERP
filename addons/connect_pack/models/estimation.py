from odoo import api, fields, models


class ConnectPackEstimation(models.Model):
    _name = "connect.pack.estimation"
    _description = "Connect Pack Estimation (مقايسة)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True
    )
    date = fields.Date(
        string="Date", default=fields.Date.context_today, tracking=True
    )
    user_id = fields.Many2one(
        "res.users",
        string="Engineer",
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    note = fields.Html(string="Notes")
    line_ids = fields.One2many(
        "connect.pack.estimation.line",
        "estimation_id",
        string="Lines",
        copy=True,
    )
    amount_total = fields.Monetary(
        string="Total", compute="_compute_amount_total", store=True
    )

    @api.depends("line_ids.price_subtotal")
    def _compute_amount_total(self):
        for estimation in self:
            estimation.amount_total = sum(
                estimation.line_ids.mapped("price_subtotal")
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "connect.pack.estimation"
                    )
                    or "New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_draft(self):
        self.write({"state": "draft"})


class ConnectPackEstimationLine(models.Model):
    _name = "connect.pack.estimation.line"
    _description = "Connect Pack Estimation Line"

    estimation_id = fields.Many2one(
        "connect.pack.estimation",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one("product.product", string="Product / Item")
    name = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one("uom.uom", string="Unit")
    price_unit = fields.Float(string="Unit Price")
    currency_id = fields.Many2one(
        related="estimation_id.currency_id", string="Currency"
    )
    price_subtotal = fields.Monetary(
        string="Subtotal", compute="_compute_price_subtotal", store=True
    )

    @api.depends("quantity", "price_unit")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.display_name
                line.uom_id = line.product_id.uom_id
                line.price_unit = line.product_id.lst_price
