from openerp.osv import osv, fields


class notebook_type(osv.osv):
    _name = "notebook_type.notebook_type"
    _description = "depend notebook"
    _columns = {
        "type":fields.char(u"type",szie=64),
        "code":fields.char(u"code",szie=64),
    }