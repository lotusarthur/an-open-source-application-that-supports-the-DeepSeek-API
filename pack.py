import PyInstaller.__main__
import os

# 指定主入口文件（通常是应用程序的启动脚本）
main_script = 'start_ui.py'  # 请确认这是您的主入口文件

PyInstaller.__main__.run([
    main_script,
    '--name=DeepSeekChat',
    '--windowed',
    '--onefile',
    # 添加额外的数据文件（如JSON配置文件）
    '--add-data=ai_personas.json;.',  # Windows使用分号分隔
    '--add-data=api_config.json;.',   # 如果是Linux/Mac，使用冒号: instead of ;
])