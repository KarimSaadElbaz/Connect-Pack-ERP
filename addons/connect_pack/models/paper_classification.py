from odoo import api, fields, models


class PaperMain(models.Model):
    _name = "connect.pack.paper.main"
    _description = "Paper - Main Classification (التصنيف الرئيسي)"
    _order = "code"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True, translate=False)
    legacy_code = fields.Char(string="Legacy Code")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "الكود لازم يكون فريد."),
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else rec.name


class PaperSub(models.Model):
    _name = "connect.pack.paper.sub"
    _description = "Paper - Sub Classification (التصنيف الفرعي)"
    _order = "code"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True, translate=False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "الكود لازم يكون فريد."),
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else rec.name


class PaperMill(models.Model):
    _name = "connect.pack.paper.mill"
    _description = "Paper - Mill / Country (المصنع / الدولة)"
    _order = "name"

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=True, translate=False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "الاسم مكرر."),
    ]


class PaperGrade(models.Model):
    _name = "connect.pack.paper.grade"
    _description = "Paper - Grade (الدرجة)"
    _order = "name"

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=True, translate=False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "الاسم مكرر."),
    ]


class PaperFamily(models.Model):
    _name = "connect.pack.paper.family"
    _description = "Paper Classification Family (عيلة الورق)"
    _order = "code"
    _rec_name = "code"

    main_id = fields.Many2one(
        "connect.pack.paper.main", string="التصنيف الرئيسي",
        required=True, ondelete="restrict",
    )
    sub_id = fields.Many2one(
        "connect.pack.paper.sub", string="التصنيف الفرعي",
        required=True, ondelete="restrict",
    )
    mill_id = fields.Many2one(
        "connect.pack.paper.mill", string="المصنع / الدولة",
        required=True, ondelete="restrict",
    )
    grade_id = fields.Many2one(
        "connect.pack.paper.grade", string="الدرجة",
        required=True, ondelete="restrict",
    )
    seq = fields.Integer(string="تسلسل", readonly=True, copy=False)
    code = fields.Char(
        string="كود العيلة", compute="_compute_code", store=True, index=True
    )
    name = fields.Char(
        string="الاسم", compute="_compute_name", store=True
    )
    active = fields.Boolean(default=True)
    product_count = fields.Integer(
        string="عدد الأصناف", compute="_compute_product_count"
    )

    _sql_constraints = [
        (
            "combo_uniq",
            "unique(main_id, sub_id, mill_id, grade_id)",
            "في عيلة بنفس (رئيسي / فرعي / مصنع / درجة) موجودة بالفعل.",
        ),
    ]

    @api.depends("main_id.code", "sub_id.code", "seq")
    def _compute_code(self):
        for rec in self:
            if rec.main_id.code and rec.sub_id.code and rec.seq:
                rec.code = f"{rec.main_id.code}-{rec.sub_id.code}-{rec.seq:03d}"
            else:
                rec.code = False

    @api.depends("main_id.name", "sub_id.name", "mill_id.name", "grade_id.name")
    def _compute_name(self):
        for rec in self:
            parts = [
                rec.main_id.name,
                rec.sub_id.name,
                rec.mill_id.name,
                rec.grade_id.name,
            ]
            rec.name = " ".join(p for p in parts if p)

    def _compute_product_count(self):
        data = self.env["product.template"]._read_group(
            [("cp_family_id", "in", self.ids)],
            groupby=["cp_family_id"],
            aggregates=["__count"],
        )
        counts = {family.id: count for family, count in data}
        for rec in self:
            rec.product_count = counts.get(rec.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("seq") and vals.get("main_id") and vals.get("sub_id"):
                last = self.search(
                    [
                        ("main_id", "=", vals["main_id"]),
                        ("sub_id", "=", vals["sub_id"]),
                    ],
                    order="seq desc",
                    limit=1,
                )
                vals["seq"] = (last.seq or 0) + 1
        return super().create(vals_list)

    def action_view_products(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "product.template",
            "view_mode": "list,form",
            "domain": [("cp_family_id", "=", self.id)],
            "context": {"default_cp_family_id": self.id},
        }
