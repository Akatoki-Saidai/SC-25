# スピーカー設定をPWM出力可能にしておく(/boot/firmware/config.txtの末尾に"dtoverlay=audremap,pins_18_19"を追加)

import subprocess
import time
from log import logger


class C():
    def poll(self):
        return 0  # まだ開始していない
proces_aplay = C()

# .poll()は終了していなかったらNone，終了していたらそのステータスを返す．
def audio_play(audio_path):
    try:
        global proces_aplay
        # logger.log('Music play')
        if (proces_aplay.poll() != None):
            proces_aplay = subprocess.Popen(f"aplay --device=hw:1,0 {audio_path}", shell=True)

            logger.log("Play music")

        else:
            logger.warning("already playing music now. canceled playing.")
    except Exception as e:
            logger.exception()


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