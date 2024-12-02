{
    'name': 'Employee Projects',
    'version': '16.0.0.0.1',
    'category': 'UNOW/project',
    'author': 'Joel Rivas',
    'contributors': ['Joel Rivas <joelrivas39@gmail.com>'],
    'images': ['static/description/icon.png'],
    'depends': ['hr', 'website'],
    'description': """
    Manage employee projects
""",
    'data': [
        'security/employee_project_security.xml',
        'security/ir.model.access.csv',
        'views/employee_projects.xml',
        'views/hr_employee_views.xml',
        'views/employee_projects_portal_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_frontend': [
            'employee_projects/static/**/*',
        ],
    },
}
