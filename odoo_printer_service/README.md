# Odoo Printer Service Integration Module
# Odoo 打印服务集成模块文档

## 1. Module Overview / 模块概述

**Technical Name**: `odoo_printer_service`
**Summary**: Integration with external PrinterService for remote/driverless printing.
**Description**:
This module enables Odoo to print PDF reports directly to a local printer connected to a Windows PC running the `PrinterService` agent. It bypasses the need for client-side printer drivers (e.g., on mobile phones) by sending print jobs via HTTP API to the Windows print node.
本模块允许 Odoo 将 PDF 报表直接发送到运行 `PrinterService` 代理的 Windows 电脑上的打印机。它通过 HTTP API 发送打印任务，从而无需在客户端（如手机）安装打印机驱动。

---

## 2. Deployment Guide / 部署指南

### Prerequisites / 前置条件
*   Odoo 17 (Community or Enterprise).
*   A Windows PC running `PrinterService` (see main project README).

### Installation Steps / 安装步骤

1.  **Copy Files / 复制文件**:
    Copy the `odoo_printer_service` folder to your Odoo custom addons directory.
    将 `odoo_printer_service` 文件夹复制到您的 Odoo 自定义插件目录。

2.  **Restart Odoo / 重启 Odoo**:
    Restart the Odoo service to recognize the new module path.
    重启 Odoo 服务以识别新模块路径。

3.  **Install in GUI / 在界面安装**:
    *   Activate Developer Mode (Settings -> Scroll down -> Activate the developer mode).
        开启开发者模式。
    *   Go to **Apps** (应用).
    *   Click **Update Apps List** (更新应用列表).
    *   Search for `Printer Service Integration`.
    *   Click **Activate** (激活/安装).

---

## 3. Configuration / 配置

1.  Navigate to **Printer Service** > **Configuration** > **Servers**.
    进入 **打印服务** > **配置** > **服务器**。
2.  Create a new server record:
    *   **Name**: A descriptive name (e.g., "Office PC").
    *   **Server URL**: The IP address of the Windows PC running the service (e.g., `http://192.168.1.100:5000`).
3.  Click **Fetch Printers** to sync the available printers from that PC.
    点击 **获取打印机** 同步打印机列表。
4.  (Optional) Click **Test Print** on a printer to verify connectivity.
    (可选) 点击打印机上的 **Test Print** 验证连接。

---

## 4. Full Source Code Reference / 完整源代码参考

Below is the complete source code for the module with detailed comments.
以下是带有详细注释的模块完整源代码。

### 4.1. Manifest (`__manifest__.py`)
Defines the module metadata and dependencies.

```python
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
        'views/print_server_views.xml',
        'wizard/print_to_server_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
```

### 4.2. Models

#### `models/__init__.py`
```python
from . import print_server
from . import ir_actions_report
```

#### `models/print_server.py`
Handles server connection and API calls.

```python
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
    
    # 关联的打印机列表
    printer_ids = fields.One2many('printer.server.printer', 'server_id', string='Printers')

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
```

#### `models/ir_actions_report.py`
Extends default report action.

```python
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
```

### 4.3. Views (`views/print_server_views.xml`)
Defines the UI for configuring servers and printers.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Printer Server Views / 打印服务器视图 -->
        
        <!-- 表单视图 -->
        <record id="view_printer_server_form" model="ir.ui.view">
            <field name="name">printer.server.form</field>
            <field name="model">printer.server</field>
            <field name="arch" type="xml">
                <form string="Printer Server">
                    <header>
                        <!-- 获取打印机按钮 -->
                        <button name="action_fetch_printers" string="Fetch Printers" type="object" class="oe_highlight"/>
                    </header>
                    <sheet>
                        <div class="oe_title">
                            <label for="name" class="oe_edit_only"/>
                            <h1><field name="name"/></h1>
                        </div>
                        <group>
                            <!-- 服务器 URL 配置 -->
                            <field name="url" placeholder="http://192.168.1.xxx:5000"/>
                            <field name="active"/>
                        </group>
                        <notebook>
                            <page string="Printers">
                                <!-- 打印机列表 -->
                                <field name="printer_ids">
                                    <tree editable="bottom">
                                        <field name="name"/>
                                        <!-- 测试打印按钮 -->
                                        <button name="action_test_print" string="Test Print" type="object" icon="fa-print"/>
                                    </tree>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                </form>
            </field>
        </record>

        <!-- 列表视图 -->
        <record id="view_printer_server_tree" model="ir.ui.view">
            <field name="name">printer.server.tree</field>
            <field name="model">printer.server</field>
            <field name="arch" type="xml">
                <tree string="Printer Servers">
                    <field name="name"/>
                    <field name="url"/>
                    <field name="active"/>
                </tree>
            </field>
        </record>

        <!-- 动作定义 -->
        <record id="action_printer_server" model="ir.actions.act_window">
            <field name="name">Printer Servers</field>
            <field name="res_model">printer.server</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Define a new Printer Server
                </p>
                <p>
                    Connect to your local PrinterService instance.
                </p>
            </field>
        </record>

        <!-- 菜单定义 -->
        <!-- 主菜单 -->
        <menuitem id="menu_printer_service_root" name="Printer Service" web_icon="odoo_printer_service,static/description/icon.png" groups="base.group_user"/>
        <!-- 子菜单 -->
        <menuitem id="menu_printer_server" name="Servers" parent="menu_printer_service_root" action="action_printer_server"/>

    </data>
</odoo>
```

### 4.4. Wizard

#### `wizard/__init__.py`
```python
from . import print_to_server_wizard
```

#### `wizard/print_to_server_wizard.py`
```python
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
```

#### `wizard/print_to_server_wizard_views.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- 向导视图 -->
    <record id="view_print_to_server_wizard_form" model="ir.ui.view">
        <field name="name">print.to.server.wizard.form</field>
        <field name="model">print.to.server.wizard</field>
        <field name="arch" type="xml">
            <form string="Print to Server">
                <group>
                    <!-- 选择打印机 -->
                    <field name="printer_id"/>
                    <!-- 份数 -->
                    <field name="copies"/>
                    <!-- 关联报表 (只读) -->
                    <field name="report_id" readonly="1"/>
                </group>
                <footer>
                    <!-- 确认按钮 -->
                    <button name="action_print" string="Print" type="object" class="btn-primary"/>
                    <!-- 取消按钮 -->
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

### 4.5. Security (`security/ir.model.access.csv`)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_printer_server,printer.server,model_printer_server,base.group_user,1,1,1,1
access_printer_server_printer,printer.server.printer,model_printer_server_printer,base.group_user,1,1,1,1
access_print_to_server_wizard,print.to.server.wizard,model_print_to_server_wizard,base.group_user,1,1,1,1
```

### 4.6. Init (`__init__.py`)
```python
from . import models
from . import wizard
```
