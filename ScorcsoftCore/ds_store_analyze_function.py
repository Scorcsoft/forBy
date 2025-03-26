import os
import time
import requests
import ds_store
# from vendor.ds_printer import Printer
from PyQt5.QtCore import Qt, QPoint
from urllib.parse import urlparse, urlunparse
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QMenu, QAction, QFileDialog, QMessageBox
from ScorcsoftUI.page_ds_store_analyze import Ui_ds_store_analyze


class Printer:
    def __init__(self, data, tree_widget):
        self.data = data
        self.tree_widget = tree_widget
        self.tree_structure = {}
        self.key_info = {}
        self.result_string = ''

    def build_tree(self):
        self.tree_structure = {}  # 清空旧数据
        for path, content in self.data.items():
            self._insert_into_tree(self.tree_structure, path, content)

    def _insert_into_tree(self, tree, path, content):
        if path.startswith('http://') or path.startswith('https://'):
            parsed_url = urlparse(path)
            base_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
            sub_path = parsed_url.path.strip("/").split("/") if parsed_url.path else []
        else:
            base_path = os.path.dirname(path)
            sub_path = []

        if base_path not in tree:
            tree[base_path] = {}

        node = tree[base_path]
        for part in sub_path:
            if part not in node:
                node[part] = {}
            node = node[part]

        self.key_info[path] = content.get("property", [])

        filtered_content = {k: v for k, v in content.items() if k not in {"property", "tested"}}
        if filtered_content:
            node.update(filtered_content)

    def populate_qtreewidget(self):
        self.tree_widget.clear()
        root_nodes = {}
        for root, sub_tree in self.tree_structure.items():
            if root not in root_nodes:
                root_item = QTreeWidgetItem(self.tree_widget, [root])
                root_nodes[root] = root_item
            else:
                root_item = root_nodes[root]
            self._add_tree_items(root_item, sub_tree, parent_path=root)
        return self.key_info

    def _add_tree_items(self, parent_item, node, parent_path=""):
        for key, value in sorted(node.items()):
            full_path = f"{parent_path}/{key}" if parent_path else key
            item = QTreeWidgetItem(parent_item, [key])
            item.setData(0, 1, full_path)  # 存储完整路径，便于双击事件获取 property
            # 目录：继续递归
            # if isinstance(value, dict):
            #     sub_keys = set(value.keys())
            #     if len(sub_keys) == 2 and sub_keys == {'property', 'tested'}:
            #         continue  # 直接作为叶子节点，不递归
            #     else:
            self._add_tree_items(item, value, full_path)  # **递归添加子目录**

    def export_to_string(self):
        self.result_string = ''
        self._print_tree(self.tree_structure)
        return self.result_string

    def _print_tree(self, node, prefix=""):
        """ 递归打印目录结构 """
        items = sorted(node.keys())
        for i in range(len(items)):
            key = items[i]
            is_last = (i == len(items) - 1)

            if is_last:
                connector = "└── "
            else:
                connector = "├── "

            self.result_string += f"{prefix}{connector}{key}\n"
            if isinstance(node[key], dict):
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._print_tree(node[key], next_prefix)

def get_ds_store_file(url=""):
    if url.startswith('http://') or url.startswith('https://'):
        try:
            req = requests.get(url)
            if req.status_code == 200:
                file = req.content
                file_save_path = os.path.abspath(f'ScorcsoftTemp/{time.time()}.ds_store')
                fp = open(file_save_path, 'wb')
                fp.write(file)
                fp.close()
            else:
                file_save_path = False
            return file_save_path
        except:
            return False
    else:
        if os.path.isfile(url):
            return url
        else:
            return False


def get_parent_directory(url):
    if url.startswith('http://') or url.startswith('https://'):
        parsed_url = urlparse(url)
        path = parsed_url.path.rstrip('/')  # 获取路径，并去除末尾的 '/'

        # 如果路径为空或路径中没有目录，则返回基础 URL
        if not path or '/' not in path:
            return urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))  # 只返回协议 + 域名部分

        # 否则，返回最后一个目录名称
        return path.split('/')[-1]
    else:
        return os.path.dirname(url)


class DSStoreAnalyze(QWidget, Ui_ds_store_analyze):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ds_store_file_path = ''
        self.model_property_list = QStandardItemModel()
        self.model_file_list = QStandardItemModel()
        self.treeView_property_viewer.setModel(self.model_property_list)

        self.resetViewer()
        self.parse_data = {}
        self.result = {}
        self.last_click_time = 0  # 记录上次点击时间
        self.current_file_path = ''
        self.current_parent_directory = ''
        self.recursive = True
        self.key_info = {}
        self.printer = False

        self.pushButton_start_analyze.clicked.connect(self.load_DS_Store_file)

    def load_DS_Store_file(self):
        self.resetViewer()
        file_path = self.lineEdit_file_path.text()
        current_parent_directory = os.path.dirname(file_path)
        if file_path.startswith('http://') or file_path.startswith('https://'):
            self.recursive = True
        else:
            self.recursive = False
        self.parse_ds_store_file(file_path, current_parent_directory)

        # 解析完成后调用：
        self.printer = Printer(self.result, self.treeWidget_file_list)
        self.printer.build_tree()
        self.key_info = self.printer.populate_qtreewidget()

        self.treeWidget_file_list.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置右键菜单策略
        self.treeWidget_file_list.customContextMenuRequested.connect(self.show_context_menu)  # 绑定信号

    def resetViewer(self):
        # 重置右侧属性表开始
        self.model_property_list.clear()
        self.model_property_list.setHorizontalHeaderLabels(["属性名", "属性值"])
        self.treeView_property_viewer.setColumnWidth(0, 200)
        self.treeView_property_viewer.setColumnWidth(1, 208)
        # 重置右侧属性表结束

        # 重置左侧文件清单开始
        self.treeWidget_file_list.clear()
        self.treeWidget_file_list.setHeaderLabel('文件及目录清单')
        notes = [
            '1. 支持递归解析',
            '    自动尝试访问子目录下的.DS_Store文件，',
            '    尽可能还原网站目录；',
            '2. 支持解析下载到本地的.DS_Store文件',
            '    不会递归解析本地.DS文件，',
            '    防止递归本地目录误报。',
            '3. 右键菜单可以查看.DS_Store文件记录的详细属性',
            '4. 右键菜单可以导出解析结果到TXT文件'
        ]
        for n in notes:
            QTreeWidgetItem(self.treeWidget_file_list, [n])
        # 重置左侧文件清单结束

        # 重置记录的本次解析结果开始
        self.parse_data = {}
        self.key_info = {}
        self.result = {}
        # 重置记录的本次解析结果开始

        # 重置递归开关开始
        self.recursive = True
        # 重置递归开关结束

    def parse_ds_store_file(self, file_path, parent_directory):
        ds_path = get_ds_store_file(file_path)
        if not ds_path:
            return

        self.current_file_path = ds_path
        parent_directory_to_display = get_parent_directory(parent_directory)
        self.current_parent_directory = parent_directory_to_display
        unable_to_parse_file_count = 1
        try:
            with ds_store.DSStore.open(ds_path, "r") as ds:
                for entry in ds:
                    if entry.filename:
                        filename = str(entry.filename)
                    else:
                        continue

                    if parent_directory not in self.parse_data.keys():
                        self.parse_data[parent_directory] = {}
                        self.result[parent_directory] = {}
                    if filename not in self.parse_data[parent_directory].keys():
                        self.parse_data[parent_directory][filename] = {
                            'property': [],
                            'tested': False
                        }
                        self.result[parent_directory][filename] = {}

                    entry_type = str(entry.type) if entry.type else None
                    if entry_type is None:
                        entry_type = f"{entry.type}"
                    if entry_type == "<class 'ds_store.store.ILocCodec'>":
                        entry_type = "ILocCodec (文件存放坐标)"
                    elif entry_type == "<class 'ds_store.store.PlistCodec'>":
                        entry_type = "PList (Finder显示所需数据)"
                    elif entry_type == "b'bool'":
                        entry_type = "bool [b'bool']"
                    elif entry_type == "b'long'":
                        entry_type = "long [b'long']"
                    elif entry_type == "b'blob'":
                        entry_type = "blob [b'blob']"
                    elif entry_type == "b'ustr'":
                        entry_type = "ustr (文件描述)"
                    elif isinstance(entry.value, bytes):
                        entry_type = f"{entry.type}"
                    elif isinstance(entry.value, int):
                        entry_type = f"{entry.type}"
                    else:
                        entry_type = f"{entry.type}"

                    if isinstance(entry.value, dict):
                        entry_value = "\n"
                        for k in entry.value:
                            entry_value += f"{k}: {entry.value[k]}\n"
                    else:
                        entry_value = str(entry.value)

                    self.parse_data[parent_directory][filename]['property'].append([entry_type, entry_value])

                    if self.recursive:
                        if not self.parse_data[parent_directory][filename]['tested']:
                            self.parse_data[parent_directory][filename]['tested'] = True
                            current_file_path = os.path.join(parent_directory, filename, '.DS_Store')
                            current_parent_directory = os.path.join(parent_directory, filename)
                            self.parse_ds_store_file(current_file_path, current_parent_directory)
            os.remove(ds_path)
        except Exception as e:
            error_item = QStandardItem("解析错误")
            self.model_property_list.appendRow([error_item, QStandardItem(str(e)), QStandardItem("")])

    def show_property_to_viewer(self, property_data):
        for i in property_data:
            type_item = QStandardItem(i[0])
            value_item = QStandardItem(i[1])
            self.model_property_list.appendRow([type_item, value_item])

    def show_property(self, item, menu):
        menu.close()
        current_time = time.time()
        if current_time - self.last_click_time < 0.3:
            return
        self.last_click_time = current_time

        # 重置右侧属性表开始
        self.model_property_list.clear()
        self.model_property_list.setHorizontalHeaderLabels(["属性名", "属性值"])
        self.treeView_property_viewer.setColumnWidth(0, 200)
        self.treeView_property_viewer.setColumnWidth(1, 208)
        # 重置右侧属性表结束

        key = item.data(0, 1)
        if key is None:
            return
        if key in self.parse_data.keys():  # 这是一个目录
            if key in self.parse_data.keys() and 'property' in self.parse_data[key].keys():
                self.show_property_to_viewer(self.parse_data[key]['property'])
            else:
                path_name = os.path.dirname(key)
                key_name = os.path.basename(key)
                if path_name in self.parse_data.keys() and key_name in self.parse_data[path_name].keys():
                    if 'property' in self.parse_data[path_name][key_name].keys():
                        self.show_property_to_viewer(self.parse_data[path_name][key_name]['property'])
        else:
            path_name = os.path.dirname(key)
            key_name = os.path.basename(key)
            if path_name in self.parse_data.keys() and key_name in self.parse_data[path_name].keys():
                if 'property' in self.parse_data[path_name][key_name].keys():
                    self.show_property_to_viewer(self.parse_data[path_name][key_name]['property'])

    def export_to_file(self, menu):
        menu.close()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "","Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            try:
                result = self.printer.export_to_string()
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(result)
                QMessageBox.information(None, "导出", f"解析结果导出成功，文件路径：<br> {file_path}")
            except Exception as e:
                QMessageBox.warning(None, "错误", f"导出到文件失败，错误：<br><br>{e}")

    def show_context_menu(self, position: QPoint):
        item = self.treeWidget_file_list.itemAt(position)  # 获取鼠标位置的项
        if item:
            menu = QMenu(self)  # 创建菜单
            action_show_property = QAction("查看属性", self)
            action_export_to_file = QAction("导出结果到TXT文件", self)

            # 连接菜单项到槽函数
            action_show_property.triggered.connect(lambda: self.show_property(item, menu))
            action_export_to_file.triggered.connect(lambda: self.export_to_file(menu))

            # 添加菜单项到菜单
            menu.addAction(action_show_property)
            menu.addSeparator()  # 添加分隔符
            menu.addAction(action_export_to_file)

            # 显示菜单
            menu.exec_(self.treeWidget_file_list.viewport().mapToGlobal(position))

    

