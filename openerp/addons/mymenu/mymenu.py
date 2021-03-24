from openerp.osv import osv, fields


class mymenu_mymenu(osv.osv):
    _name = 'mymenu.mymenu'
    _columns = {
        'x_daterequired': fields.date('Date Required', required=True),
        'x_rush': fields.boolean('Rush Order'),
    }
