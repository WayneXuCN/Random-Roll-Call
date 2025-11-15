"""
打包脚本 - 将随机点名软件打包为独立可执行文件
"""
import os
import sys
from pathlib import Path

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('template.xlsx', '.'),
        ('docs', 'docs'),
    ],
    hiddenimports=['excel_importer', 'pandas', 'numpy', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='随机点名系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标路径
)
'''
    
    with open('random_roll_call.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Spec文件已创建: random_roll_call.spec")

def main():
    """主函数"""
    print("随机点名软件打包工具")
    print("=" * 30)
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller")
    
    # 创建spec文件
    create_spec_file()
    
    print("\n打包命令已准备就绪")
    print("运行以下命令进行打包:")
    print("pyinstaller random_roll_call.spec")
    
    response = input("\n是否立即开始打包？(y/n): ")
    if response.lower() == 'y':
        os.system("pyinstaller random_roll_call.spec")
        print("\n打包完成！可执行文件位于 dist/ 目录中")

if __name__ == "__main__":
    main()