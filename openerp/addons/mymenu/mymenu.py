from openerp.osv import osv, fields
class silkworm_sale_order(osv.Model):
    _inherit = 'sale.order'
    _columns = {
       'x_daterequired': fields.date('Date Required', required=True),
       'x_rush': fields.boolean('Rush Order'),
        }
