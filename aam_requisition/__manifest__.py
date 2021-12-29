{
    'name': 'Store Requisition System',
    'summary': 'Store Requisition System',
    'description': """
        This module will help to manage store requisition system.
    """,
    'version': '1.0.2',
    'category': 'stock',
    'author': 'Md. Abdullah Al Mamun',
    'support': 'mamun.cse.hstu@gmail.com',
    'company': "A@M.Tech",
    'depends': ['stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/default_data.xml',
        'views/ccl_requisition_views.xml',
        'views/menu_item.xml'
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 51,
    'currency': 'BDT',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
