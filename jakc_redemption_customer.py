from openerp.osv import fields, osv

class rdm_customer(osv.osv):
    _name = "rdm.customer"
    _inherit = "rdm.customer"
    _columns = {
        'reward_trans_ids': fields.one2many('rdm.reward.trans','customer_id','Rewards',readonly=True)
    }
rdm_customer()