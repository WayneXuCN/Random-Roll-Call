"""
测试Excel导入功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.excel_importer import ExcelImporter

def test_excel_import():
    """测试Excel导入功能"""
    try:
        # 检查模板文件是否存在
        if not os.path.exists('template.xlsx'):
            print("模板文件不存在，创建测试模板...")
            import pandas as pd
            data = {
                '姓名': ['张三', '李四', '王五', '赵六', '钱七']
            }
            df = pd.DataFrame(data)
            df.to_excel('template.xlsx', index=False)
            print("模板文件已创建: template.xlsx")
        
        # 导入Excel文件
        students = ExcelImporter.import_from_excel('template.xlsx')
        print(f"成功导入 {len(students)} 个学生姓名:")
        for i, student in enumerate(students, 1):
            print(f"{i}. {student}")
        
        # 验证数据
        validation_result = ExcelImporter.validate_data(students)
        print(f"\n数据验证结果: {validation_result}")
        
    except Exception as e:
        print(f"导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_import()