# スピーカー設定をPWM出力可能にしておく(/boot/firmware/config.txtの末尾に"dtoverlay=audremap,pins_18_19"を追加)

import subprocess
import time


class C():
    def poll(self):
        return 0  # まだ開始していない
proces_aplay = C()

# .poll()は終了していなかったらNone，終了していたらそのステータスを返す．
def audio_play(audio_path):
    global proces_aplay
    # print('Music play')
    if (proces_aplay.poll() != None):
        proces_aplay = subprocess.Popen(f"aplay --device=hw:1,0 {audio_path}", shell=True)

        print("Play music")

    else:
        print("already playing music now. canceled playing.")


if __name__ == '__main__':
    try:
        audio_play("/home/jaxai/Desktop/Megalovania_Trim.wav")
        time.sleep(3)

    except Exception as e:
        print(f"An error occurd in play music: {e}")


### 参考にしたサイト
# thread関連
# https://qiita.com/kaitolucifer/items/e4ace07bd8e112388c75
# コントローラーの接続
# https://hellobreak.net/raspberry-pi-ps4-controller-0326/