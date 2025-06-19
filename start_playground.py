#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Search Playground 启动器
启动一个简单的HTTP服务器来运行playground界面
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_playground(port=8080):
    """
    启动playground服务器
    
    Args:
        port: 服务器端口，默认8080
    """
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 检查playground.html是否存在
    playground_file = current_dir / "playground.html"
    if not playground_file.exists():
        print(f"❌ 错误: 找不到 playground.html 文件")
        print(f"   期望位置: {playground_file}")
        return False
    
    # 切换到项目目录
    os.chdir(current_dir)
    
    # 创建HTTP服务器
    class PlaygroundHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(current_dir), **kwargs)
        
        def end_headers(self):
            # 添加CORS头部，允许跨域请求
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_OPTIONS(self):
            # 处理预检请求
            self.send_response(200)
            self.end_headers()
        
        def log_message(self, format, *args):
            # 自定义日志格式
            print(f"🌐 {self.address_string()} - {format % args}")
    
    try:
        # 尝试启动服务器
        with socketserver.TCPServer(("", port), PlaygroundHandler) as httpd:
            server_url = f"http://localhost:{port}/playground.html"
            
            print("\n" + "="*60)
            print("🚀 Code Search Playground 已启动!")
            print("="*60)
            print(f"📍 服务器地址: {server_url}")
            print(f"🔧 项目目录: {current_dir}")
            print("\n💡 使用说明:")
            print("   1. 浏览器会自动打开playground界面")
            print("   2. 确保代码检索API服务正在运行 (http://localhost:8000)")
            print("   3. 在搜索框中输入查询，选择参数后点击搜索")
            print("   4. 按 Ctrl+C 停止服务器")
            print("\n" + "="*60)
            
            # 自动打开浏览器
            try:
                webbrowser.open(server_url)
                print("🌐 正在打开浏览器...")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print(f"   请手动访问: {server_url}")
            
            print("\n⏳ 服务器运行中... (按 Ctrl+C 停止)\n")
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {port} 已被占用")
            print(f"   请尝试使用其他端口: python start_playground.py --port 8081")
        else:
            print(f"❌ 启动服务器失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
        print("👋 感谢使用 Code Search Playground!")
        return True
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def main():
    """
    主函数，处理命令行参数
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="启动 Code Search Playground",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python start_playground.py              # 使用默认端口8080
  python start_playground.py --port 8081  # 使用端口8081
  python start_playground.py -p 9000      # 使用端口9000
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080,
        help='服务器端口 (默认: 8080)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Code Search Playground v1.0.0'
    )
    
    args = parser.parse_args()
    
    # 验证端口范围
    if not (1024 <= args.port <= 65535):
        print("❌ 端口必须在 1024-65535 范围内")
        sys.exit(1)
    
    # 启动playground
    success = start_playground(args.port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()