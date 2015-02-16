# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
import locale
import pytz
from openerp.tools.translate import _
import time
from itertools import ifilter
class debitcredit(osv.Model):
	_order = 'date desc'
	_name = 'debit.credit'

	def cancel_voucher(self, cr, uid, ids, context=None):
		reconcile_pool = self.pool.get('account.move.reconcile')
		move_pool = self.pool.get('account.move')
		move_line_pool = self.pool.get('account.move.line')
		for voucher in self.browse(cr, uid, ids, context=context):
			# refresh to make sure you don't unlink an already removed move
			voucher.refresh()
			for line in voucher.move_ids:
				# refresh to make sure you don't unreconcile an already unreconciled entry
				line.refresh()
				if line.reconcile_id:
					move_lines = [move_line.id for move_line in line.reconcile_id.line_id]
					move_lines.remove(line.id)
					reconcile_pool.unlink(cr, uid, [line.reconcile_id.id])
					if len(move_lines) >= 2:
						move_line_pool.reconcile_partial(cr, uid, move_lines, 'auto',context=context)
			if voucher.move_id:
				move_pool.button_cancel(cr, uid, [voucher.move_id.id])
				move_pool.unlink(cr, uid, [voucher.move_id.id])
		res = {
		    'state':'cancel',
		    'move_id':False,
		}
		self.write(cr, uid, ids, res)
		return True


	def create(self, cr, uid, values, context=None):
		seq_obj = self.pool.get('ir.sequence')
		name = "/"
		journal_obj = self.pool.get('account.journal')
		diario = journal_obj.browse(cr,uid,values['journal_id'],context=context)

		
		if diario.sequence_id_credeb:
			if not diario.sequence_id_credeb.active:
				raise osv.except_osv(_('Configuration Error !'),_('Please activate the sequence of selected journal !'))
			c = dict(context)
			name = seq_obj.next_by_id(cr, uid, diario.sequence_id_credeb.id, context=c)
			
		else:
			raise osv.except_osv(_('Configuration Error !'),_('Please select the sequence of selected journal !'))
		
		values['number']=name
		b =super(debitcredit, self).create(cr, uid, values, context=context)	
		return b

#def onchange_journal(self,cr,uid,ids,journal_id,account_id,context=None):
#	    test_user(self,cr, uid, ids,args=None, context=None):



	def action_validate(self, cr, uid, ids, context=None):
		for debitcredit in self.browse(cr,uid,ids,context=context):
			if len(debitcredit.mcheck_ids) > 0:
				total=0
				totald=0
				totalc=0
				

				for lines in debitcredit.mcheck_ids:
					total+=lines.amount
					if debitcredit.type_dc=='dr':
						totald+=lines.amount
					if debitcredit.type_dc=='cr':
						totalc+=lines.amount
				
				if (totald or totalc) > 0:
					print "entro if (totald or totalc)"
					lines_array=[]
					name = "/"
					if debitcredit.number:
						name=debitcredit.number
					amove_obj= self.pool.get('account.move')
					amovedata={}
					amovedata['journal_id']=debitcredit.journal_id.id
					amovedata['name']=name
					amovedata['ref']=debitcredit.reference					
					seq_obj = self.pool.get('ir.sequence')

					move_id= amove_obj.create(cr,uid,amovedata)
					mline_obj= self.pool.get('account.move.line')
					for lines in debitcredit.mcheck_ids:
						lines_col={}
						lines_col['move_id']=move_id
						lines_col['name']=lines.name  or '/'
						if debitcredit.type_dc == 'dr':
							lines_col['credit']=0
							lines_col['debit']=lines.amount
						else:
							lines_col['credit']=lines.amount		
							lines_col['debit']=0
						lines_col['move_id']=move_id
						lines_col['date']=debitcredit.date
						lines_col['account_id']=lines.account_id.id
						lines_col['debitcredit_id']=debitcredit.id
						lines_array.append(lines_col)

				

					mline_data={}
					mline_data['move_id']=move_id
					mline_data['name']= name

					if debitcredit.type_dc == 'dr':
						mline_data['credit']=totald
						mline_data['debit']=0
					elif debitcredit.type_dc == 'cr':
						mline_data['debit']=totalc
						mline_data['credit']=0

					mline_data['date']=debitcredit.date
					mline_data['account_id']=debitcredit.journal_id.default_credit_account_id.id
					mline_data['debitcredit_id']=debitcredit.id
					#"antes de crear account.move.line"
					line_id= mline_obj.create(cr,uid,mline_data)

					#"despues de crear account.move.line"
					# mline_data
					for lines2 in lines_array:
						mline_obj.create(cr,uid,lines2)
					return self.write(cr, uid, ids, {'state':'posted','number':name,'move_id':move_id}, context=context)
				else:
					raise osv.except_osv(_('amount total is 0'),_("the value of total is 0") )
			else:
				raise osv.except_osv(_('No lines'),_("select more than one line") )
		
	def _get_totald(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.mcheck_ids) > 0:
				total=0
				totald=0
				totalc=0
				for lines in mcheck.mcheck_ids:
					total+=lines.amount
					if lines.type=='dr':
						totald+=lines.amount
					if lines.type=='cr':
						totalc+=lines.amount
			result[mcheck.id]=self.addComa('%.2f'%(totald-totalc))
		return result	

	def _get_totaldebit(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.move_ids) > 0:
				totald=0
				for lines in mcheck.move_ids:
					totald+=lines.debit
			result[mcheck.id]=self.addComa('%.2f'%(totald))
		return result	

	def _get_totalcredit(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.move_ids) > 0:
				totalc=0
				for lines in mcheck.move_ids:
					totalc+=lines.credit
			result[mcheck.id]=self.addComa('%.2f'%(totalc))
		return result	


	def _get_totalt(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for mcheck in self.browse(cr,uid,ids,context=context):
			if len(mcheck.mcheck_ids) > 0:
				total=0
				totald=0
				totalc=0
				for lines in mcheck.mcheck_ids:
					total+=lines.amount
					if lines.type=='dr':
						totald+=lines.amount
					if lines.type=='cr':
						totalc+=lines.amount
			if(mcheck.journal_id.currency):
				a=self.to_word(totald-totalc,mcheck.journal_id.currency.name)
			else:
				a=self.to_word(totald-totalc,'HNL')
			print a
			result[mcheck.id]=a
		return result
		    # (self, cr, uid, values, context=None):
#		     (self, cr, uid, ids,name,args=None,context=None)

	def _calcula_precio(self, cr, uid, ids,name,args=None,context=None):
		result={}
		for invoice in self.browse(cr,uid,ids,context=context):
			total=invoice.quantity * invoice.price_unit
			total_desc=total-(invoice.quantity * invoice.discount_amount)			
			self.write(cr,uid,invoice.id,{'p_subtotal':total_desc},context=context)
			result[invoice.id]=total_desc
		return result

	'''
	def test_user(self,cr, uid, ids,args=None, context=None):
		result= {}
		#print uid
		
		companys = self.pool.get('res.company')
		#print "user pool get--------------------------------------"
		#print companys
		res_companys=companys.search(cr,uid,[('user_ids','=',uid)])#busco las compañias que pertenecen a este usuario

		#print "res_user filtrado---------------"
		#print res_companys
		#ids_user=user.read(cr,uid,['uid'],['cid','user_id'])

		#user = self.pool.get('res_company_users_rel').browse(cr,uid,args[][],context=context)
		#for users in user.browse(cr,uid,ids,context):
		#	print users.cid
		#	company=users.cid

		#print "*"*40
		return result

	'''	

		
	_columns={
        'move_id':fields.many2one('account.move', 'Account Entry', copy=False),
	                'journal_id':fields.many2one('account.journal', 'Journal',required=True ),
		'name':fields.text('Memo',  ),
		'date':fields.date('Date',  select=True, 
                           help="Effective date for accounting entries", ),
		'amount': fields.function(_get_totald,type='char',string='Total', ),
		'amountdebit': fields.function(_get_totaldebit,type='char',string='Total', ),
		'amountcredit': fields.function(_get_totalcredit,type='char',string='Total',),
		'amounttext': fields.function(_get_totalt,type='char',string='Total',),
		'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), ),
		'reference': fields.char('Pay to', 
		                         help="Transaction reference number.", copy=False,required=True),
		'number': fields.char('Number'),
		'obs':fields.text('obs',  ),
		'type_dc':fields.selection([('dr','Debit'),('cr','Credit')], 'Dr/Cr',required=True),
        	'type':fields.selection([
			('sale','Sale'),
			('purchase','Purchase'),
			('payment','Payment'),
			('receipt','Receipt'),
			],'Default Type', ),
		

		
		
		'mcheck_ids' :fields.one2many('debitcredit_lines','debitcredit_id',string="checks lines"),
		'move_ids' :fields.one2many('account.move.line','debitcredit_id',string="checks lines"),
		'state':fields.selection(
		    [('draft','Draft'),
		     ('cancel','Cancelled'),
		     ('proforma','Pro-forma'),
		     ('posted','Posted')
		    ], 'Status', 
		    help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
		                \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
		                \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
		                \n* The \'Cancelled\' status is used when user cancel voucher.'),


	}
	_defaults = {
	'state' : 'draft',
	'type' : 'payment',
 	'date': lambda *a: time.strftime('%Y-%m-%d'),
		} 




	# Para definir la moneda me estoy basando en los código que establece el ISO 4217
	# Decidí poner las variables en inglés, porque es más sencillo de ubicarlas sin importar el país
	# Si, ya sé que Europa no es un país, pero no se me ocurrió un nombre mejor para la clave.


	def to_word(self,number, mi_moneda):
	    valor= number
	    print valor
	    number=int(number)
	    print valor-number
	    centavos=int((round(valor-number,2))*100)
	    print centavos
	    UNIDADES = (
	    '',
	    'UN ',
	    'DOS ',
	    'TRES ',
	    'CUATRO ',
	    'CINCO ',
	    'SEIS ',
	    'SIETE ',
	    'OCHO ',
	    'NUEVE ',
	    'DIEZ ',
	    'ONCE ',
	    'DOCE ',
	    'TRECE ',
	    'CATORCE ',
	    'QUINCE ',
	    'DIECISEIS ',
	    'DIECISIETE ',
	    'DIECIOCHO ',
	    'DIECINUEVE ',
	    'VEINTE '
	)

	    DECENAS = (
	    'VENTI',
	    'TREINTA ',
	    'CUARENTA ',
	    'CINCUENTA ',
	    'SESENTA ',
	    'SETENTA ',
	    'OCHENTA ',
	    'NOVENTA ',
	    'CIEN '
	)

	    CENTENAS = (
	    'CIENTO ',
	    'DOSCIENTOS ',
	    'TRESCIENTOS ',
	    'CUATROCIENTOS ',
	    'QUINIENTOS ',
	    'SEISCIENTOS ',
	    'SETECIENTOS ',
	    'OCHOCIENTOS ',
	    'NOVECIENTOS '
	)
	    MONEDAS = (
		    {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
		    {'country': u'Honduras', 'currency': 'HNL', 'singular': u'Lempira', 'plural': u'Lempiras', 'symbol': u'L'},
		    {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
		    {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
		    {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
		    {'country': u'Perú', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
		    {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
		)
	    print self.convert_group('003')
	    if mi_moneda != None:
		try:
		    moneda = ifilter(lambda x: x['currency'] == mi_moneda, MONEDAS).next()
		    if number < 2:
		        moneda = moneda['singular']
		    else:
		        moneda = moneda['plural']
		except:
		    return "Tipo de moneda inválida"
	    else:
		moneda = ""
	    """Converts a number into string representation"""
	    converted = ''

	    if not (0 < number < 999999999):
		return 'No es posible convertir el numero a letras'

	    number_str = str(number).zfill(9)
	    millones = number_str[:3]
	    miles = number_str[3:6]
	    cientos = number_str[6:]

	    if(millones):
		if(millones == '001'):
		    converted += 'UN MILLON '
		elif(int(millones) > 0):
		    converted += '%sMILLONES ' % self.convert_group(millones)

	    if(miles):
		if(miles == '001'):
		    converted += 'MIL '
		elif(int(miles) > 0):
		    converted += '%sMIL ' % self.convert_group(miles)

	    if(cientos):
		if(cientos == '001'):
		    converted += 'UN '
		elif(int(cientos) > 0):
		    converted += '%s ' % self.convert_group(cientos)
	    if(centavos)>0:
		converted+= "con %2i/100 "%centavos
	    converted += moneda

	    return converted.title()


	def convert_group(self,n):
	    UNIDADES = (
	    '',
	    'UN ',
	    'DOS ',
	    'TRES ',
	    'CUATRO ',
	    'CINCO ',
	    'SEIS ',
	    'SIETE ',
	    'OCHO ',
	    'NUEVE ',
	    'DIEZ ',
	    'ONCE ',
	    'DOCE ',
	    'TRECE ',
	    'CATORCE ',
	    'QUINCE ',
	    'DIECISEIS ',
	    'DIECISIETE ',
	    'DIECIOCHO ',
	    'DIECINUEVE ',
	    'VEINTE '
	)

	    DECENAS = (
	    'VENTI',
	    'TREINTA ',
	    'CUARENTA ',
	    'CINCUENTA ',
	    'SESENTA ',
	    'SETENTA ',
	    'OCHENTA ',
	    'NOVENTA ',
	    'CIEN '
	)

	    CENTENAS = (
	    'CIENTO ',
	    'DOSCIENTOS ',
	    'TRESCIENTOS ',
	    'CUATROCIENTOS ',
	    'QUINIENTOS ',
	    'SEISCIENTOS ',
	    'SETECIENTOS ',
	    'OCHOCIENTOS ',
	    'NOVECIENTOS '
	)
	    MONEDAS = (
		    {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
		    {'country': u'Honduras', 'currency': 'HNL', 'singular': u'Lempira', 'plural': u'Lempiras', 'symbol': u'L'},
		    {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
		    {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
		    {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
		    {'country': u'Perú', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
		    {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
		)
	    """Turn each group of numbers into letters"""
	    output = ''

	    if(n == '100'):
		output = "CIEN "
	    elif(n[0] != '0'):
		output = CENTENAS[int(n[0]) - 1]

	    k = int(n[1:])
	    if(k <= 20):
		output += UNIDADES[k]
	    else:
		if((k > 30) & (n[2] != '0')):
		    output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
		else:
		    output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])

	    return output

	def addComa(self, snum ):
		s = snum;
		i = s.index('.') # Se busca la posición del punto decimal
		while i > 3:
			i = i - 3
			s = s[:i] +  ',' + s[i:]
		return s




class debitcredit_line(osv.Model):
	_name='debitcredit_lines' 
	_columns = {
		'debitcredit_id':fields.many2one('debit.credit','debit credit'),
	        'account_id':fields.many2one('account.account','Account',domain=[('type','not in',['view'])],required=True),
		'name':fields.char('Description',),
		'amount':fields.float('Amount', digits_compute=dp.get_precision('Account')),	
        	'type':fields.selection([('dr','Debit'),('cr','Credit')], 'Dr/Cr'),
}

	_defaults = {
	'type' : 'dr',
		} 
class account_move_line(osv.osv):
	_inherit = 'account.move.line'
	_columns = {
		'debitcredit_id':fields.many2one('debit.credit','mcheck'),
		}
