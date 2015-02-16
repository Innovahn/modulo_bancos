# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import locale
import pytz
from openerp.tools.translate import _

class account_journal(osv.osv):
	_inherit = 'account.journal'
	_columns = {
		'checkmiscelaneous_creditdebit':fields.boolean(string="Checks Debit and Credit"),
		'sequence_id_transfer':fields.many2one('ir.sequence','Sequence of Transfer'),
		'sequence_id_credeb':fields.many2one('ir.sequence','Sequence of Debit and Credit'),
		'sequence_id_deposit':fields.many2one('ir.sequence','Sequence of Deposit'),
		'show_sequence':fields.boolean('Show the sequences'),
	
	}
	_defaults = {
	'checkmiscelaneous_creditdebit' : False,
	'show_sequence' : False,
		} 
