"""
Excel导入器模块，负责处理Excel文件的导入和解析
"""
import pandas as pd
from typing import List
import os


class ExcelImporter:
    """Excel导入器"""
    
    @staticmethod
    def import_from_excel(file_path: str) -> List[str]:
        """从Excel文件导入学生姓名"""
        try:
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