from odoo import models, fields, api, _
import json

class PrintToServerWizard(models.TransientModel):
    """
    打印到服务器向导
    用于在前端弹出对话框，选择打印机和份数。
    """
    _name = 'print.to.server.wizard'
    _description = 'Print to Server Wizard'

    # 选择打印机
    printer_id = fields.Many2one('printer.server.printer', string='Printer', required=True)
    # 打印份数
    copies = fields.Integer(string='Copies', default=1, required=True)
    
    # 记录来源模型名称
    res_model = fields.Char(required=True)
    # 记录 ID 列表 (JSON 字符串格式)
    res_ids = fields.Char(required=True, help="JSON list of IDs")
    
    # 关联的报表动作
    report_id = fields.Many2one('ir.actions.report', string='Report', required=True, domain="[('model', '=', res_model)]")

    @api.model
    def default_get(self, fields_list):
        """
        初始化向导，从上下文获取当前选中的记录。
        """
        res = super(PrintToServerWizard, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        
        # 将 active_ids 转换为 JSON 字符串存储
        if active_ids and 'res_ids' in fields_list:
            res['res_ids'] = json.dumps(active_ids)
        
        # 设置当前模型
        if active_model and 'res_model' in fields_list:
            res['res_model'] = active_model
            
        return res

    def action_print(self):
        """
        确认打印按钮点击事件
        """
        self.ensure_one()
        # 解析 ID 列表
        ids = json.loads(self.res_ids)
        # 调用报表的远程打印方法
        return self.report_id.action_print_to_server(ids, self.printer_id.id, copies=self.copies)
