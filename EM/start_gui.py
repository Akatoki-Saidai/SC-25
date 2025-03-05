import http.server
import json
from logging import getLogger, StreamHandler
import os
import socket
import socketserver
import subprocess
import time

# ローカルIPを取得
local_ip = ""

# ラズパイ以外
# local_ip = socket.gethostbyname_ex(socket.gethostname())[2][-1]

#ラズパイ
str_out_lines = subprocess.Popen("ip addr", stdout=subprocess.PIPE, shell=True).communicate()[0].decode("ascii", "ignore").splitlines()
for line in str_out_lines:
    if line.startswith("    inet "):
        local_ip = line.split()[1]
        local_ip = (local_ip[0:-3] if local_ip[-3] == '/' else local_ip[0:-2])

HOST, PORT = '', 8000

# 一度削除
try:
    os.remove('./data_from_browser.json')
    os.remove('./data_to_browser.json')
except Exception as e:
    pass

try:
    # 受信用のJSONファイルを作成
    with open("./data_from_browser.json", "w") as f:
        f.write('{"nanimonai": true}')

    # 送信用のJSONファイルを作成
    with open("./data_to_browser.json", "w") as f:
        f.write('{"motor_l": 0, "motor_r": 0, "light": false, "buzzer": false, "lat": null, "lon": null, "grav": [null, null, null], "mag": [null, null, null], "phase": null, "pressure: 0", "altitude: 0", "local_ip": "' + f'{local_ip}:{PORT}' + '"}')
except Exception as e:
    print(f'<<エラー>>\nGUI送信ファイルへの書き込みに失敗しました: {e}')
# 書き込み権限を設定
subprocess.run('chmod 664 data_from_browser.json', shell=True)
subprocess.run('chmod 664 data_to_browser.json', shell=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        file_length = int(self.headers['Content-Length'])
        with open("./data_from_browser.json", 'w') as f:
            f.write(self.rfile.read(file_length).decode('utf-8'))
        self.send_response(201, 'Created')
        self.end_headers()
        with open("./data_to_browser.json", "r") as f:
            self.wfile.write(f.read().encode('utf-8'))

def start_server(*, logger=None):
    if logger is None:
        logger = logger or getLogger(__name__)
        logger.addHandler(StreamHandler())
        logger.setLevel(10)
    while True:
        try:
            with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
                logger.info(f"サーバーが稼働しました！  同じネットワーク内のブラウザで http://{local_ip}:{PORT} にアクセスしてください")
                httpd.serve_forever()
        except Exception as e:
            logger.exception(f'<<エラー>>\nGUI用のサーバーでエラーが発生しました')


def write_to_gui(devices, data, logger=None):
    try:
        # もしloggerが渡されなかったら，ログの記録先を標準出力に設定
        if _logger is None:
            _logger = getLogger(__name__)
            _logger.addHandler(StreamHandler())
            _logger.setLevel(10)
        _logger = logger

        data_to_browser = {}
        with open('data_to_browser.json', 'r') as f:
            data_to_browser = json.load(f)

        with open('data_to_browser.json', 'w') as f:
            right_pin1duty, right_pin2duty, left_pin1duty, left_pin2duty = devices["motor"].getPWMduty()
            
            if right_pin1duty > right_pin2duty:
                motor_r = right_pin1duty
            elif right_pin1duty < right_pin2duty:
                motor_r = -1 * right_pin2duty
            else:
                motor_r = 0

            if left_pin1duty > left_pin2duty:
                motor_l = left_pin1duty
            elif left_pin1duty < left_pin2duty:
                motor_l = -1 * left_pin2duty
            else:
                motor_l = 0

            data_to_browser['motor_r'] = motor_r
            data_to_browser['motor_l'] = motor_l
            data_to_browser['phase'] = data["phase"]
            data_to_browser['lat'] = data["lat"]
            data_to_browser['lon'] = data["lon"]
            data_to_browser['mag'] = data["mag"]
            data_to_browser['grav'] = data["grav"]
            data_to_browser['pressure'] = data["press"]
            data_to_browser['altitude'] = data["alt"]

            f.write(json.dumps(data_to_browser))
            
            time.sleep(0.1)

    except Exception as e:
        _logger.exception("An error occured in update gui")
        

if __name__ == '__main__':
    start_server()


# 参考にしたサイト
## https://stackoverflow.com/questions/66514500/how-do-i-configure-a-python-server-for-post