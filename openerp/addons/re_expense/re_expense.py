# -*- coding: utf-8 -*-
import datetime
import time

import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields


def _get_last_month_end(obj, cr, uid, context=None):
    """
    获取上月最后一天
    """
    today = datetime.date.today()
    last_day_of_last_month = datetime.date(today.year, today.month, 1) - datetime.timedelta(1)
    ret = last_day_of_last_month.strftime("%Y-%m-%d")
    return ret


class re_expense_expense(osv.osv):

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.product_amount * line.amount
            res[expense.id] = total
        return res

    def _check_role(self,cr,uid,ids, field_name, arg, context=None):
        res = {}
        for expense in self.browse(cr, uid, ids, context=context):
            reception = expense.reception
            if self.pool.get('res.users').has_group(cr, uid, "re_expense.expense_users"):
                self._readonly = True
                res[expense.id] = reception
            elif self.pool.get('res.users').has_group(cr, uid, "re_expense.expense_manager"):
                res[expense.id] = reception
                self._readonly = False
        return res

    _name = 're.expense.expense'
    _description = "Expense"
    _order = "id desc"
    _readonly = True

    _columns = {
        'user': fields.many2one('res.users', u'员工', required=True, readonly=True),
        'date': fields.date(u'日期', select=True, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'department': fields.many2one('hr.department', u'部门', readonly=True, states={'draft': [('readonly', False)]}),
        'instructions': fields.char(u'说明', readonly=True, states={'draft': [('readonly', False)]}),
        'total_amount': fields.function(_amount, readonly=True, string=u'总金额', digits=(12,3)),
        # 'reception': fields.boolean(u'已收单', readonly=_readonly, states={'submitted': [('readonly', False)]}),
        'reception': fields.function(_check_role,string=u'已收单', readonly=_readonly),
        'note': fields.text(u'备注', readonly=True,
                            states={'draft': [('readonly', False)], 'submitted': [('readonly', False)]}),

        'user_create': fields.many2one('res.users', u'创建人', readonly=True),
        'date_create': fields.datetime(u'创建时间', readonly=True),

        'user_submit': fields.many2one('res.users', u'提交人', readonly=True),
        'date_submit': fields.datetime(u'提交时间', readonly=True),

        'user_accept': fields.many2one('res.users', u'审核人', readonly=True),
        'date_accept': fields.datetime(u'审核时间', readonly=True),

        'user_reject': fields.many2one('res.users', u'驳回人', readonly=True),
        'date_reject': fields.datetime(u'驳回时间', readonly=True),

        'state': fields.selection([
            ('draft', u'草稿'),
            ('submitted', u'已提交'),
            ('done', u'已完成'),
            ('cancelled', u'已取消'),
        ],
            '状态', readonly=True
        ),
        'line_ids': fields.one2many('re.expense.line', 'expense_id', 'Expense Lines', readonly=True, states={'draft': [('readonly', False)]}),

    }
    _defaults = {
        'date': fields.date.context_today,
        'user_create': lambda cr, uid, id, c={}: id,
        'date_create': time.strftime('%Y-%m-%d %H:%M:%S'),
        # 'date_check': fields.datetime.now(),
        # 'date_cancel': fields.datetime.now(),
        # 'date_commit': fields.datetime.now(),
        'reception': False,
        'state': 'draft',
        'user': lambda cr, uid, id, c={}: id,
    }

    def expense_submit(self, cr, uid, ids, context=None):
        data = {
            'state': 'submitted',
            'user_submit': uid,
            'date_submit': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        print data
        return self.write(cr, uid, ids, data, context=context)

    def expense_accept(self, cr, uid, ids, context=None):
        data = {
            'state': 'done',
            'user_accept': uid,
            'date_accept': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.write(cr, uid, ids,data,context=context)

    def expense_rejected(self, cr, uid, ids, context=None):
        data = {
            'state': 'draft',
            'user_reject': uid,
            'date_reject': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.write(cr, uid, ids, data, context=context)


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
        cr.execute(
            "SELECT l.id,COALESCE(SUM(l.product_amount*l.amount),0) AS amount FROM re_expense_line l WHERE id IN %s GROUP BY l.id ",
            (tuple(ids),))
        res = dict(cr.fetchall())
        return res

    _columns = {
        'expense_id': fields.many2one('re.expense.expense', 'Expense'),
        'product_id': fields.many2one('product.product', u'产品', required=True),
        'product_amount': fields.integer(u'数量', required=True),
        # 'expense_data': fields.date(u'费用日期', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'expense_data': fields.date(u'费用日期', required=True),
        'expense_note': fields.char(u'费用备注', required=False),
        'order_no.': fields.char(u'单号', required=False),
        'auxiliary': fields.char(u'辅助核算项', required=False),
        'amount': fields.float(string=u'金额', digits=(12,3), required=True),
        'total_amount': fields.function(_amount, string=u'合计', digits=(12,3)),
    }

    _defaults = {
        'expense_data': _get_last_month_end,
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
