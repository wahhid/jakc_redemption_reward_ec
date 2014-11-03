from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),
    ('request','Request'),
    ('ready','Ready'),    
    ('open','Open'),    
    ('done', 'Closed'),
]

reportserver = '172.16.0.3'
reportserverport = '8080'


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

class rdm_reward_trans(osv.osv):
    _name = "rdm.reward.trans"
    _description = "Redemption Reward Transaction"
    
    def trans_close(self, cr, uid, ids, context=None):    
        _logger.info("Close Transaction for ID : " + str(ids))    
        self.write(cr,uid,ids,{'state':'done'},context=context)    
        self._deduct_point_(cr, uid, ids, context)
        return True
    
    def _update_print_status(self, cr, uid, ids, context=None):
        _logger.info("Update Print Status for ID : " + str(ids))
        values = {}
        values.update({'bypass':True})
        values.update({'method':'_update_print_status'})
        values.update({'printed':True})
        self.write(cr, uid, ids, values, context=context)
                    
        
    def print_receipt(self, cr, uid, ids, context=None):
        _logger.info("Print Receipt for ID : " + str(ids))        
        id = ids[0]   
        serverUrl = 'http://' + reportserver + ':' + reportserverport +'/jasperserver'
        j_username = 'rdm_operator'
        j_password = 'rdm123'
        ParentFolderUri = '/rdm'
        reportUnit = '/rdm/trans_receipt'
        url = serverUrl + '/flow.html?_flowId=viewReportFlow&standAlone=true&_flowId=viewReportFlow&ParentFolderUri=' + ParentFolderUri + '&reportUnit=' + reportUnit + '&ID=' +  str(id) + '&decorate=no&j_username=' + j_username + '&j_password=' + j_password + '&output=pdf'
        return {
            'type':'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new' 
        }        
        
    
    def re_print(self, cr, uid, ids, context=None):
        _logger.info("Re-Print Receipt for ID : " + str(ids))
        
        return True
    
    def trans_reset(self, cr, uid, ids, context=None):
        _logger.info("Reset for ID : " + str(ids))
        trans_data = {}
        trans_data.update({'state':'open'})      
        super(rdm_reward_trans,self).write(cr, uid, [id], trans_data, context=context)        
        return True
    
    def onchange_reward_id(self, cr, uid, ids, reward_id, context=None):
        if reward_id:
            reward = self.pool.get('rdm.reward').browse(cr, uid, reward_id, context=context)
            return {'value':{'point':reward.point}}
        return {}
        
    def _get_trans(self, cr, uid, trans_id , context=None):
        return self.browse(cr, uid, trans_id, context=context);

    def _deduct_point_(self, cr, uid, ids, context=None):        
        _logger.info('Start Deduct Point')
        trans_id = ids[0]
        trans = self._get_trans(cr, uid, trans_id, context)        
        _logger.info('Total Point :' + str(trans.total_point))
        point_data = {}
        point_data.update({'customer_id': trans.customer_id.id})
        point_data.update({'trans_id':trans.id})
        point_data.update({'trans_type':'reward'})
        point_data.update({'point':-1 * trans.point})                
        self.pool.get('rdm.customer.point').create(cr, uid, point_data, context=context)
        _logger.info('End Generate Coupon')
        
        
        
    _columns = {
        'trans_date': fields.date('Transaction Date', required=True, readonly=True),        
        'customer_id': fields.many2one('rdm.customer','Customer', required=True),        
        'reward_id': fields.many2one('rdm.reward','Reward', required=True),
        'point': fields.integer('Point # Deduct', required=True, readonly=True),      
        'remarks': fields.text('Remarks'),
        'is_booking': fields.boolean('Is Booking ?'),
        'booking_expired': fields.date('Booking Expired'),
        'printed': fields.boolean('Printed', readonly=True),        
        're_print': fields.integer('Re-Print'),
        're_print_remarks': fields.text('Re-print Remarks'),
        'state':  fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'deleted': fields.boolean('Deleted'),
    }
    
    _defaults = {
        'trans_date': fields.date.context_today,
        'state': lambda *a: 'draft',
        'is_booking': lambda *a: False,        
    }
    
rdm_reward_trans()