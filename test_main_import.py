"""
测试主应用程序导入
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.main import RandomRollCallApp
    print("成功导入 RandomRollCallApp")
    
    from src.excel_importer import ExcelImporter
    print("成功导入 ExcelImporter")
    
    import PyQt6
    print(f"成功导入 PyQt6: {PyQt6.__version__ if hasattr(PyQt6, '__version__') else 'Unknown'}")
    
    import pandas
    print(f"成功导入 pandas: {pandas.__version__}")
    
    import openpyxl
    print(f"成功导入 openpyxl: {openpyxl.__version__}")
    
    print("所有依赖导入成功！")
    
except ImportError as e:
    print(f"导入失败: {e}")
    import traceback
    traceback.print_exc()