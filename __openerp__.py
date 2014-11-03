{
    'name' : 'Redemption and Point Management - Reward Module',
    'version' : '1.0',
    'author' : 'JakC',
    'category' : 'Generic Modules/Redemption And Point Management',
    'depends' : ['base_setup','base','jakc_redemption_customer','jakc_redemption_customer_point'],
    'init_xml' : [],
    'data' : [			
        'security/ir.model.access.csv',
        'jakc_redemption_reward_view.xml',
        'jakc_redemption_reward_menu.xml',    
        'jakc_redemption_customer_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}