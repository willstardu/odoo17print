{
    'name': 'Printer Service Integration',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Integrate with external PrinterService for remote printing',
    'description': """
        Printer Service Integration
        ===========================
        此模块允许将 Odoo 报表直接发送到运行 PrinterService 的本地服务器。
        
        功能特点:
        - 无需客户端驱动：通过 HTTP API 发送文件到打印节点。
        - 支持多打印机：自动同步打印节点上的所有打印机。
        - 远程打印：支持从任何设备（手机、Web）触发打印。
    """,
    'author': 'Trae AI',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/print_server_views.xml',
        'wizard/print_to_server_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
