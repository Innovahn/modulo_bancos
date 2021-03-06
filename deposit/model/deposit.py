from openerp.osv import fields, osv
from openerp.tools.translate import _



class deposit(osv.Model):
	_name= 'deposit'	

	def create(self, cr, uid, values, context=None):
		seq_obj = self.pool.get('ir.sequence')
		name = "/"
		journal_obj = self.pool.get('account.journal')
		diario = journal_obj.browse(cr,uid,values['journal'],context=context)

		
		if diario.sequence_id_deposit:
			if not diario.sequence_id_deposit.active:
				raise osv.except_osv(_('Configuration Error !'),_('Please activate the sequence of selected journal !'))
			c = dict(context)
			name = seq_obj.next_by_id(cr, uid, diario.sequence_id_deposit.id, context=c)
			
		else:
			raise osv.except_osv(_('Configuration Error !'),_('Please select the sequence of selected journal !'))
		
		values['number']=name
		b =super(deposit, self).create(cr, uid, values, context=context)	
		return b

	def load_voucher(self,cr,uid,ids,journal_id,context=None):
		journal=self.pool.get('account.journal')
		voucher=self.pool.get('account.voucher')

		voucher_ids=voucher.search(cr,uid,[('journal_id', '=', journal_id)])
		res={    'value': {'pays': []   },}

		for vouch in voucher.browse(cr, uid, voucher_ids, context=context):
			print "----------------------voucher"
			print vouch.id
        	#    if line.type == 'cr':
               		res['value']['pays'].append((vouch.id))
        	#    else:
                #default['value']['line_dr_ids'].append((2, line.id))

        	#if not partner_id or not journal_id:
         	#   return default
		
		print "###"*30
		print journal_id
		print voucher_ids
		return res

	_columns= {
		'journal':fields.many2one('account.journal','Journal',help="Select the checkbook for this deposit"),
		'date':fields.date('Date',select=True ,help="Select date of the deposit"),
		'description':fields.char('Description',100),
		'number':fields.char('Number',readonly=True, help="Number of sequence of deposit"),
		'state':fields.selection(
		    [('draft','Draft'),
		     ('cancel','Cancelled'),
		     ('posted','Posted')
		    ], 'Status', 
		    help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
		                \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
		                \n* The \'Cancelled\' status is used when user cancel voucher.'),
		'amount':fields.integer('Amount'),
		'pays':fields.one2many('account.voucher','deposit_id'),
	}
