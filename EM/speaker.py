# スピーカー設定をPWM出力可能にしておく(/boot/firmware/config.txtの末尾に"dtoverlay=audiomap,pins_19_18"を追加)

import subprocess
import time
import os
# import sc_logging
from logging import getLogger, StreamHandler  # ログを記録するため

# logger = sc_logging.get_logger(__name__)

class C():
    def poll(self):
        return 0  # まだ開始していない

class Speaker:
    def __init__(self, logger=None):
        # もしloggerが渡されなかったら，ログの記録先を標準出力に設定
        if logger is None:
            logger = getLogger(__name__)
            logger.addHandler(StreamHandler())
            logger.setLevel(10)
        self._logger = logger
        
        # スピーカーを演奏終了状態に設定
        self.proces_aplay = C()

    # .poll()は終了していなかったらNone，終了していたらそのステータスを返す．
    def audio_play(self, file_name):
        try:
            # logger.log('Music play')
            audio_path = f"/home/omusubi0/SC-25/Sound/{file_name}"

            if (self.proces_aplay.poll() != None and os.path.exists(audio_path)):
                # 音楽ファイルはSC-25内musicフォルダに入れておく
                # サウンドカードはaplay -lでbcm2835 Headphonesの番号を選択
                self.proces_aplay = subprocess.Popen(f"aplay --device=hw:2,0 {audio_path}", shell=True)

                self._logger.log("Play music")

            else:
                self._logger.warning("already playing music now. canceled playing.")
        except Exception as e:
                self._logger.exception("An error occured in playing speaker")

if __name__ == '__main__':
    try:
        speaker = Speaker()
        speaker.audio_play("Megalovania_Trim.wav")
        time.sleep(3)

    except Exception as e:
        print(f"An error occurd in play music: {e}")


### 参考にしたサイト
# thread関連
# https://qiita.com/kaitolucifer/items/e4ace07bd8e112388c75
# コントローラーの接続
# https://hellobreak.net/raspberry-pi-ps4-controller-0326/