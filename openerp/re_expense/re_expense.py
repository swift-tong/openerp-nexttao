from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

def _employee_get(obj, cr, uid, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
    if ids:
        return ids[0]
    return False

class re_expense_expense(osv.osv):
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.unit_amount * line.unit_quantity
            res[expense.id] = total
        return res

    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        return user.company_id.currency_id.id

    _name = 're.expense.expense'
    _description = "Expense"
    _order = "id desc"

    _columns = {
        'name': fields.char('Description', size=128, required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'id': fields.integer('Sheet ID', readonly=True),
        'date': fields.date('Date', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Force Journal', help = "The journal used when the expense is done."),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date_confirm': fields.date('Confirmation Date', select=True, help="Date of the confirmation of the sheet expense. It's filled when the button Confirm is pressed."),
        'date_valid': fields.date('Validation Date', select=True, help="Date of the acceptation of the sheet expense. It's filled when the button Accept is pressed."),
        'user_valid': fields.many2one('res.users', 'Validation By', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'account_move_id': fields.many2one('account.move', 'Ledger Posting'),
        'line_ids': fields.one2many('hr.expense.line', 'expense_id', 'Expense Lines', readonly=True, states={'draft':[('readonly',False)]} ),
        'note': fields.text('Note'),
        'amount': fields.function(_amount, string='Total Amount', digits_compute=dp.get_precision('Account')),
        'voucher_id': fields.many2one('account.voucher', "Employee's Receipt"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'department_id':fields.many2one('hr.department','Department', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('paid', 'Paid'),
            ],
            'Status', readonly=True, track_visibility='onchange',
            help='When the expense request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the expense request, the status is \'Waiting Payment\'.'),

    }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context=c),
        'date': fields.date.context_today,
        'state': 'draft',
        'employee_id': _employee_get,
        'user_id': lambda cr, uid, id, c={}: id,
        'currency_id': _get_currency,
    }
