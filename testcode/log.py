from datetime import datetime
from logging import getLogger, StreamHandler, Formatter, Logger, DEBUG, INFO, WARNING, ERROR, CRITICAL
from logging.handlers import RotatingFileHandler

logger = getLogger(__name__)
logger.setLevel(DEBUG)  # 全ログデータの記録するレベル(DEBUG以上など)
logger.propagate = False

s_handler = StreamHandler()
s_handler.setLevel(DEBUG)
logger.addHandler(s_handler)  # コンソールに出力するメッセージのレベル(INFO以上など)

now_timestamp = datetime.now().strftime("%m%dT%H%M")
tsv_format = Formatter('%(asctime)s.%(msecs)d+09:00\t%(name)s\t%(filename)s\t%(lineno)d\t%(funcName)s\t%(levelname)s\t%(message)s', '%Y-%m-%dT%H:%M:%S')
f_handler = RotatingFileHandler('sc25_' + now_timestamp + '.log', maxBytes=100*1000, encoding='utf-8')  # 最大で100kBまで記録
f_handler.setLevel(DEBUG)  # ファイルに記録するメッセージのレベル(INFO以上など)
f_handler.setFormatter(tsv_format)
logger.addHandler(f_handler)

if __name__ == "__main__":
    logger.debug("これはデバッグ時専用のメッセージです")
    logger.info("これはINFOです")
    logger.warning("これは警告です")
    logger.error("これはエラーメッセージです")
    logger.critical("これは致命的なエラーメッセージです")

# from log import logger  でloggerを読み込んで
# logger.info("aiu")      のように記録してください