# -*- coding: utf-8 -*-
{	
	'name' : 'Debit and Credit',
	'author': 'Grupo Innova',
	'category': 'Generic Modules/Accounting',
	'summary': '',
	'description': """   """,

	'data':[	
		'views/journal_view.xml',
		'views/mcheck_view.xml',	
		'views/reporte1.xml' ,
		'views/layouts.xml' ,
		'views/mcheck_reports.xml'
			
	],
	'update_xml' : [
			'security/groups.xml',
			'security/ir.model.access.csv',
	],
	'depends': ['base','sale','account_voucher'],
    	'installable': True,
}
