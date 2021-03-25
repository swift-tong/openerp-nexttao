from openerp.osv import fields, osv

class notebook(osv.osv):
    _name = "notebook.notebook"
    _description = "demo"
    _columns = {
        "title":fields.char(u"title",size=64,select=True),
        "content":fields.text(u"content",size=1000),
        "create_date":fields.date(u"create_date",select=True),
        "type":fields.many2one('notebook_type.notebook_type'u"type"),
    }


    # def search(self, cr, uid, domain, offset=0,limit=None, order=None, context=None, count=False):
    #     obj = self.pool.get('notebook.notebook')
    #     ids = obj.search(cr, uid, domain)
    #     return ids