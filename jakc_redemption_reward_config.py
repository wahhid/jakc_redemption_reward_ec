from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)

class rdm_reward_config(osv.osv):
    _name = 'rdm.reward.config'
    _description = 'Redemption Reward Config'
    
    def get_config(self, cr, uid, context=None):
        ids = self.search(cr, uid, [('state','=', True),], context=context)
        if ids:
            return self.pool.get('rdm.reward.config').browse(cr, uid, uid, context=context)
        else:
            return None
            
    _columns = {
        'reward_limit' : fields.boolean('Reward Limit Per Day'),
        'reward_limit_count': fields.integer('Reward Limit Count'),
        'state': fields.boolean('Status'),
    }
    _defaults = {
        'reward_limit': lambda *a: False,
        'reward_limit_count': lambda *a: 0,
        'state': lambda *a: True,
        
    }
rdm_reward_config()

class rdm_reward_config_settings(osv.osv_memory):
    _name = 'rdm.reward.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'reward_limit' : fields.boolean('Reward Limit Per Day'),
        'reward_limit_count': fields.integer('Reward Limit Count'),
    }

    def get_default_reward_limit(self, cr, uid, fields, context=None):
        ids = self.pool.get('rdm.reward.config').search(cr, uid, [('state','=', True),], context=context)
        if ids:
            reward_limit = self.pool.get('rdm.reward.config').browse(cr, uid, uid, context=context).enable_referal
        else: 
            reward_data = {}
            result_id = self.pool.get('rdm.reward.config').create(cr, uid, reward_data, context=context)
            reward_limit = False
        return {'reward_limit': reward_limit}


    def set_default_reward_limit(self, cr, uid, ids, context=None):
        config_ids = self.pool.get('rdm.reward.config').search(cr, uid, [('state','=', True),], context=context)
        config = self.browse(cr, uid, ids[0], context)
        reward_limit = config.reward_limit
        self.pool.get('rdm.reward.config').write(cr, uid, config_ids, {'reward_limit': reward_limit})


    def get_default_reward_limit_count(self, cr, uid, fields, context=None):
        ids = self.pool.get('rdm.reward.config').search(cr, uid, [('state','=', True),], context=context)
        if ids:
            reward_limit_count = self.pool.get('rdm.reward.config').browse(cr, uid, uid, context=context).enable_referal
        else: 
            reward_data = {}
            result_id = self.pool.get('rdm.reward.config').create(cr, uid, reward_data, context=context)
            reward_limit_count = 0
        return {'reward_limit_count': reward_limit_count}


    def set_default_reward_limit_count(self, cr, uid, ids, context=None):
        config_ids = self.pool.get('rdm.reward.config').search(cr, uid, [('state','=', True),], context=context)
        config = self.browse(cr, uid, ids[0], context)
        reward_limit_count = config.reward_limit_count
        self.pool.get('rdm.reward.config').write(cr, uid, config_ids, {'reward_limit_count': reward_limit_count})
