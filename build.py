"""
打包脚本 - 将随机点名软件打包为独立可执行文件
支持多平台打包
"""
import os
import sys
import platform
from pathlib import Path

def create_spec_file():
    """创建PyInstaller spec文件"""
    # 根据操作系统设置一些特定选项
    system = platform.system().lower()

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('template.xlsx', '.'),
        ('docs', 'docs'),
        ('data', 'data'),
    ],
    hiddenimports=['excel_importer', 'pandas', 'numpy', 'openpyxl'],
    hookspath=[],
    hooksconfig={{}},
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
    argv_emulation=False,  # 仅适用于macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标路径
)
'''

    with open('random_roll_call.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"Spec文件已创建: random_roll_call.spec")
    print(f"当前系统: {platform.system()} {platform.machine()}")


def explain_cross_platform_options():
    """解释跨平台打包选项"""
    print("\n跨平台打包说明:")
    print("=" * 50)
    print("1. 最可靠的方法是在目标系统上打包:")
    print("   - Windows exe: 在Windows系统上运行打包命令")
    print("   - macOS app: 在macOS系统上运行打包命令")
    print("   - Linux binary: 在Linux系统上运行打包命令")
    print()
    print("2. 使用虚拟机或远程服务:")
    print("   - 可以使用虚拟机安装目标操作系统")
    print("   - 或使用CI/CD服务如GitHub Actions进行多平台构建")
    print()
    print("3. Docker (有限支持):")
    print("   - 对GUI应用支持有限，主要适用于命令行工具")
    print()
    print("4. 打包命令:")
    print("   pyinstaller random_roll_call.spec")
    print()


def main():
    """主函数"""
    print("随机点名软件跨平台打包工具")
    print("=" * 40)
    print(f"当前系统: {platform.system()} {platform.machine()}")
    print(f"Python版本: {platform.python_version()}")

    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller")

    # 创建spec文件
    create_spec_file()
    explain_cross_platform_options()

    print("\n注意: 由于PyInstaller生成的是平台特定的可执行文件，")
    print("要在Windows上生成exe文件，需要在Windows系统上运行此工具。")

    print("\n正在创建GitHub Actions工作流文件以实现多平台CI/CD...")
    create_github_workflow()

    response = input("\n是否立即开始打包 (当前平台)？(y/n): ")
    if response.lower() == 'y':
        os.system("pyinstaller random_roll_call.spec")
        print("\n打包完成！可执行文件位于 dist/ 目录中")


def create_github_workflow():
    """创建GitHub Actions工作流文件"""
    workflow_content = '''name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            target: linux
            artifact_name: random-roll-call-linux
            asset_name: random-roll-call-linux
          - os: windows-latest
            target: windows
            artifact_name: random-roll-call-windows
            asset_name: random-roll-call-windows.exe
          - os: macos-latest
            target: macos
            artifact_name: random-roll-call-macos
            asset_name: random-roll-call-macos
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install PyInstaller
      run: pip install pyinstaller

    - name: Create spec file
      run: python build.py

    - name: Build executable
      run: |
        pyinstaller random_roll_call.spec

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.artifact_name }}
        path: dist/随机点名系统*

  release:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
    - uses: actions/download-artifact@v3

    - name: Create Release
      uses: ncipollo/release-action@v1
      with:
        artifacts: |
          random-roll-call-windows/随机点名系统.exe
          random-roll-call-macos/随机点名系统
          random-roll-call-linux/随机点名系统
        token: ${{ secrets.GITHUB_TOKEN }}
'''

    # 创建.github/workflows目录结构
    os.makedirs('.github/workflows', exist_ok=True)

    with open('.github/workflows/build.yml', 'w', encoding='utf-8') as f:
        f.write(workflow_content)

    print("GitHub Actions工作流文件已创建: .github/workflows/build.yml")


if __name__ == "__main__":
    main()