# -*- coding: utf-8 -*-
import datetime
import time

import openerp.addons.decimal_precision as dp
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
        'user': fields.many2one('res.users', u'员工', required=True,readonly=True),
        'date': fields.date(u'日期', select=True, readonly=True,states={'draft': [('readonly', False)]}),
        'department': fields.text(u'部门', readonly=True,states={'draft': [('readonly', False)]}),
        'instructions': fields.text(u'说明', readonly=True,states={'submitted': [('readonly', False)]}),
        'total_amount': fields.function(_amount, readonly=True,string=u'总金额'),
        'reception': fields.text(u'已收单', readonly=True, states={'submitted': [('readonly', False)]}),
        'note': fields.text(u'备注', readonly=True, states={'submitted': [('readonly', False)]}),

        'user_create': fields.many2one('res.users', u'创建人', required=True),
        'date_create': fields.datetime(u'创建时间',  readonly=True),

        'user_check': fields.many2one('res.users', u'审核人', required=True),
        'date_check': fields.datetime(u'审核时间',  readonly=True),

        'user_cancel': fields.many2one('res.users', u'取消人', required=True),
        'date_cancel': fields.datetime(u'取消时间', readonly=True),

        'user_commit': fields.many2one('res.users', u'提交人', required=True),
        'date_commit': fields.datetime(u'提交时间', readonly=True),

        'state': fields.selection([
            ('draft', u'新建'),
            ('submitted', u'已提交'),
            ('done', u'已完成'),
            ('cancelled', u'已取消'),
            ],
            '状态', readonly=True, track_visibility='onchange'
        ),
        'line_ids': fields.one2many('re.expense.line', 'expense_id', 'Expense Lines'),

    }
    _defaults = {
        'date': fields.date.context_today,
        'date_create': fields.datetime.now(),
        'date_check': fields.datetime.now(),
        'date_cancel': fields.datetime.now(),
        'date_commit': fields.datetime.now(),
        'state': 'draft',
    }

    def expense_submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'submitted', 'date_create': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)

    def expense_accept(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'accepted', 'date_valid': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_valid': uid}, context=context)

    def expense_canceled(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)

    def action_receipt_create(self, cr, uid, ids,):
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'expense_ok': fields.boolean('可以报销'),
    }

product_product()

class re_expense_line(osv.osv):
    _name = "re.expense.line"
    _description = "Expense Line"

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.product_amount*l.amount),0) AS amount FROM hr_expense_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res

    _columns = {
        'expense_id': fields.many2one('re.expense.expense', 'Expense'),
        'product_id': fields.many2one('product.product', u'产品',readonly=True, states={'draft': [('readonly', False)]}),
        'product_amount': fields.integer(u'数量',readonly=True, states={'draft': [('readonly', False)]}),
        'expense_data': fields.date(u'费用日期', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'expense_note': fields.text(u'费用备注', required=False,readonly=True, states={'draft': [('readonly', False)]}),
        'order_no.': fields.text(u'单号', required=False,readonly=True, states={'draft': [('readonly', False)]}),
        'auxiliary': fields.text(u'辅助核算项', required=False,readonly=True, states={'draft': [('readonly', False)]}),
        'amount': fields.integer(string=u'金额',digits_compute=dp.get_precision('Product Price')),
        'total_amount': fields.function(_amount, string=u'合计',digits_compute=dp.get_precision('Account')),
        }

    _defaults = {
        'expense_data':_get_last_month_end,
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            res['name'] = product.name
            amount_unit = product.price_get('standard_price')[product.id]
            res['unit_amount'] = amount_unit
            res['uom_id'] = product.uom_id.id
        return {'value': res}