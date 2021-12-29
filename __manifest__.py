{
    "name": "Prescription Extension", 
    "description": """
        Prescription Extension.
    """, 
    'version': '14.0.1.0',
    'category': 'AI',
    'author': 'Md. Abdullah Al Mamun',
    'website': 'http://www.aam-software-valey.com',
    "depends": ["base","acs_hms",'acs_laboratory'],
    "data": [
        "security/ir.model.access.csv",
        "views/prescription.xml",
    ],
    'sequence': 3,
    'installable': True,
    'application': False,
}
