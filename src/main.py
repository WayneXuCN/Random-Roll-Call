"""
随机点名软件 - 主程序

本程序实现了一个适用于课堂教学场景的随机点名工具，
具备Excel导入、随机抽取、历史记录等功能。
"""
import sys
import os
import json
import random
from datetime import datetime
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox,
                             QGroupBox, QSpinBox, QCheckBox, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from excel_importer import ExcelImporter


class DataStorage:
    """数据存储类，管理学生名单和历史记录"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.students_file = os.path.join(data_dir, "students.json")
        self.history_file = os.path.join(data_dir, "history.json")
        self.config_file = os.path.join(data_dir, "config.json")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 初始化数据
        self.students = self.load_students()
        self.history = self.load_history()
        self.config = self.load_config()
    
    def load_students(self) -> List[str]:
        """加载学生名单"""
        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('students', [])
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取学生名单文件失败: {e}")
                return []
            except Exception as e:
                print(f"加载学生名单时发生未知错误: {e}")
                return []
        return []

    def save_students(self, students: List[str]):
        """保存学生名单"""
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            data = {'students': students, 'timestamp': datetime.now().isoformat()}
            with open(self.students_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存学生名单失败: {e}")
        except Exception as e:
            print(f"保存学生名单时发生未知错误: {e}")

    def load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('history', [])
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取历史记录文件失败: {e}")
                return []
            except Exception as e:
                print(f"加载历史记录时发生未知错误: {e}")
                return []
        return []

    def save_history(self, history: List[Dict]):
        """保存历史记录"""
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            data = {'history': history, 'timestamp': datetime.now().isoformat()}
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存历史记录失败: {e}")
        except Exception as e:
            print(f"保存历史记录时发生未知错误: {e}")

    def load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取配置文件失败: {e}")
            except Exception as e:
                print(f"加载配置时发生未知错误: {e}")
        return {
            'num_students': 1,
            'prevent_duplicate': True,
            'window_geometry': [100, 100, 800, 600]
        }

    def save_config(self, config: Dict):
        """保存配置"""
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存配置失败: {e}")
        except Exception as e:
            print(f"保存配置时发生未知错误: {e}")


class ExcelImporter:
    """Excel导入器"""

    @staticmethod
    def import_from_excel(file_path: str) -> List[str]:
        """从Excel文件导入学生姓名"""
        try:
            import pandas as pd

            # 判断文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 判断文件扩展名
            _, ext = os.path.splitext(file_path.lower())
            if ext not in ['.xlsx', '.xls']:
                raise ValueError(f"不支持的文件格式: {ext}，仅支持.xlsx和.xls")

            # 尝试读取Excel文件
            df = pd.read_excel(file_path)

            # 假设第一列是学生姓名
            if df.shape[1] >= 1:
                # 获取第一列并去除空值
                names = df.iloc[:, 0].dropna().astype(str).tolist()
                # 去除空字符串和仅包含空白字符的字符串
                names = [name.strip() for name in names if name.strip()]
                return names
            else:
                raise ValueError("Excel文件至少需要一列数据")
        except Exception as e:
            raise e

    @staticmethod
    def validate_data(names: List[str]) -> dict:
        """验证导入的数据"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'count': len(names)
        }

        # 检查是否有重复姓名
        unique_names = set(names)
        if len(unique_names) != len(names):
            duplicate_count = len(names) - len(unique_names)
            result['warnings'].append(f"发现 {duplicate_count} 个重复姓名")

        # 检查姓名长度
        for i, name in enumerate(names):
            if len(name) > 50:
                result['warnings'].append(f"第 {i+1} 行姓名过长: {name[:20]}...")

        # 检查特殊字符（可以根据需要调整）
        import re
        invalid_pattern = re.compile(r'[!@#$%^&*()+=\[\]{}|\\:";\'<>?,./]')
        for i, name in enumerate(names):
            if invalid_pattern.search(name):
                result['errors'].append(f"第 {i+1} 行姓名包含无效字符: {name}")

        if result['errors']:
            result['valid'] = False

        return result


class RandomRollCallApp(QMainWindow):
    """随机点名软件主窗口"""
    
    def __init__(self):
        super().__init__()
        self.data_storage = DataStorage()
        self.students = self.data_storage.students.copy()
        self.history = self.data_storage.history.copy()
        self.current_names = []
        self.roll_call_timer = None
        self.animation_counter = 0
        self.animation_names = []
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('随机点名系统')
        self.setGeometry(100, 100, 800, 600)
        
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#danger {
                background-color: #e74c3c;
            }
            QPushButton#danger:hover {
                background-color: #c0392b;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：学生名单和设置
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 学生名单分组
        students_group = QGroupBox("学生名单")
        students_layout = QVBoxLayout(students_group)
        
        self.students_list = QListWidget()
        self.update_students_list()
        students_layout.addWidget(self.students_list)
        
        # 导入名单按钮
        import_btn = QPushButton("导入名单")
        import_btn.clicked.connect(self.import_students)
        students_layout.addWidget(import_btn)
        
        left_layout.addWidget(students_group)
        
        # 设置分组
        settings_group = QGroupBox("设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 点名人数选择
        num_layout = QHBoxLayout()
        num_layout.addWidget(QLabel("点名人数:"))
        self.num_spinbox = QSpinBox()
        self.num_spinbox.setRange(1, 20)
        self.num_spinbox.setValue(self.data_storage.config.get('num_students', 1))
        self.num_spinbox.valueChanged.connect(self.on_num_changed)
        num_layout.addWidget(self.num_spinbox)
        settings_layout.addLayout(num_layout)
        
        # 防重复选项
        self.prevent_duplicate_cb = QCheckBox("防重复点名")
        self.prevent_duplicate_cb.setChecked(self.data_storage.config.get('prevent_duplicate', True))
        self.prevent_duplicate_cb.stateChanged.connect(self.on_prevent_duplicate_changed)
        settings_layout.addWidget(self.prevent_duplicate_cb)
        
        left_layout.addWidget(settings_group)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始点名")
        self.start_btn.clicked.connect(self.start_roll_call)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止点名")
        self.stop_btn.clicked.connect(self.stop_roll_call)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        
        reset_btn = QPushButton("重置名单")
        reset_btn.clicked.connect(self.reset_students)
        buttons_layout.addWidget(reset_btn)
        
        left_layout.addLayout(buttons_layout)
        
        # 右侧：当前结果和历史记录
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 当前点名结果显示
        current_group = QGroupBox("当前点名结果")
        current_layout = QVBoxLayout(current_group)
        
        self.current_result_label = QLabel("等待点名...")
        self.current_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.current_result_label.setFont(font)
        self.current_result_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border: 2px dashed #3498db;
                border-radius: 10px;
                padding: 20px;
                color: #2c3e50;
            }
        """)
        current_layout.addWidget(self.current_result_label)
        
        right_layout.addWidget(current_group)
        
        # 历史记录分组
        history_group = QGroupBox("历史记录")
        history_layout = QVBoxLayout(history_group)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.update_history_display()
        history_layout.addWidget(self.history_text)
        
        # 历史记录按钮
        history_btn_layout = QHBoxLayout()
        
        view_history_btn = QPushButton("查看详细历史")
        view_history_btn.clicked.connect(self.view_history)
        history_btn_layout.addWidget(view_history_btn)
        
        clear_history_btn = QPushButton("清空历史")
        clear_history_btn.setObjectName("danger")
        clear_history_btn.clicked.connect(self.clear_history)
        history_btn_layout.addWidget(clear_history_btn)
        
        history_layout.addLayout(history_btn_layout)
        
        right_layout.addWidget(history_group)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)
        
        # 设置菜单栏
        self.create_menu_bar()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        import_action = QAction('导入名单', self)
        import_action.triggered.connect(self.import_students)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出名单', self)
        # export_action.triggered.connect(self.export_students)  # 暂时未实现
        # file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 历史菜单
        history_menu = menubar.addMenu('历史')
        
        view_history_action = QAction('查看历史记录', self)
        view_history_action.triggered.connect(self.view_history)
        history_menu.addAction(view_history_action)
        
        clear_history_action = QAction('清空历史记录', self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        stats_action = QAction('统计信息', self)
        stats_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(stats_action)
    
    def load_settings(self):
        """加载设置"""
        config = self.data_storage.config
        geometry = config.get('window_geometry', [100, 100, 800, 600])
        self.setGeometry(*geometry)

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存当前配置
        self.save_settings()
        # 保存数据
        self.data_storage.students = self.students
        self.data_storage.history = self.history
        self.data_storage.save_students(self.students)
        self.data_storage.save_history(self.history)

        event.accept()

    def save_settings(self):
        """保存设置"""
        config = {
            'num_students': self.num_spinbox.value(),
            'prevent_duplicate': self.prevent_duplicate_cb.isChecked(),
            'window_geometry': [self.x(), self.y(), self.width(), self.height()]
        }
        self.data_storage.config = config
        self.data_storage.save_config(config)

    def import_students(self):
        """导入学生名单"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择学生名单文件",
            "",
            "Excel文件 (*.xlsx *.xls)"
        )

        if not file_path:
            return

        # 检查文件是否存在
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "错误", f"文件不存在: {file_path}")
            return

        try:
            new_students = ExcelImporter.import_from_excel(file_path)

            # 验证数据
            validation_result = ExcelImporter.validate_data(new_students)

            if not validation_result['valid']:
                error_msg = "\n".join(validation_result['errors'])
                QMessageBox.critical(self, "数据验证失败", f"导入的Excel文件包含错误:\n{error_msg}")
                return

            if validation_result['warnings']:
                warning_msg = "\n".join(validation_result['warnings'])
                # 显示警告但仍然允许导入
                reply = QMessageBox.question(
                    self,
                    "数据验证警告",
                    f"导入的Excel文件包含警告:\n{warning_msg}\n\n是否继续导入？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            if not new_students:
                QMessageBox.warning(self, "警告", "Excel文件中没有找到有效学生姓名！")
                return

            # 检查重复
            existing_set = set(self.students)
            new_set = set(new_students)
            duplicates = existing_set.intersection(new_set)

            if duplicates:
                reply = QMessageBox.question(
                    self,
                    "确认",
                    f"发现 {len(duplicates)} 个重复姓名，是否继续？\n重复姓名: {', '.join(list(duplicates)[:5])}{'...' if len(duplicates) > 5 else ''}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.No:
                    return

            # 合并名单
            self.students = list(existing_set.union(new_set))

            # 更新界面
            self.update_students_list()
            self.data_storage.students = self.students
            self.data_storage.save_students(self.students)

            success_msg = f"成功导入 {len(new_students)} 个学生姓名！\n当前总人数: {len(self.students)}"
            if validation_result['warnings']:
                success_msg += f"\n(包含{len(validation_result['warnings'])}个警告)"

            QMessageBox.information(self, "成功", success_msg)

        except FileNotFoundError as e:
            QMessageBox.critical(self, "文件错误", f"找不到指定文件: {str(e)}")
        except ValueError as e:
            QMessageBox.critical(self, "文件格式错误", f"Excel文件格式不正确: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
            import traceback
            print(f"导入异常: {traceback.format_exc()}")
    
    def update_students_list(self):
        """更新学生名单列表"""
        self.students_list.clear()
        self.students_list.addItems(self.students)
    
    def on_num_changed(self, value):
        """点名人数变化"""
        self.save_settings()
    
    def on_prevent_duplicate_changed(self, state):
        """防重复选项变化"""
        self.save_settings()
    
    def start_roll_call(self):
        """开始点名"""
        if not self.students:
            QMessageBox.warning(self, "警告", "请先导入学生名单！")
            return
        
        if len(self.students) < self.num_spinbox.value():
            QMessageBox.warning(self, "警告", f"学生人数({len(self.students)})少于点名人数({self.num_spinbox.value()})！")
            return
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 开始动画效果
        self.animation_counter = 0
        self.current_names = []
        
        if self.roll_call_timer:
            self.roll_call_timer.stop()
        
        self.roll_call_timer = QTimer(self)
        self.roll_call_timer.timeout.connect(self.update_roll_call_animation)
        self.roll_call_timer.start(100)  # 每100毫秒更新一次
    
    def update_roll_call_animation(self):
        """更新点名动画效果"""
        if self.animation_counter < 30:  # 动画持续3秒 (30 * 100ms)
            # 随机选择学生姓名作为动画效果，增加动画速度变化
            if self.animation_counter < 10:
                display_text = "正在随机点名..."
            elif self.animation_counter < 20:
                temp_names = random.choices(self.students, k=min(3, len(self.students)))
                display_text = "\n".join(temp_names[:self.num_spinbox.value()])
            else:
                # 接近结束时放慢速度，增加紧张感
                temp_names = random.choices(self.students, k=min(5, len(self.students)))
                display_text = "\n".join(random.sample(self.students, min(self.num_spinbox.value(), len(self.students))))

            self.current_result_label.setText(display_text)
            # 改变样式以增强动画效果
            self.current_result_label.setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    border: 2px solid #c0392b;
                    border-radius: 10px;
                    padding: 20px;
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                }
            """)
            self.animation_counter += 1
        else:
            # 停止动画并确定最终结果
            self.select_random_students()
            self.roll_call_timer.stop()
            # 恢复正常样式
            self.current_result_label.setStyleSheet("""
                QLabel {
                    background-color: #ecf0f1;
                    border: 2px dashed #3498db;
                    border-radius: 10px;
                    padding: 20px;
                    color: #2c3e50;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def stop_roll_call(self):
        """停止点名"""
        if self.roll_call_timer:
            self.roll_call_timer.stop()
        
        self.select_random_students()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def select_random_students(self):
        """选择随机学生"""
        num_to_select = self.num_spinbox.value()
        prevent_duplicate = self.prevent_duplicate_cb.isChecked()

        if not self.students:
            QMessageBox.warning(self, "警告", "学生名单为空，请先导入学生名单！")
            return

        if prevent_duplicate:
            # 防重复模式：确保不重复选择
            if len(self.students) < num_to_select:
                QMessageBox.warning(self, "警告", f"在防重复模式下，学生人数({len(self.students)})少于点名人数({num_to_select})！")
                return

            selected = random.sample(self.students, num_to_select)
        else:
            # 允许重复模式：可重复选择
            selected = random.choices(self.students, k=num_to_select)

        self.current_names = selected
        self.current_result_label.setText("\n".join(selected))

        # 记录到历史
        self.add_to_history(selected)
    
    def add_to_history(self, names: List[str]):
        """添加到历史记录"""
        try:
            timestamp = datetime.now()
            record = {
                'names': names,
                'timestamp': timestamp.isoformat(),
                'date': timestamp.strftime('%Y-%m-%d'),
                'time': timestamp.strftime('%H:%M:%S')
            }

            self.history.insert(0, record)
            self.data_storage.history = self.history
            self.data_storage.save_history(self.history)

            # 更新历史记录显示
            self.update_history_display()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加历史记录失败: {str(e)}")
            import traceback
            print(f"历史记录异常: {traceback.format_exc()}")
    
    def update_history_display(self):
        """更新历史记录显示"""
        if not self.history:
            self.history_text.setPlainText("暂无历史记录")
            return
        
        # 显示最近20条记录
        recent_history = self.history[:20]
        text = ""
        
        for record in recent_history:
            names_str = ", ".join(record['names'])
            text += f"[{record['date']} {record['time']}] {names_str}\n"
        
        self.history_text.setPlainText(text)
    
    def reset_students(self):
        """重置学生名单"""
        reply = QMessageBox.question(
            self, 
            "确认", 
            "确定要清空当前学生名单吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.students = []
            self.update_students_list()
            self.data_storage.students = self.students
            self.data_storage.save_students(self.students)
    
    def view_history(self):
        """查看详细历史记录"""
        if not self.history:
            QMessageBox.information(self, "提示", "暂无历史记录")
            return
        
        # 创建历史记录对话框
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("详细历史记录")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(dialog)
        
        history_list = QListWidget()
        for record in self.history:
            names_str = ", ".join(record['names'])
            item_text = f"[{record['date']} {record['time']}] {names_str}"
            history_list.addItem(item_text)
        
        layout.addWidget(history_list)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self, 
            "确认", 
            "确定要清空所有历史记录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history = []
            self.update_history_display()
            self.data_storage.history = self.history
            self.data_storage.save_history(self.history)
    
    def show_statistics(self):
        """显示统计信息"""
        if not self.history:
            QMessageBox.information(self, "统计信息", "暂无点名记录")
            return
        
        # 统计每个学生被点名的次数
        name_counts = {}
        for record in self.history:
            for name in record['names']:
                name_counts[name] = name_counts.get(name, 0) + 1
        
        # 按次数排序
        sorted_counts = sorted(name_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 统计信息
        total_calls = len(self.history)
        today_calls = 0
        today = datetime.now().strftime('%Y-%m-%d')
        for record in self.history:
            if record['date'] == today:
                today_calls += 1
        
        # 生成统计文本
        stats_text = f"统计信息:\n\n"
        stats_text += f"今日点名次数: {today_calls}\n"
        stats_text += f"总点名次数: {total_calls}\n\n"
        stats_text += f"各学生被点名次数排名:\n"
        
        for i, (name, count) in enumerate(sorted_counts[:10], 1):
            stats_text += f"{i}. {name}: {count}次\n"
        
        if len(sorted_counts) > 10:
            stats_text += f"\n... 还有{len(sorted_counts)-10}个学生"
        
        QMessageBox.information(self, "统计信息", stats_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("随机点名系统")
    app.setWindowIcon(QIcon())  # 可以设置图标
    
    window = RandomRollCallApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()