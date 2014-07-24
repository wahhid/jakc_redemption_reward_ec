from openerp.osv import fields, osv

class rdm_customer(osv.osv):
    _name = "rdm.customer"
    _inherit = "rdm.customer"
    _columns = {
        'point_reward_ids': fields.one2many('rdm.point.reward','customer_id','Rewards',readonly=True)
    }
rdm_customer()