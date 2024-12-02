from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    total_projects = fields.Integer(string="Total Projects", compute="_compute_total_projects")

    def _compute_total_projects(self):
        """Compute the number of projects associated to an employee"""
        for rec in self:
            project_ids = rec.env['employee.project'].with_context(active_test=False).search([('employee_id', '=', rec.id)])
            rec.total_projects = len(project_ids)
