from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),
    ('open','Open'),    
    ('done', 'Closed'),
]

reportserver = '172.16.0.3'
reportserverport = '8080'

class rdm_reward(osv.osv):
    _name = "rdm.reward"
    _description = "Redemption Reward"
    
    def get_stocks(self, cr, uid, ids, field_name, args, context=None):
        id = ids[0]
        res = {}
        sql_req= "SELECT sum(c.stock) as total FROM rdm_reward_detail c WHERE (c.reward_id=" + str(id) + ")"        
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_coupons = sql_res['total']
        else:
            total_coupons = 0
        #return {'value':{'':total_coupons}}
        res[id] = total_coupons    
        return res    
    
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'point': fields.integer('Point #'),
        'stock': fields.function(get_stocks,type="integer",string="Stocks"),
        'reward_detail_ids': fields.one2many('rdm.reward.detail','reward_id','Reward Details'),   
        'image1': fields.binary('Image'),             
        'state': fields.selection(AVAILABLE_STATES,'Status',size=16,readonly=True),        
    }
    
    _defaults ={
        'point': lambda *a: 1,
        'state': lambda *a: 'draft',
    }

rdm_reward()

class rdm_reward_detail(osv.osv):
    _name = "rdm.reward.detail"
    _description = "Redemption Reward Detail"    
    _columns = {
        'reward_id': fields.many2one('rdm.reward','Reward',readonly=True),
        'trans_date': fields.date('Transaction Date'),     
        'stock': fields.integer('Stock'),       
    }
    
rdm_reward_detail()

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
        res = {}
        if reward_id:
            reward = self.pool.get('rdm.reward').browse(cr, uid, reward_id, context=context)
            res['point'] = reward.point
            #return {'value':{'point':reward.point}}
        return {'value':res}
        
    def _get_trans(self, cr, uid, trans_id , context=None):
        return self.browse(cr, uid, trans_id, context=context);
    
    def _get_reward(self, cr, uid, reward_id, context=None):
        reward = self.pool.get('rdm.reward').browse(cr, uid, reward_id, context=context)
        return reward
    
    def _deduct_point_(self, cr, uid, ids, context=None):        
        _logger.info('Start Deduct Point')
        trans_id = ids[0]
        trans = self._get_trans(cr, uid, trans_id, context)                
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
        'point': fields.integer('Point # Deduct', readonly=True),      
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
    
    def create(self, cr, uid, values, context=None):     
        customer_id = values.get('customer_id')
        customer_point = self.pool.get('rdm.customer').get_points(cr, uid, [customer_id], field_name=None, args=None, context=None)        
        _logger.info('Customer Point : ' + str(customer_point.get(customer_id)))        
        reward_id = values.get('reward_id')
        reward = self._get_reward(cr, uid, reward_id, context)        
        if customer_point.get(customer_id) >= reward.point:            
            values.update({'point':reward.point})
            values.update({'state':'open'})
            trans_id = super(rdm_reward_trans,self).create(cr, uid, values, context=context)            
            return trans_id
        else:
            raise osv.except_osv(('Warning'), ('Point not enough'))           
    
    def write(self, cr, uid, ids, values, context=None ):
        trans_id = ids[0]                
        trans = self._get_trans(cr, uid, trans_id, context)        
        if trans['state'] == 'done':                 
            if values.get('bypass') == True:
                trans_data = {}                
            else: 
                raise osv.except_osv(('Warning'), ('Edit not allowed, Transaction already closed!'))              
        else:
            reward_id = values.get('reward_id')
            if reward_id:
                reward = self._get_reward(cr, uid, reward_id, context)        
                values.update({'point':reward.point})            
        result = super(rdm_reward_trans,self).write(cr, uid, ids, values, context=context)
        return result
    
rdm_reward_trans()