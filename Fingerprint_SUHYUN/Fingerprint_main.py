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

    sensor = FingerprintSensor()
    sensor.message.connect(window.on_message_received)
    sensor.start()
    
    window.showFullScreen()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()