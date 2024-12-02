from markupsafe import Markup

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR, AND


class PortalEmployeeProjects(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        domain = self._prepare_employee_project_domain()
        if 'employee_project_count' in counters:
            employee_project_count = request.env['employee.project'].with_context(active_test=False).search_count(domain) \
                if request.env['employee.project'].check_access_rights('read', raise_exception=False) else 0
            values['employee_project_count'] = employee_project_count
        return values

    # ------------------------------------------------------------
    # My Employee Projects
    # ------------------------------------------------------------

    def _employee_projects_get_page_view_values(self, employee_project, access_token, **kwargs):
        values = {
            'page_name': 'employee_project',
            'employee_project': employee_project,
        }
        return self._get_page_view_values(employee_project, access_token, values, 'my_employee_projects_history', False, **kwargs)

    def _prepare_employee_project_domain(self):
        return [('employee_id', '=', request.env.user.employee_id.id)]

    def _prepare_searchbar_sortings(self):
        return {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'id': {'label': _('ID'), 'order': 'id'},
        }

    def _prepare_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('id', 'ilike', search)])
            search_domain.append([('name', 'ilike', search)])
            search_domain.append([('employee_id.name', 'ilike', search)])
        if search_in in ('employee', 'all'):
            search_domain.append([('employee_id.name', 'ilike', search)])
        if search_in in ('id', 'all'):
            search_domain.append([('id', '=', search)])
        if search_in in ('name', 'all'):
            search_domain.append([('name', 'ilike', search)])
        return OR(search_domain)

    @http.route(['/my/employee-projects', '/my/employee-projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_employee_projects(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        EmployeeProject = request.env['employee.project'].with_context(active_test=False)
        domain = self._prepare_employee_project_domain()

        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby or sortby not in searchbar_sortings:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        employee_project_count = EmployeeProject.search_count(domain)

        pager = portal_pager(
            url="/my/employee-projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=employee_project_count,
            page=page,
            step=self._items_per_page
        )

        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'id': {'input': 'id', 'label': _('Search in Reference')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'employee': {'input': 'employee', 'label': _('Search in Employee')},
        }

        search_domain = self._prepare_search_domain(search_in, search)
        domain = AND([domain, search_domain])
        employee_projects = EmployeeProject.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_employee_projects_history'] = employee_projects.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'employee_projects': employee_projects,
            'current_employee': request.env.user.employee_id.id,
            'page_name': 'employee_project',
            'default_url': '/my/employee-projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("employee_projects.portal_my_employee_projects", values)

    @http.route(['/my/employee-projects/<int:employee_project_id>'], type='http', auth="user", website=True)
    def portal_my_task(self, employee_project_id, report_type=None, access_token=None, project_sharing=False, **kw):
        try:
            employee_project_sudo = self._document_check_access('employee.project', employee_project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('pdf', 'html', 'text'):
            return self._show_task_report(task_sudo, report_type, download=kw.get('download'))

        values = self._employee_projects_get_page_view_values(employee_project_sudo, access_token, **kw)
        return request.render("employee_projects.portal_my_employee_project", values)

    @http.route('/my/employee-projects/create', type='json', auth="user")
    def portal_create_employee_projects(self, name, employee_id, date_start, date_end, description="", **kw):
        """Method used to create employee projects from js code"""
        vals = {
            'name': name,
            'employee_id': employee_id,
            'date_start': date_start,
            'date_end': date_end,
            'description': description,
        }

        project_ids = request.env['employee.project'].sudo().create(vals)

        ret_vals = {}
        if project_ids:
            ret_vals = {
                'success': True,
                'redirect_url': '/my/employee-projects'
            }
        else:
            ret_vals = {
                'success': False,
                'error': 'Project creation failed.'
                }

        return ret_vals
