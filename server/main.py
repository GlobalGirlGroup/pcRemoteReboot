from flask import Flask, request, jsonify
import time
from threading import Lock

app = Flask(__name__)

# 全局存储字典
# 格式: {"mac1": {"time": 123456, "status": "active"}, ...}
devices_registry = {}
# 创建一把锁，保证多线程修改字典时的安全
registry_lock = Lock()


@app.route('/save', methods=['GET', 'POST'])
def interface_a():
    """
    接口 A：注册/保存 MAC 地址
    参数：mac
    """
    # 兼容 GET (args) 和 POST (form/json)
    mac = request.values.get('mac')

    if not mac:
        return jsonify({"error": "Missing mac address"}), 400

    with registry_lock:
        devices_registry[mac] = {
            "time": int(time.time()),
            "ip": request.remote_addr,
            "description": "pending_verification"
        }

    print(f"[A] Registered: {mac} | Current Registry: {list(devices_registry.keys())}")
    return jsonify({"status": "success", "msg": f"MAC {mac} saved"}), 200


@app.route('/get', methods=['GET'])
def interface_b():
    """
    接口 B：ESP32 访问验证
    参数：mac
    逻辑：存在则删除并返回 yes，否则返回 no
    """
    mac = request.args.get('mac')

    if not mac:
        return "no_mac_provided", 400

    with registry_lock:
        if mac in devices_registry:
            # 存在则删除该 key
            del devices_registry[mac]
            print(f"[B] Verified and Deleted: {mac}")
            return "yes", 200
        else:
            print(f"[B] Not Found: {mac}")
            return "no", 200


if __name__ == '__main__':
    # 建议关闭 debug 模式或设置 use_reloader=False 以防止代码重载导致全局变量清空
    app.run(host='0.0.0.0', port=5000)