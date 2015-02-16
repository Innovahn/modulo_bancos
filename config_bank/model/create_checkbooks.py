# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools.translate import _

class mcheck(osv.Model):
	_name = 'checkbooks'

	#def unlink(self):
	def unlink(self,cr, uid, values, context=None):
		print "*"*40
		checkbook_id=values[0]

		#journal_id=values['journal']
		checkbook=self.browse(cr,uid,checkbook_id,context=context)
		journal_id=checkbook.journal.id
		print journal_id
		#cuantos checkbook con este mismo journal existe

		#num_journal=self.browse(cr,uid,journal_id,context=context)
		num_journal = self.search(cr, uid, [('journal', '=', journal_id)])
		print '------------------------ num_journal'
		print len(num_journal)

		if len(num_journal)==1:
			journals=self.pool.get('account.journal').browse(cr,uid,journal_id,context=context)
			if journals.show_sequence==True:
				journals.show_sequence=False

		return super(mcheck, self).unlink(cr,uid,values,context=context)	

	#Modifico el field show_sequence a True del Diario utilizado al crear una chequera
	#Este boolean oculta o muestra la pestaña bancos(secuencias) en los diarios
	def create(self, cr, uid, values, context=None):
		journal_id=values['journal']
		journals=self.pool.get('account.journal').browse(cr,uid,journal_id,context=context)
	
		if journals.show_sequence==False:
			journals.show_sequence=True
		b =super(mcheck, self).create(cr, uid, values, context=context)	
		return b
	

	#Funcion que verifica si la cuenta contable seleccionada y la cuenta acreedora del diario seleccionado son las mismas
	def onchange_journal(self,cr,uid,ids,journal_id,account_id,context=None):

	    account_journal= self.pool.get('account.journal').browse(cr, uid,journal_id, context=context)
	    account_journal_credit=account_journal.default_credit_account_id.id	
	    #message=_('The account of the checkbook and the credit account in the Journal must be the same.')

	    msg={
	    'title':_('Account Journal and checkbook do not match!'),
	    'message':_('The account of the checkbook and the credit account in the Journal must be the same.')}

	    if account_journal_credit != account_id:		
		 return {'value': {'account':None,},'warning':msg} 
	    	
 	    return {}
	
	_columns= {
		'name':fields.char("Checkbook Name"),
		'bank':fields.many2one('conf.banks',"Select Bank",required=True),
		'currency':fields.many2one('res.currency',"Currency",required=True),
		'account':fields.many2one('account.account',"Account",required=True),
		'journal':fields.many2one('account.journal',"Journal of Checkbook",required=True,domain=['|',('allow_check_writing','=',True),('checkmiscelaneous','=','True')]),
		
	}
