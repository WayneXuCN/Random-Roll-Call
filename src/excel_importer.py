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
    def validate_data(names: List[str], existing_names: List[str] = None) -> dict:
        """验证导入的数据"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'count': len(names),
            'duplicates': [],
            'duplicates_list': []  # 更详细的信息
        }

        # 检查内部重复
        seen = set()
        duplicates = []
        duplicate_indices = {}

        for i, name in enumerate(names):
            if name in seen and name not in duplicates:
                duplicates.append(name)
                # 记录每个重复姓名的所有位置
                duplicate_indices[name] = [j for j, n in enumerate(names) if n == name]
            seen.add(name)

        result['duplicates'] = duplicates
        if duplicates:
            result['warnings'].append(f"导入列表内部发现 {len(duplicates)} 个重复姓名: {', '.join(duplicates[:5])}{'...' if len(duplicates) > 5 else ''}")

        # 记录详细的重复信息
        result['duplicates_list'] = duplicate_indices

        # 检查与现有名单的重复（如果提供现有名单）
        if existing_names:
            existing_set = set(existing_names)
            external_duplicates = [name for name in set(names) if name in existing_set]
            if external_duplicates:
                result['warnings'].append(f"与现有名单重复 {len(external_duplicates)} 个姓名: {', '.join(external_duplicates[:5])}{'...' if len(external_duplicates) > 5 else ''}")

        # 检查姓名长度和内容
        for i, name in enumerate(names):
            if len(name) > 50:
                result['warnings'].append(f"第 {i+1} 行姓名过长 (长度: {len(name)}): {name[:20]}...")
            elif len(name.strip()) == 0:
                result['errors'].append(f"第 {i+1} 行姓名为空")
            elif not any(c.isalpha() for c in name):
                # 检查是否包含至少一个字母（中文也是字母）
                result['warnings'].append(f"第 {i+1} 行姓名可能无效: {name}")

        # 检查特殊字符（可以根据需要调整）
        import re
        invalid_pattern = re.compile(r'[!@#$%^&*()+=\[\]{}|\\:";\'<>?,./]')
        for i, name in enumerate(names):
            if invalid_pattern.search(name):
                result['errors'].append(f"第 {i+1} 行姓名包含无效字符: {name}")

        # 检查总体数量
        if len(names) > 1000:
            result['warnings'].append(f"导入的学生数量过多 ({len(names)}个)，可能会影响性能")

        if result['errors']:
            result['valid'] = False

        return result