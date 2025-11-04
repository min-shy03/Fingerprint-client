import sys
from PyQt5.QtWidgets import QApplication
from Fingerprint_ui import FingerprintUI
from Fingerprint_sensor import FingerprintSensor
from Fingerprint_api import api_message, init_api

def main():
    app = QApplication(sys.argv)

    window = FingerprintUI()

    init_api()

    api_message.message.connect(window.on_message_received)
    
    print("api 연결 완료")
    sensor = FingerprintSensor()
    sensor.message.connect(window.on_message_received)
    print("센서 연결 완료")
    sensor.start()
    
    print("화면 연결 시작")
    window.showFullScreen()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
