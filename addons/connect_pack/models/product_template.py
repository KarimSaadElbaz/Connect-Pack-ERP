from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cp_family_id = fields.Many2one(
        "connect.pack.paper.family",
        string="عيلة الورق",
        index=True,
        help="التصنيف الرئيسي + الفرعي + المصنع + الدرجة. الوزن والمقاس بيتحطوا على الصنف نفسه.",
    )
    cp_main_id = fields.Many2one(
        related="cp_family_id.main_id", store=True, string="التصنيف الرئيسي"
    )
    cp_sub_id = fields.Many2one(
        related="cp_family_id.sub_id", store=True, string="التصنيف الفرعي"
    )
    cp_mill_id = fields.Many2one(
        related="cp_family_id.mill_id", store=True, string="المصنع / الدولة"
    )
    cp_grade_id = fields.Many2one(
        related="cp_family_id.grade_id", store=True, string="الدرجة"
    )
    cp_grammage = fields.Integer(string="الوزن (جم)")
    cp_width = fields.Float(string="المقاس (سم)", digits=(8, 2))
    cp_code = fields.Char(
        string="كود الصنف", compute="_compute_cp_code", store=True, index=True
    )

    @api.depends("cp_family_id.code", "cp_grammage", "cp_width")
    def _compute_cp_code(self):
        for tmpl in self:
            fam = tmpl.cp_family_id
            if fam.code and tmpl.cp_grammage and tmpl.cp_width:
                width = ("%g" % tmpl.cp_width)
                tmpl.cp_code = f"{fam.code}-{tmpl.cp_grammage}-{width}"
            elif not tmpl.cp_code:
                tmpl.cp_code = False

    @api.onchange("cp_family_id")
    def _onchange_cp_family_id(self):
        if self.cp_family_id:
            self.is_storable = True
            self.tracking = "serial"
            if not self.name:
                self.name = self.cp_family_id.name

    def _sync_paper_fields(self):
        for tmpl in self:
            if not tmpl.cp_family_id:
                continue
            vals = {}
            if not tmpl.is_storable:
                vals["is_storable"] = True
            if tmpl.tracking == "none":
                vals["tracking"] = "serial"
            if tmpl.cp_code and tmpl.default_code != tmpl.cp_code:
                vals["default_code"] = tmpl.cp_code
            if vals:
                super(ProductTemplate, tmpl).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        templates._sync_paper_fields()
        return templates

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("_cp_paper_sync"):
            self.with_context(_cp_paper_sync=True)._sync_paper_fields()
        return res
