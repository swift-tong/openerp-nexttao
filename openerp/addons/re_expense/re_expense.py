import datetime

from openerp.osv import osv, fields

def _get_last_month_end():
    """
    获取上月最后一天
    """
    today = datetime.date.today()
    last_day_of_last_month = datetime.date(today.year, today.month, 1) - datetime.timedelta(1)
    return last_day_of_last_month


class re_expense_expense(osv.osv):

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.unit_amount * line.unit_quantity
            res[expense.id] = total
        return res

    _name = 're.expense.expense'
    _description = "Expense"
    _order = "id desc"

    _columns = {
        'user': fields.many2one('res.users', '员工', required=True),
        'date': fields.date('日期', select=True, readonly=True,states={'draft': [('readonly', False)]}),
        'department': fields.text('部门', readonly=True,states={'draft': [('readonly', False)]}),
        'note': fields.text('说明', readonly=True,states={'submitted': [('readonly', False)]}),
        'total_amount': fields.function(_amount, readonly=True,string='总金额'),

        'user_create': fields.many2one('res.users', '创建人', required=True),
        'date_create': fields.datetime('创建时间',  readonly=True),

        'user_check': fields.many2one('res.users', '审核人', required=True),
        'date_check': fields.datetime('审核时间',  readonly=True),

        'user_cancel': fields.many2one('res.users', '取消人', required=True),
        'date_cancel': fields.datetime('取消时间', readonly=True),

        'user_commit': fields.many2one('res.users', '提交人', required=True),
        'date_commit': fields.datetime('提交时间', readonly=True),

        'state': fields.selection([
            ('draft', '新建'),
            ('submitted', '已提交'),
            ('done', '已完成'),
            ('cancelled', '已取消'),
            ],
            'Status', readonly=True, track_visibility='onchange',
        ),

        'product_id': fields.many2one('product.product', '产品',readonly=True, states={'draft': [('readonly', False)]}),
        'product_amount': fields.integer('产品数量',readonly=True, states={'draft': [('readonly', False)]}),
        'expense_data': fields.date('费用日期', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'expense_note': fields.text('费用备注', required=False,readonly=True, states={'draft': [('readonly', False)]}),
        'order_no.': fields.text('单号', required=False,readonly=True, states={'draft': [('readonly', False)]}),
        'auxiliary.': fields.text('辅助核算项', required=False,readonly=True, states={'draft': [('readonly', False)]}),
        'amount': fields.integer(string='金额'),

    }
    _defaults = {
        'date': fields.date.context_today,
        'date_create': fields.datetime.now(),
        'date_check': fields.datetime.now(),
        'date_cancel': fields.datetime.now(),
        'date_commit': fields.datetime.now(),
        'expense_data':_get_last_month_end,
        'state': 'draft',
    }
