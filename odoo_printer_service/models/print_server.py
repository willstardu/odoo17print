from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class PrinterServer(models.Model):
    """
    打印服务器模型
    用于配置连接到运行 PrinterService 的 Windows 电脑。
    """
    _name = 'printer.server'
    _description = 'Printer Service Server'

    # 服务器名称，例如 "仓库电脑"
    name = fields.Char(string='Name', required=True, default='Local Printer Server')
    
    # 服务器地址，指向运行 PrinterService 的 IP 和端口
    url = fields.Char(string='Server URL', required=True, default='http://localhost:5000', 
                      help="PrinterService 运行的地址，例如 http://192.168.1.100:5000")
    
    # 是否启用
    active = fields.Boolean(default=True)
    
    # 状态字段
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('unknown', 'Unknown')
    ], string='Status', default='unknown', readonly=True)
    
    last_heartbeat = fields.Datetime(string='Last Heartbeat', readonly=True)
    
    # 关联的打印机列表
    printer_ids = fields.One2many('printer.server.printer', 'server_id', string='Printers')

    def action_check_status(self):
        """
        检查服务器状态（心跳检测）
        """
        for server in self:
            try:
                url = f"{server.url.rstrip('/')}/heartbeat"
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200 and response.json().get('status') == 'ok':
                        server.status = 'online'
                        server.last_heartbeat = fields.Datetime.now()
                    else:
                        server.status = 'offline'
                except requests.exceptions.RequestException:
                    server.status = 'offline'
            except Exception:
                server.status = 'offline'

    @api.model
    def _cron_check_server_status(self):
        """
        定时任务：检查所有启用服务器的状态
        """
        servers = self.search([('active', '=', True)])
        if servers:
            servers.action_check_status()

    def action_fetch_printers(self):
        """
        从远程服务器获取打印机列表
        """
        self.ensure_one()
        try:
            # 构建 API URL
            api_url = f"{self.url.rstrip('/')}/api/printers"
            _logger.info(f"正在从 {api_url} 获取打印机列表")
            
            # 发送请求
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                # 获取当前已保存的打印机名称
                current_printers = self.printer_ids.mapped('name')
                fetched_printers = data.get('printers', [])
                
                # 添加新发现的打印机
                for p_name in fetched_printers:
                    if p_name not in current_printers:
                        self.env['printer.server.printer'].create({
                            'name': p_name,
                            'server_id': self.id,
                        })
                
                # 返回成功通知
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Found %d printers.') % len(fetched_printers),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_('Server returned error: %s') % data.get('message'))
        except Exception as e:
            _logger.error(f"Failed to fetch printers: {e}")
            raise UserError(_('Failed to connect to printer server. Check URL and network.\nError: %s') % str(e))

class PrinterServerPrinter(models.Model):
    """
    打印机模型
    存储从服务器获取的具体打印机信息。
    """
    _name = 'printer.server.printer'
    _description = 'Printer Server Printer'

    # 打印机名称 (Windows 系统中的名称)
    name = fields.Char(required=True)
    
    # 关联的服务器
    server_id = fields.Many2one('printer.server', required=True, ondelete='cascade')
    
    # 服务器 URL (关联字段，方便读取)
    server_url = fields.Char(related='server_id.url', readonly=True)

    def action_print_file(self, file_content, filename, copies=1):
        """
        上传并打印文件
        :param file_content: 文件二进制内容
        :param filename: 文件名
        :param copies: 打印份数
        """
        self.ensure_one()
        server_url = self.server_id.url.rstrip('/')
        
        # 1. 上传文件
        files = {'file': (filename, file_content)}
        try:
            upload_url = f"{server_url}/upload"
            _logger.info(f"正在上传文件 {filename} 到 {upload_url}")
            
            # 设置较长的超时时间，因为上传可能需要时间
            upload_resp = requests.post(upload_url, files=files, timeout=30)
            upload_resp.raise_for_status()
            upload_data = upload_resp.json()
            
            if not upload_data.get('success'):
                raise UserError(_('Upload failed: %s') % upload_data.get('message'))
                
            # 获取服务器返回的保存文件名
            uploaded_filename = upload_data.get('filename')
            
            # 2. 发送打印指令
            print_payload = {
                'filename': uploaded_filename,
                'printer': self.name,
                'copies': copies
            }
            
            print_url = f"{server_url}/print_single"
            _logger.info(f"正在发送打印请求到 {print_url}: {print_payload}")
            
            print_resp = requests.post(print_url, json=print_payload, timeout=10)
            print_resp.raise_for_status()
            print_data = print_resp.json()
            
            if not print_data.get('success'):
                raise UserError(_('Print failed: %s') % print_data.get('message'))
            
            return True
            
        except Exception as e:
            _logger.error(f"Printing error: {e}")
            raise UserError(_('Printing error: %s') % str(e))

    def action_test_print(self):
        """
        测试打印功能
        生成一个简单的文本文件并发送打印。
        """
        self.ensure_one()
        # 创建测试内容
        content = b"This is a test print from Odoo Printer Service Integration.\nHello World!"
        filename = "test_print_odoo.txt"
        
        try:
            self.action_print_file(content, filename)
            # 返回成功通知
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Test print sent to %s') % self.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(str(e))
