# -*- coding: utf-8 -*-

from openerp.osv import fields, osv



class banks(osv.Model):
	_name = 'conf.banks'

	_columns= {
		'name':fields.char("Bank Name"),
	}
