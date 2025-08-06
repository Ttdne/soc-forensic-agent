import importlib
import os
from pathlib import Path

def load_toolkit_plugins():
    plugins_path = Path(__file__).parent / "plugins"
    plugins = {}

    for plugin_dir in plugins_path.iterdir():
        if plugin_dir.is_dir():
            logic_path = plugin_dir / "logic.py"
            if logic_path.exists():
                module_name = f"toolkits.plugins.{plugin_dir.name}.logic"
                module = importlib.import_module(module_name)
                plugins[plugin_dir.name] = module

    return plugins
