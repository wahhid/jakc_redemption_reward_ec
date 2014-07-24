from openerp.osv import fields, osv

class rdm_reward(osv.osv):
    _name = "rdm.reward"
    _description = "Redemption Reward"
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'point': fields.integer('Point #'),
        'stock': fields.integer('Stock #'),
        'image1': fields.binary('Image'),
        'status': fields.boolean('Status'),
    }

rdm_reward()

class rdm_point_reward(osv.osv):
    _name = "rdm.point.reward"
    _description = "Redemption Point Reward"
    _columns = {
        'customer_id': fields.many2one('rdm.customer','Customer'),
        'reward_id': fields.many2one('rdm.reward','Reward'),
        'point': fields.integer('Point # Deduct', readonly=True),      
        'remarks': fields.text('Remarks')
    }
    
rdm_point_reward()