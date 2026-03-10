# wol_sender.py （可保存为 main.py 或通过 Thonny 运行）
import network
import usocket as socket
import ubinascii
import utime
import machine

# ===================== 配置 =====================
TARGET_MAC = "1C:69:7A:F4:40:B5"  # 你的目标电脑 MAC（大写冒号分隔）
WIFI_SSID = "7033"
WIFI_PASS = "cc753852951"
BROADCAST_IP = "192.168.101.255"  # 改成你局域网的广播地址（常见 192.168.x.255）
WOL_PORT = 9  # 常用 9 或 7


# ===================== 连 WiFi =====================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("连接 WiFi...")
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            utime.sleep(1)
            timeout -= 1
        if wlan.isconnected():
            print("WiFi 已连上，IP:", wlan.ifconfig()[0])
        else:
            print("WiFi 连接失败")
            machine.reset()


# ===================== 生成并发送 WoL 包 =====================
def send_wol(mac_str):
    # 把 MAC 转成 bytes，如 b'\x1c\x69\x7a\xf4\x40\xb5'
    mac_bytes = ubinascii.unhexlify(mac_str.replace(':', '').replace('-', ''))

    # 魔法包：FF:FF:FF:FF:FF:FF + 16 次 MAC
    magic_packet = b'\xFF' * 6 + (mac_bytes * 16)

    # UDP 广播
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(magic_packet, (BROADCAST_IP, WOL_PORT))
    s.close()

    print(f"WoL 包已发送给 {mac_str}")


# ===================== 主逻辑 =====================
connect_wifi()

# 示例：立即发送一次（你可以改成 Web 服务器、按钮、定时等触发）
send_wol(TARGET_MAC)

# 保持运行或进入 Deep Sleep
# utime.sleep(60)           # 保持 60 秒在线
# machine.deepsleep()       # 或进入深度睡眠
