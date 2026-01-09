# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Hermes - Crowdin i18n Management Tool.

Build command:
    uv run pyinstaller hermes.spec

Output:
    dist/hermes.exe (single executable ~25-35MB)

Note: Config file (hermes.config.json) will be created next to the .exe
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all Textual data files (CSS, default themes, etc.)
textual_datas = collect_data_files('textual')

# Collect Rich data files
rich_datas = collect_data_files('rich')

a = Analysis(
    ['src/hermes/__main__.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/hermes/tui/hermes.tcss', 'hermes/tui'),
    ] + textual_datas + rich_datas,
    hiddenimports=[
        'hermes',
        'hermes.core',
        'hermes.core.config',
        'hermes.core.crowdin_api',
        'hermes.core.crowdin_upload_api',
        'hermes.core.file_operations',
        'hermes.tui',
        'hermes.tui.app',
        'hermes.tui.screens',
        'hermes.tui.screens.main_menu',
        'hermes.tui.screens.settings',
        'hermes.tui.screens.download',
        'hermes.tui.screens.upload',
        'hermes.cli',
        'textual',
        'textual.app',
        'textual.screen',
        'textual.widgets',
        'textual.containers',
        'textual.worker',
        'textual.binding',
        'textual.validation',
        'rich',
        'rich.console',
        'rich.table',
        'rich.progress',
        'typer',
        'typer.main',
        'click',
        'google.generativeai',
        'google.ai.generativelanguage',
    ] + collect_submodules('textual') + collect_submodules('google.generativeai'),
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
    name='hermes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
