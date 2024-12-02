from odoo import fields, models


class EmployeeProject(models.Model):
    _name = 'employee.project'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Manage employee projects'
    _order = "sequence, name, id"

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Description")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    is_favorite = fields.Boolean(string="Favorite", compute="_compute_is_favorite", inverse="_inverse_is_favorite")
    favorite_user_ids = fields.Many2many('res.users', 'job_favorite_user_rel', 'job_id', 'user_id', default=_get_default_favorite_user_ids)
    active = fields.Boolean(string="Active", default=True)

    def _compute_is_favorite(self):
        """Method to compute favorite projects"""
        for rec in self:
            rec.is_favorite = self.env.user in rec.favorite_user_ids

    def _inverse_is_favorite(self):
        """Inverse method to recompute favorite projects"""
        unfavorited_em_projects = favorited_em_projects = self.env['employee.project']
        for rec in self:
            if self.env.user in rec.favorite_user_ids:
                unfavorited_em_projects |= rec
            else:
                favorited_em_projects |= rec
        favorited_em_projects.write({'favorite_user_ids': [(4, self.env.uid)]})
        unfavorited_em_projects.write({'favorite_user_ids': [(3, self.env.uid)]})
