from odoo import models, api, _
from odoo.exceptions import UserError

class IrActionsReport(models.Model):
    """
    继承报表动作模型
    添加将报表发送到远程打印机的功能。
    """
    _inherit = 'ir.actions.report'

    def action_print_to_server(self, res_ids, printer_id, copies=1):
        """
        生成 PDF 并发送到打印服务器
        :param res_ids: 要打印的记录 ID 列表
        :param printer_id: 目标打印机 ID (printer.server.printer)
        :param copies: 份数
        """
        self.ensure_one()
        if not printer_id:
            raise UserError(_("No printer selected."))
            
        printer = self.env['printer.server.printer'].browse(printer_id)
        if not printer.exists():
             raise UserError(_("Selected printer not found."))

        try:
            # 1. 生成 PDF 内容
            # _render_qweb_pdf 返回 (pdf_content, content_type)
            content, _content_type = self._render_qweb_pdf(res_ids)
            
            # 2. 生成文件名
            filename = f"{self.name}_{len(res_ids)}_records.pdf"
            
            # 3. 调用打印机模型的打印方法
            printer.action_print_file(content, filename, copies=copies)
            
            # 4. 返回成功通知
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Document sent to printer %s') % printer.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Failed to print: %s") % str(e))
