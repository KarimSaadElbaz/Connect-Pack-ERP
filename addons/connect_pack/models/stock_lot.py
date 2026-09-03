from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    cp_roll_weight = fields.Float(
        string="الوزن الفعلي (كجم)",
        digits="Stock Weight",
        help="وزن البكرة/اللفة الفعلي وقت الاستلام.",
    )
