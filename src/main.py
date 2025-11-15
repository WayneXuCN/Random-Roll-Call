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
from typing import List, Dict
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QSpinBox,
    QCheckBox,
    QTextEdit,
    QSplitter,
    QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from excel_importer import ExcelImporter


class DataStorage:
    """数据存储类，管理学生名单和历史记录"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.students_file = os.path.join(data_dir, "students.json")
        self.classes_file = os.path.join(
            data_dir, "classes.json"
        )  # New file for multiple classes
        self.history_file = os.path.join(data_dir, "history.json")
        self.config_file = os.path.join(data_dir, "config.json")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 初始化数据
        self.classes = self.load_classes()  # Dictionary of class_name -> student_list
        self.current_class = self.load_current_class()  # Track current active class
        self.history = self.load_history()
        self.config = self.load_config()

    def load_students(self) -> List[str]:
        """加载学生名单"""
        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("students", [])
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取学生名单文件失败: {e}")
                return []
            except Exception as e:
                print(f"加载学生名单时发生未知错误: {e}")
                return []
        return []

    def load_classes(self) -> Dict[str, List[str]]:
        """加载所有班级列表"""
        if os.path.exists(self.classes_file):
            try:
                with open(self.classes_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("classes", {})
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取班级列表文件失败: {e}")
                # 尝试 loading from old format
                return self.migrate_from_old_format()
            except Exception as e:
                print(f"加载班级列表时发生未知错误: {e}")
                return self.migrate_from_old_format()
        else:
            # Migrate from old format if classes file doesn't exist
            return self.migrate_from_old_format()

    def migrate_from_old_format(self) -> Dict[str, List[str]]:
        """从旧格式迁移数据到新格式"""
        # If there's an existing students.json, move it to a default class
        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    old_students = old_data.get("students", [])
                    if old_students:
                        return {"默认班级": old_students}
            except Exception:
                pass  # If migration fails, start fresh
        return {"默认班级": []}

    def load_current_class(self) -> str:
        """加载当前选中的班级"""
        if os.path.exists(self.classes_file):
            try:
                with open(self.classes_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("current_class", "默认班级")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取当前班级失败: {e}")
            except Exception as e:
                print(f"加载当前班级时发生未知错误: {e}")
        return "默认班级"

    def save_classes(self):
        """保存所有班级列表"""
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            data = {
                "classes": self.classes,
                "current_class": self.current_class,
                "timestamp": datetime.now().isoformat(),
            }
            with open(self.classes_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存班级列表失败: {e}")
        except Exception as e:
            print(f"保存班级列表时发生未知错误: {e}")

    def get_current_students(self) -> List[str]:
        """获取当前班级的学生列表"""
        if self.current_class in self.classes:
            return self.classes[self.current_class]
        else:
            # If current class doesn't exist, create it with empty list
            self.classes[self.current_class] = []
            return []

    def set_current_students(self, students: List[str]):
        """设置当前班级的学生列表"""
        self.classes[self.current_class] = students
        self.save_classes()

    def save_students(self, students: List[str]):
        """保存学生名单（现在是当前选中班级的名单）"""
        self.set_current_students(students)
        # Also save to old format for compatibility (deprecated)
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            data = {"students": students, "timestamp": datetime.now().isoformat()}
            with open(self.students_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存学生名单失败: {e}")
        except Exception as e:
            print(f"保存学生名单时发生未知错误: {e}")

    def load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("history", [])
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

            data = {"history": history, "timestamp": datetime.now().isoformat()}
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存历史记录失败: {e}")
        except Exception as e:
            print(f"保存历史记录时发生未知错误: {e}")

    def load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"读取配置文件失败: {e}")
            except Exception as e:
                print(f"加载配置时发生未知错误: {e}")
        return {
            "num_students": 1,
            "prevent_duplicate": True,
            "window_geometry": [100, 100, 800, 600],
        }

    def save_config(self, config: Dict):
        """保存配置"""
        try:
            # 确保数据目录存在
            os.makedirs(self.data_dir, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            print(f"保存配置失败: {e}")
        except Exception as e:
            print(f"保存配置时发生未知错误: {e}")


class RandomRollCallApp(QMainWindow):
    """随机点名软件主窗口"""

    def __init__(self):
        super().__init__()
        self.data_storage = DataStorage()
        self.students = self.data_storage.get_current_students().copy()
        self.history = self.data_storage.history.copy()
        self.current_names = []
        self.roll_call_timer = None
        self.animation_counter = 0
        self.animation_names = []
        self.allow_duplicate_names = False  # 是否允许重复姓名

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("随机点名助手")
        self.setGeometry(100, 100, 900, 700)  # 增加窗口大小以改善布局

        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f5f2;
            }
            QLabel {
                color: #232323;  /* 更深的颜色，提高对比度 */
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #078080;
                color: #fffffe;  /* 白色文字，更好对比 */
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #067070;
            }
            QPushButton:pressed {
                background-color: #056060;
            }
            QPushButton#danger {
                background-color: #f45d48;
                color: #fffffe;
            }
            QPushButton#danger:hover {
                background-color: #e44d38;
            }
            QListWidget {
                background-color: #fffffe;
                border: 2px solid #232323;  /* 更粗的边框 */
                border-radius: 6px;
                color: #232323;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #232323;
                border: 2px solid #078080;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px 5px 10px;
                color: #232323;
                background-color: #f8f5f2;
                font-weight: bold;
                font-size: 15px;
            }
            QComboBox {
                background-color: #fffffe;
                border: 2px solid #232323;
                border-radius: 6px;
                padding: 8px;
                color: #232323;
                font-size: 14px;
            }
            QComboBox:hover {
                background-color: #f0efee;
            }
            QSpinBox {
                background-color: #fffffe;
                border: 2px solid #232323;
                border-radius: 6px;
                color: #232323;
                padding: 5px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #fffffe;
                border: 2px solid #232323;
                border-radius: 6px;
                color: #232323;
                font-size: 14px;
            }
            QCheckBox {
                color: #232323;
                font-weight: bold;
                font-size: 14px;
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

        # 班级选择分组
        class_group = QGroupBox("班级管理")
        class_layout = QVBoxLayout(class_group)

        # 班级选择下拉框
        class_selector_layout = QHBoxLayout()
        class_selector_layout.addWidget(QLabel("选择班级:"))
        self.class_selector = QComboBox()
        self.update_class_selector()  # 初始化下拉框
        self.class_selector.currentTextChanged.connect(self.on_class_changed)
        class_selector_layout.addWidget(self.class_selector)
        class_layout.addLayout(class_selector_layout)

        # 班级操作按钮
        class_btn_layout = QHBoxLayout()

        add_class_btn = QPushButton("添加班级")
        add_class_btn.clicked.connect(self.add_class)
        class_btn_layout.addWidget(add_class_btn)

        rename_class_btn = QPushButton("重命名班级")
        rename_class_btn.clicked.connect(self.rename_class)
        class_btn_layout.addWidget(rename_class_btn)

        delete_class_btn = QPushButton("删除班级")
        delete_class_btn.clicked.connect(self.delete_class)
        class_btn_layout.addWidget(delete_class_btn)

        class_layout.addLayout(class_btn_layout)

        left_layout.addWidget(class_group)

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

        # 手动输入按钮
        manual_input_btn = QPushButton("手动添加姓名")
        manual_input_btn.clicked.connect(self.manual_input_student)
        students_layout.addWidget(manual_input_btn)

        # 手动移除按钮
        manual_remove_btn = QPushButton("移除选中姓名")
        manual_remove_btn.clicked.connect(self.manual_remove_student)
        students_layout.addWidget(manual_remove_btn)

        left_layout.addWidget(students_group)

        # 设置分组
        settings_group = QGroupBox("设置")
        settings_layout = QVBoxLayout(settings_group)

        # 点名人数选择
        num_layout = QHBoxLayout()
        num_layout.addWidget(QLabel("点名人数:"))
        self.num_spinbox = QSpinBox()
        self.num_spinbox.setRange(1, 20)
        self.num_spinbox.setValue(self.data_storage.config.get("num_students", 1))
        self.num_spinbox.valueChanged.connect(self.on_num_changed)
        num_layout.addWidget(self.num_spinbox)
        settings_layout.addLayout(num_layout)

        # 防重复选项
        self.prevent_duplicate_cb = QCheckBox("防重复点名")
        self.prevent_duplicate_cb.setChecked(
            self.data_storage.config.get("prevent_duplicate", True)
        )
        self.prevent_duplicate_cb.stateChanged.connect(
            self.on_prevent_duplicate_changed
        )
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
        font.setPointSize(26)  # 增大字体
        font.setBold(True)
        self.current_result_label.setFont(font)
        self.current_result_label.setStyleSheet("""
            QLabel {
                background-color: #fffffe;
                border: 4px solid #078080;
                border-radius: 20px;
                padding: 40px;
                color: #232323;
                qproperty-alignment: 'AlignCenter';
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
        splitter.setSizes([400, 500])  # 调整比例使界面更平衡

        main_layout.addWidget(splitter)

        # 设置菜单栏
        self.create_menu_bar()

    def create_menu_bar(self):
        """创建菜单栏"""

        menubar = self.menuBar()

        # 为了解决Pylance报错，添加类型检查
        if menubar is None:
            return

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        import_action = QAction("导入名单", self)
        import_action.triggered.connect(self.import_students)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 历史菜单
        history_menu = menubar.addMenu("历史")

        view_history_action = QAction("查看历史记录", self)
        view_history_action.triggered.connect(self.view_history)
        history_menu.addAction(view_history_action)

        clear_history_action = QAction("清空历史记录", self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具")

        stats_action = QAction("统计信息", self)
        stats_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(stats_action)

        clear_all_action = QAction("清空学生名单", self)
        clear_all_action.triggered.connect(self.clear_all_students)
        tools_menu.addAction(clear_all_action)

    def load_settings(self):
        """加载设置"""
        config = self.data_storage.config
        geometry = config.get("window_geometry", [100, 100, 800, 600])
        self.setGeometry(*geometry)

    def clear_all_students(self):
        """清空所有学生名单"""
        if not self.students:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.information(self, "提示", "学生名单已经是空的！")
            return

        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确定要清空所有 {len(self.students)} 个学生姓名吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.students = []
            self.update_students_list()
            self.data_storage.set_current_students(self.students)  # Use the new method
            self.data_storage.save_classes()  # Save all class data
            QMessageBox.information(self, "成功", "学生名单已清空！")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存当前配置
        self.save_settings()
        # 保存数据
        self.data_storage.set_current_students(self.students)  # Use the new method
        self.data_storage.history = self.history
        self.data_storage.save_classes()  # Save all class data
        self.data_storage.save_history(self.history)

        event.accept()

    def save_settings(self):
        """保存设置"""
        config = {
            "num_students": self.num_spinbox.value(),
            "prevent_duplicate": self.prevent_duplicate_cb.isChecked(),
            "window_geometry": [self.x(), self.y(), self.width(), self.height()],
        }
        self.data_storage.config = config
        self.data_storage.save_config(config)

    def import_students(self):
        """导入学生名单"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择学生名单文件", "", "Excel文件 (*.xlsx *.xls)"
        )

        if not file_path:
            return

        # 检查文件是否存在
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "错误", f"文件不存在: {file_path}")
            return

        try:
            new_students = ExcelImporter.import_from_excel(file_path)

            # 验证数据，传入现有的学生名单进行重复检查
            validation_result = ExcelImporter.validate_data(new_students, self.students)

            if not validation_result["valid"]:
                error_msg = "\n".join(validation_result["errors"])
                QMessageBox.critical(
                    self, "数据验证失败", f"导入的Excel文件包含错误:\n{error_msg}"
                )
                return

            if validation_result["warnings"]:
                warning_msg = "\n".join(validation_result["warnings"])
                # 显示警告但仍然允许导入
                reply = QMessageBox.question(
                    self,
                    "数据验证警告",
                    f"导入的Excel文件包含警告:\n{warning_msg}\n\n是否继续导入？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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
                    f"发现 {len(duplicates)} 个重复姓名，是否继续导入（包括重复的）？\n重复姓名: {', '.join(list(duplicates)[:5])}{'...' if len(duplicates) > 5 else ''}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.No:
                    # 只导入不重复的学生
                    new_students = [
                        name for name in new_students if name not in existing_set
                    ]
                    # 仍然使用智能合并方法，但不保留重复项
                    self.students = self.merge_student_lists(
                        self.students, new_students, keep_duplicates=False
                    )
                else:
                    # 导入所有学生，包括重复的
                    self.students = self.merge_student_lists(
                        self.students, new_students, keep_duplicates=True
                    )
            else:
                # 没有重复，直接导入
                self.students = self.merge_student_lists(
                    self.students, new_students, keep_duplicates=True
                )

            # 更新界面
            self.update_students_list()
            self.data_storage.set_current_students(self.students)  # Use the new method
            self.data_storage.save_classes()  # Save all class data

            success_msg = f"成功导入 {len(new_students)} 个学生姓名！\n当前总人数: {len(self.students)}"
            if validation_result["warnings"]:
                success_msg += f"\n(包含{len(validation_result['warnings'])}个警告)"

            # 如果有重复姓名，在消息中显示详情
            if validation_result["duplicates"]:
                dup_msg = f"\n重复姓名: {', '.join(validation_result['duplicates'][:5])}{'...' if len(validation_result['duplicates']) > 5 else ''}"
                success_msg += dup_msg

            QMessageBox.information(self, "成功", success_msg)

        except FileNotFoundError as e:
            QMessageBox.critical(self, "文件错误", f"找不到指定文件: {str(e)}")
        except ValueError as e:
            QMessageBox.critical(self, "文件格式错误", f"Excel文件格式不正确: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")
            import traceback

            print(f"导入异常: {traceback.format_exc()}")

    def manual_input_student(self):
        """手动添加学生姓名"""
        from PyQt6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QMessageBox,
        )

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("手动添加学生姓名")
        dialog.setGeometry(300, 300, 400, 150)

        layout = QVBoxLayout(dialog)

        # 输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("学生姓名:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("输入学生姓名，多个姓名用逗号分隔")
        input_layout.addWidget(name_input)
        layout.addLayout(input_layout)

        # 按钮
        button_layout = QHBoxLayout()

        add_btn = QPushButton("添加")
        add_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(add_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            input_text = name_input.text().strip()
            if not input_text:
                QMessageBox.warning(self, "警告", "请输入学生姓名！")
                return

            # 分割输入的姓名（支持逗号分隔）
            new_names = [name.strip() for name in input_text.split(",") if name.strip()]

            if not new_names:
                QMessageBox.warning(self, "警告", "未检测到有效姓名！")
                return

            # 验证输入的姓名
            validation_result = ExcelImporter.validate_data(new_names, self.students)

            if not validation_result["valid"]:
                error_msg = "\n".join(validation_result["errors"])
                QMessageBox.critical(
                    self, "输入验证失败", f"输入包含错误:\n{error_msg}"
                )
                return

            # 询问是否保留重复姓名
            if validation_result["warnings"]:
                warning_msg = "\n".join(validation_result["warnings"])
                reply = QMessageBox.question(
                    self,
                    "输入验证警告",
                    f"输入包含警告:\n{warning_msg}\n\n是否继续添加？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            # 检查是否有重复（内部重复或与现有名单重复）
            existing_set = set(self.students)
            unique_new_names = set()
            for name in new_names:
                if name not in existing_set and name not in unique_new_names:
                    unique_new_names.add(name)

            # 询问是否添加重复姓名
            duplicate_with_existing = [
                name for name in new_names if name in existing_set
            ]
            unique_new = [name for name in new_names if name not in existing_set]

            if duplicate_with_existing and unique_new:
                # 有重复也有不重复的，询问如何处理
                reply = QMessageBox.question(
                    self,
                    "重复姓名",
                    f"发现 {len(duplicate_with_existing)} 个重复姓名，是否继续导入（包括重复的）？\n重复姓名: {', '.join(duplicate_with_existing[:5])}{'...' if len(duplicate_with_existing) > 5 else ''}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 导入所有姓名，包括重复的
                    names_to_add = new_names
                else:
                    # 只导入不重复的姓名
                    names_to_add = unique_new
            elif duplicate_with_existing and not unique_new:
                # 所有输入都与现有名单重复
                reply = QMessageBox.question(
                    self,
                    "重复姓名",
                    f"所有输入的姓名都已存在，是否仍然添加？\n姓名: {', '.join(duplicate_with_existing[:5])}{'...' if len(duplicate_with_existing) > 5 else ''}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    names_to_add = duplicate_with_existing
                else:
                    names_to_add = []  # 不添加任何姓名
            else:
                # 没有重复，全部导入
                names_to_add = new_names

            # 添加新姓名到列表
            added_count = 0
            for name in names_to_add:
                self.students.append(name)  # 允许添加（包括可能的重复）
                added_count += 1

            # 更新界面
            self.update_students_list()
            self.data_storage.set_current_students(self.students)  # Use the new method
            self.data_storage.save_classes()  # Save all class data

            success_msg = f"成功添加 {added_count} 个新学生姓名！\n当前总人数: {len(self.students)}"

            # 如果有重复姓名，在消息中显示详情
            if validation_result["duplicates"]:
                dup_msg = f"\n重复姓名已跳过: {', '.join(validation_result['duplicates'][:5])}{'...' if len(validation_result['duplicates']) > 5 else ''}"
                success_msg += dup_msg

            QMessageBox.information(self, "成功", success_msg)

    def manual_remove_student(self):
        """手动移除选中的学生姓名"""
        from PyQt6.QtWidgets import QMessageBox

        # 获取选中的项目
        selected_items = self.students_list.selectedItems()

        if not selected_items:
            QMessageBox.information(self, "提示", "请先选择要移除的学生姓名！")
            return

        # 获取要移除的姓名
        names_to_remove = [item.text() for item in selected_items]

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(names_to_remove)} 个学生姓名吗？\n{', '.join(names_to_remove[:5])}{'...' if len(names_to_remove) > 5 else ''}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 从学生列表中移除选中的姓名
            for name in names_to_remove:
                if name in self.students:
                    self.students.remove(name)

            # 更新界面
            self.update_students_list()
            self.data_storage.set_current_students(self.students)  # Use the new method
            self.data_storage.save_classes()  # Save all class data

            QMessageBox.information(
                self,
                "成功",
                f"成功删除 {len(names_to_remove)} 个学生姓名！\n当前总人数: {len(self.students)}",
            )

    def merge_student_lists(
        self,
        existing_list: List[str],
        new_list: List[str],
        keep_duplicates: bool = False,
    ) -> List[str]:
        """智能合并学生名单，处理重复项"""
        # 使用现有列表作为基础
        result = existing_list.copy()

        if keep_duplicates:
            # If allowed to keep duplicates, simply append all new names
            result.extend(new_list)
        else:
            # Add only new names that don't already exist
            existing_set = set(existing_list)
            for student in new_list:
                if student not in existing_set:
                    result.append(student)
                    existing_set.add(student)

        return result

    def update_class_selector(self):
        """更新班级选择下拉框"""
        self.class_selector.clear()
        class_names = list(self.data_storage.classes.keys())
        self.class_selector.addItems(class_names)

        # Set the current class as selected
        if self.data_storage.current_class in class_names:
            self.class_selector.setCurrentText(self.data_storage.current_class)

    def on_class_changed(self, class_name: str):
        """班级选择改变时的处理"""
        if class_name and class_name != self.data_storage.current_class:
            # Save current class data before switching
            self.data_storage.set_current_students(self.students)

            # Update current class
            self.data_storage.current_class = class_name

            # Load new class data
            self.students = self.data_storage.get_current_students().copy()
            self.update_students_list()

            # Save the updated current class setting
            self.data_storage.save_classes()

    def add_class(self):
        """添加新班级"""
        from PyQt6.QtWidgets import QInputDialog

        new_class, ok = QInputDialog.getText(self, "添加班级", "请输入新班级名称:")
        if ok and new_class.strip():
            new_class = new_class.strip()
            if new_class in self.data_storage.classes:
                QMessageBox.warning(self, "警告", f"班级 '{new_class}' 已存在！")
                return

            # Add the new class with empty student list
            self.data_storage.classes[new_class] = []
            self.data_storage.save_classes()

            # Update the selector and switch to the new class
            self.update_class_selector()
            self.class_selector.setCurrentText(new_class)

            QMessageBox.information(self, "成功", f"班级 '{new_class}' 添加成功！")
        elif ok:
            QMessageBox.warning(self, "警告", "班级名称不能为空！")

    def rename_class(self):
        """重命名当前班级"""
        from PyQt6.QtWidgets import QInputDialog

        current_class = self.data_storage.current_class
        if current_class == "默认班级" and len(self.data_storage.classes) == 1:
            QMessageBox.information(self, "提示", "不能重命名最后一个默认班级！")
            return

        new_name, ok = QInputDialog.getText(
            self, "重命名班级", "请输入新班级名称:", text=current_class
        )
        if ok and new_name.strip() and new_name.strip() != current_class:
            new_name = new_name.strip()
            if new_name in self.data_storage.classes:
                QMessageBox.warning(self, "警告", f"班级 '{new_name}' 已存在！")
                return

            # Save current students before renaming
            current_students = self.data_storage.get_current_students()

            # Remove old class and add new one
            del self.data_storage.classes[current_class]
            self.data_storage.classes[new_name] = current_students
            self.data_storage.current_class = new_name

            self.data_storage.save_classes()

            # Update UI
            self.update_class_selector()
            self.class_selector.setCurrentText(new_name)

            QMessageBox.information(self, "成功", f"班级已重命名为 '{new_name}'！")
        elif ok and new_name.strip() == current_class:
            QMessageBox.information(self, "提示", "新名称与当前名称相同，无需重命名。")
        elif ok:
            QMessageBox.warning(self, "警告", "班级名称不能为空！")

    def delete_class(self):
        """删除当前班级"""
        current_class = self.data_storage.current_class
        if len(self.data_storage.classes) <= 1:
            QMessageBox.warning(self, "警告", "不能删除最后一个班级！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除班级 '{current_class}' 吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete the class
            del self.data_storage.classes[current_class]

            # Switch to the first available class
            available_classes = list(self.data_storage.classes.keys())
            self.data_storage.current_class = available_classes[0]

            # Update current students to the new class
            self.students = self.data_storage.get_current_students().copy()

            self.data_storage.save_classes()

            # Update UI
            self.update_class_selector()
            self.update_students_list()
            QMessageBox.information(
                self,
                "成功",
                f"班级 '{current_class}' 已删除，已切换到 '{available_classes[0]}'。",
            )

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
            QMessageBox.warning(
                self,
                "警告",
                f"学生人数({len(self.students)})少于点名人数({self.num_spinbox.value()})！",
            )
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
                display_text = "\n".join(temp_names[: self.num_spinbox.value()])
            else:
                # 接近结束时放慢速度，增加紧张感
                temp_names = random.choices(self.students, k=min(5, len(self.students)))
                display_text = "\n".join(
                    random.sample(
                        self.students, min(self.num_spinbox.value(), len(self.students))
                    )
                )

            self.current_result_label.setText(display_text)
            # 改变样式以增强动画效果
            self.current_result_label.setStyleSheet("""
                QLabel {
                    background-color: #f45d48;
                    border: 4px solid #232323;
                    border-radius: 20px;
                    padding: 40px;
                    color: #fffffe;
                    font-size: 32px;  /* 更大字体 */
                    font-weight: bold;
                    qproperty-alignment: 'AlignCenter';
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
                    background-color: #fffffe;
                    border: 4px solid #078080;
                    border-radius: 20px;
                    padding: 40px;
                    color: #232323;
                    font-size: 28px;  /* 更大字体 */
                    font-weight: bold;
                    qproperty-alignment: 'AlignCenter';
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
                QMessageBox.warning(
                    self,
                    "警告",
                    f"在防重复模式下，学生人数({len(self.students)})少于点名人数({num_to_select})！",
                )
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
                "names": names,
                "timestamp": timestamp.isoformat(),
                "date": timestamp.strftime("%Y-%m-%d"),
                "time": timestamp.strftime("%H:%M:%S"),
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
            names_str = ", ".join(record["names"])
            text += f"[{record['date']} {record['time']}] {names_str}\n"

        self.history_text.setPlainText(text)

    def reset_students(self):
        """重置学生名单"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空当前学生名单吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.students = []
            self.update_students_list()
            self.data_storage.set_current_students(self.students)  # Use the new method
            self.data_storage.save_classes()  # Save all class data

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
            names_str = ", ".join(record["names"])
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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
            for name in record["names"]:
                name_counts[name] = name_counts.get(name, 0) + 1

        # 按次数排序
        sorted_counts = sorted(name_counts.items(), key=lambda x: x[1], reverse=True)

        # 统计信息
        total_calls = len(self.history)
        today_calls = 0
        today = datetime.now().strftime("%Y-%m-%d")
        for record in self.history:
            if record["date"] == today:
                today_calls += 1

        # 生成统计文本
        stats_text = "统计信息:\n\n"
        stats_text += f"今日点名次数: {today_calls}\n"
        stats_text += f"总点名次数: {total_calls}\n\n"
        stats_text += "各学生被点名次数排名:\n"

        for i, (name, count) in enumerate(sorted_counts[:10], 1):
            stats_text += f"{i}. {name}: {count}次\n"

        if len(sorted_counts) > 10:
            stats_text += f"\n... 还有{len(sorted_counts) - 10}个学生"

        QMessageBox.information(self, "统计信息", stats_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("随机点名系统")
    # app.setWindowIcon(QIcon("icon.png"))  # 可以设置图标，如果有的话

    window = RandomRollCallApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
