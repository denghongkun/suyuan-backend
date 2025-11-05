# test_network.py
import socket
import subprocess
import sys

def test_network_connectivity():
    """测试网络连通性"""
    print("🌐 网络连通性测试...")
    
    # 您的数据库主机和端口（替换为实际值）
    host = "gz-cdb-rejbzo23.sql.tencentcdb.com"
    port = 63982  # 替换为您的实际外网端口
    
    print(f"目标: {host}:{port}")
    
    # 方法1: 使用socket测试
    print("1. Socket连接测试...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5秒超时
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ Socket连接成功")
        else:
            print(f"❌ Socket连接失败，错误码: {result}")
            print("可能的原因：")
            print("  - 防火墙阻止")
            print("  - 网络路由问题")
            print("  - 目标服务未运行")
    except Exception as e:
        print(f"❌ Socket测试异常: {e}")
    
    # 方法2: 使用telnet测试（如果系统支持）
    print("\n2. Telnet测试...")
    try:
        result = subprocess.run(
            ["telnet", host, str(port)], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if "Connected" in result.stdout:
            print("✅ Telnet连接成功")
        else:
            print("❌ Telnet连接失败")
    except Exception as e:
        print(f"❌ Telnet测试异常: {e}")
        print("(这可能是因为telnet客户端未安装)")

def check_firewall():
    """检查防火墙设置"""
    print("\n🔥 防火墙检查...")
    try:
        # 检查Windows防火墙状态
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles", "state"],
            capture_output=True, 
            text=True
        )
        print("Windows防火墙状态:")
        print(result.stdout)
    except Exception as e:
        print(f"防火墙检查失败: {e}")

if __name__ == "__main__":
    test_network_connectivity()
    check_firewall()