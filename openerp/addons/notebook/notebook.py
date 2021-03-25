from openerp.osv import osv, fields


# -*- coding:utf-8 -*-
from openerp.osv import fields, osv
class notebook(osv.osv):
    _name = "notebook.notebook"
    _description = "demo"
    _columns = {
        "title":fields.char(u"title",size=64,select=True),
        "content":fields.text(u"content",size=1000),
        "create_date":fields.date(u"create_date",select=True),
        "type":fields.many2one('notebook_type.notebook_type',u"type"),
    }
notebook()