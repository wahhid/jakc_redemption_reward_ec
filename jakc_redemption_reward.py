from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),
    ('open','Open'),    
    ('done', 'Closed'),
]

AVAILABLE_TYPE = [
    ('goods','Goods'),
    ('coupon','Coupon'),
    ('voucher','Voucher'),
]

AVAILABLE_VOUCHER_STATES = [
    ('open','Open'),
    ('done','Closed'),
    ('disable','Disable'),
]

reportserver = '172.16.0.3'
reportserverport = '8080'

class rdm_reward(osv.osv):
    _name = "rdm.reward"
    _description = "Redemption Reward"
    
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]        
        return self.browse(cr, uid, trans_id, context=context)
        
    def get_stocks(self, cr, uid, ids, field_name, args, context=None):
        _logger.info('Start Get Stocks')       
        id = ids[0]     
        trans = self.get_trans(cr, uid, ids, context)
        total_stock = 0
        res = {}
        if trans.type == 'goods':
            total_stock = self.pool.get('rdm.reward.goods').get_stock(cr, uid, id, context=context)
        if trans.type == 'coupon':
            total_stock = self.pool.get('rdm.reward.coupon').get_stock(cr, uid, id, context=context)
        if trans.type == 'voucer':
            total_stock = self.pool.get('rdm.reward.voucher').get_stock(cr, uid, id, context=context)            
        res[id] = total_stock
        _logger.info('End Get Stocks')    
        return res    
    
    def get_usages(self, cr, uid, ids, field_name, args, context=None):
        _logger.info('Start Get Usage')        
        id = ids[0]
        total_usage = 0
        res = {}
        sql_req= "SELECT sum(point) as total FROM rdm_reward_trans WHERE reward_id=" + str(id)            
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_usage = sql_res['total']
        res[id] = total_usage            
        _logger.info('End Get Usages')                
        return res                 
        
            
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'type': fields.selection(AVAILABLE_TYPE,'Type', size=16, required=True),
        'point': fields.integer('Point #'),
        'stock': fields.function(get_stocks, type="integer", string="Stock"),
        'usage': fields.function(get_usages, type="integer", string="Usage"),                        
        'image1': fields.binary('Image'),
        'goods_ids': fields.one2many('rdm.reward.goods', 'reward_id', 'Goods'),
        'coupon_ids': fields.one2many('rdm.reward.coupon', 'reward_id', 'Coupon'),
        'voucher_ids': fields.one2many('rdm.reward.voucher', 'reward_id', 'Voucher'),             
        'state': fields.selection(AVAILABLE_STATES,'Status',size=16,readonly=True),        
    }
    
    _defaults ={
        'point': lambda *a: 1,
        'type': lambda *a: 'goods',
        'state': lambda *a: 'draft',
    }

        
rdm_reward()

class rdm_reward_goods(osv.osv):
    _name = "rdm.reward.goods"
    _description = "Redemption Reward Goods"
    
    def get_stock(self, cr, uid, reward_id, context=None):
        _logger.info('Start Get Goods Stocks')        
        total_stock = 0        
        sql_req= "SELECT sum(stock) as total FROM rdm_reward_goods WHERE reward_id=" + str(reward_id)            
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_stock = sql_res['total']            
        _logger.info('End Get Goods Stocks')        
        return total_stock    
                                
    _columns = {
        'reward_id': fields.many2one('rdm.reward','Reward', readonly=True),
        'trans_date': fields.date('Transaction Date'),     
        'stock': fields.integer('Stock'),       
    }    

    _defaults = {
        'trans_date': fields.date.context_today,
    }
    
rdm_reward_goods()

class rdm_reward_coupon(osv.osv):
    _name = "rdm.reward.coupon"
    _description = "Redemption Reward Coupon"
    
    def get_stock(self, cr, uid, reward_id, context=None):
        _logger.info('Start Get Coupon Stocks')        
        total_stock = 0        
        sql_req= "SELECT sum(stock) as total FROM rdm_reward_coupon WHERE reward_id=" + str(reward_id)            
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_stock = sql_res['total']            
        _logger.info('End Get Coupon Stocks')        
        return total_stock    
        
    _columns = {
        'reward_id': fields.many2one('rdm.reward','Reward', readonly=True),
        'trans_date': fields.date('Transaction Date'),     
        'stock': fields.integer('Stock'),       
    }
    
    _defaults = {
        'trans_date': fields.date.context_today,
    }
    
rdm_reward_coupon()

class rdm_reward_voucher(osv.osv):
    _name = "rdm.reward.voucher"
    _description = "Redemption Reward Voucher"
    
    def get_stock(self, cr, uid, reward_id, context=None):        
        _logger.info('Start Get Voucher Stocks')        
        total_stock = 0        
        sql_req= "SELECT count(*) as total FROM rdm_reward_voucher WHERE reward_id=" + str(reward_id) + " AND state='open'"            
        cr.execute(sql_req)
        sql_res = cr.dictfetchone()
        if sql_res:
            total_stock = sql_res['total']            
        _logger.info('End Get Voucher Stocks')        
        return total_stock    
    
    _columns = {
        'reward_id': fields.many2one('rdm.reward','Reward', readonly=True),
        'trans_date': fields.date('Transaction Date'),
        'voucher_no': fields.char('Voucher #', size=15),
        'state': fields.selection(AVAILABLE_VOUCHER_STATES,'Status',size=16, readonly=True),
    }
    
    _defaults = {
        'trans_date': fields.date.context_today,
        'state': lambda *a : 'open',
    }
    
rdm_reward_voucher()

class rdm_reward_trans(osv.osv):
    _name = "rdm.reward.trans"
    _description = "Redemption Reward Transaction"
    
    def trans_close(self, cr, uid, ids, context=None):    
        _logger.info("Close Transaction for ID : " + str(ids))
        #Get Transaction
        trans_id = ids[0]
        trans = self._get_trans(cr, uid, trans_id, context)        
        #Close Transaction         
        self.write(cr,uid,ids,{'state':'done'},context=context)        
        #Deduct Point
        customer_id = trans.customer_id.id                
        self.pool.get('rdm.customer.point').deduct_point(cr, uid, trans_id, customer_id, trans.point, context=context)
        return True
    
    def _update_print_status(self, cr, uid, ids, context=None):
        _logger.info("Start Update Print Status for ID : " + str(ids))
        values = {}
        values.update({'bypass':True})
        values.update({'method':'_update_print_status'})
        values.update({'printed':True})
        self.write(cr, uid, ids, values, context=context)
        _logger.info("End Update Print Status for ID : " + str(ids))            
        
    def trans_print_receipt(self, cr, uid, ids, context=None):
        _logger.info("Print Receipt for ID : " + str(ids))        
        trans_id = ids[0]   
        
        serverUrl = 'http://' + reportserver + ':' + reportserverport +'/jasperserver'
        j_username = 'rdm_operator'
        j_password = 'rdm123'
        ParentFolderUri = '/rdm'
        reportUnit = '/rdm/trans_receipt'
        url = serverUrl + '/flow.html?_flowId=viewReportFlow&standAlone=true&_flowId=viewReportFlow&ParentFolderUri=' + ParentFolderUri + '&reportUnit=' + reportUnit + '&ID=' +  str(trans_id) + '&decorate=no&j_username=' + j_username + '&j_password=' + j_password + '&output=pdf'
        return {
            'type':'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new' 
        }        
            
    def trans_re_print(self, cr, uid, ids, context=None):
        _logger.info("Re-Print Receipt for ID : " + str(ids))
        trans_id = ids[0]
        trans = self._get_trans(cr, uid, trans_id, context)
        
        return True
    
    def trans_reset(self, cr, uid, ids, context=None):
        _logger.info("Start Reset for ID : " + str(ids))
        values = {}
        values.update({'bypass':True})
        values.update({'method':'trans_reset'})
        values.update({'state':'open'})
        self.write(cr, uid, ids, values, context=context)
        _logger.info("End Reset for ID : " + str(ids))            

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
        customer = self.pool.get('rdm.customer').get_trans(cr, uid, customer_id, context=context)            
        _logger.info('Customer Point : ' + str(customer['point']))        
        reward_id = values.get('reward_id')
        reward = self._get_reward(cr, uid, reward_id, context)        
        if customer['point'] >= reward.point:            
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
                if values.get('method') == 'trans_reset':
                    trans_data.update({'state': values.get('state')})
                if values.get('method') == 'trans_print_receipt':
                    trans_data.update({'printed': values.get('printed')})
                
                result = super(rdm_reward_trans,self).write(cr, uid, ids, trans_data, context=context)                       
            else: 
                raise osv.except_osv(('Warning'), ('Edit not allowed, Transaction already closed!'))              
        else:
            result = super(rdm_reward_trans,self).write(cr, uid, ids, values, context=context)
        return result
    
rdm_reward_trans()