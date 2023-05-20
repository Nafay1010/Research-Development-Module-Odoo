{
    'name': 'Research and Development',
    'version': '16.0.1.0.0',
    'author': 'Nafay',
    'category': 'Research and Development Management System',
    'license': "AGPL-3",
    'Summary': 'A Module For Research and Development',
    'images': ['static/description/icon.jpg'],
    'depends': ['base', 'hr'],
    'data': [
        'security/cms_RD_security.xml',
        'security/ir.model.access.csv', 
        'views/cms_RD_view.xml',
        'views/hr_employee_view.xml',
        'views/cms_RD_menu.xml', 
        ],
        
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
