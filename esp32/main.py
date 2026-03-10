import network
import urequests
import ubinascii
import time
import usocket as socket
import gc
from machine import Pin
import time
import neopixel

# ===================== WS2812 =====================
pin = Pin(48, Pin.OUT)
num_leds = 1
np = neopixel.NeoPixel(pin, num_leds)

def green_flash():
        # 绿色
    np[0] = (0, 255, 0)
    np.write()
    time.sleep(0.1)
    off_ws2812()
    time.sleep(0.05)
    np[0] = (0, 255, 0)
    np.write()
    time.sleep(0.1)
    off_ws2812()

def red():
    np[0] = (255, 0, 0)
    np.write()
    time.sleep(0.5)
    off_ws2812()

def off_ws2812():
    np[0] = (0, 0, 0)
    np.write()

# ===================== 服务器配置 =====================
SERVER_IP = "148.135.15.123"
SERVER_PORT = 5000

# ===================== WiFi =====================
WIFI_SSID = "7033"
WIFI_PASSWORD = "cc753852951"

# ===================== WOL配置 =====================
TARGET_MAC = "1C:69:7A:F4:40:B5"
BROADCAST_IP = "192.168.101.255"
WOL_PORT = 9


# ===================== 发送WOL =====================
def send_wol(mac_str):

    mac_bytes = ubinascii.unhexlify(mac_str.replace(':', '').replace('-', ''))

    magic_packet = b'\xFF' * 6 + mac_bytes * 16

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        s.sendto(magic_packet, (BROADCAST_IP, WOL_PORT))
        print("WoL 包已发送:", mac_str)
    except Exception as e:
        print("WoL 发送失败:", e)

    s.close()


# ===================== 获取ESP MAC =====================
def get_mac_address():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    mac_raw = wlan.config('mac')

    mac_str = ubinascii.hexlify(mac_raw, ':').decode().upper()

    return mac_str


# ===================== 连接WiFi =====================
def connect_wifi():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():

        print("正在连接WiFi...")

        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        while not wlan.isconnected():
            time.sleep(1)

    print("WiFi已连接:", wlan.ifconfig())


# ===================== 检查WiFi =====================
def check_wifi():

    wlan = network.WLAN(network.STA_IF)

    if not wlan.isconnected():

        print("WiFi断开，重新连接...")

        connect_wifi()


# ===================== 请求服务器 =====================
def verify_device():

    mac = get_mac_address()

    url = "http://{}:{}/get?mac={}&description={}--requested".format(
        SERVER_IP,
        SERVER_PORT,
        TARGET_MAC,
        mac
    )

    print("请求:", url)

    response = None

    try:

        response = urequests.get(url, timeout=3)

        result = response.text.strip()

        print("服务器返回:", result)

        if result == "yes":
            print("服务器允许唤醒")
            send_wol(TARGET_MAC)
            green_flash()

        elif result == "no":
            print("服务器拒绝")

        else:
            print("未知响应:", result)

    except Exception as e:
        red()
        print("HTTP请求失败:", e)

    finally:

        if response:
            try:
                response.close()
            except:
                pass

        gc.collect()

        print("剩余内存:", gc.mem_free())


# ===================== 主程序 =====================
connect_wifi()

while True:

    check_wifi()

    verify_device()

    time.sleep(1)
