import os
import sys
import time
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pyfingerprint.pyfingerprint import PyFingerprint
from Fingerprint_api import get_all_fingerprint_data, register_fingerprint_api, close_door_api, log_status_api
from PyQt5.QtCore import QThread, pyqtSignal
from dotenv import load_dotenv

load_dotenv()

MATCH_THRESHOLD = 50

class FingerprintManager(QThread):
    message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.PASSWORD = None
        self.STUDENT_LIST = []
        
        try :
            password = os.getenv("FP_PASSWORD")
            if password is None:
                raise ValueError("FP_PASSWORD 환경 변수가 설정되지 않았습니다.")
            self.PASSWORD = password.encode("utf-8")
        except Exception as e:
            print(e)
            sys.exit(1)
        
        try:
            self.sensor = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)
            print("지문 인식기 연결 성공")
        except Exception as e:
            print("지문 인식기 초기화 실패:", e)
            self.message.emit(str(e))
        
        self.get_finger_list()

    def generate_key(self, password, salt) :
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password)

    def encrypt(self, data, key) :
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return iv + encryptor.update(data) + encryptor.finalize()

    def decrypt(self, encrypted_data, key):
        iv = encrypted_data[:16]
        data = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(data) + decryptor.finalize()

    def decode_and_decrypt(self, encoded_data_b64, key):
        encrypted_data = base64.b64decode(encoded_data_b64.encode("utf-8"))
        return self.decrypt(encrypted_data, key)

    def encode_and_encrypt(self, buffer_id, key):
        fingerprint_data = bytes(self.sensor.downloadCharacteristics(buffer_id))
        encrypted = self.encrypt(fingerprint_data, key)
        return base64.b64encode(encrypted).decode()

    
    # 서버로부터 지문 데이터 받아오기
    def get_finger_list(self):
        # self.sensor.clearDatabase()
        self.STUDENT_LIST.clear()
        data_list = get_all_fingerprint_data()

        for data in data_list:
            salt = base64.b64decode(data["salt"])
            key = self.generate_key(self.PASSWORD, salt)

            fp_data1 = self.decode_and_decrypt(data["fingerPrintImage1"], key)
            fp_data2 = self.decode_and_decrypt(data["fingerPrintImage2"], key)

            self.sensor.uploadCharacteristics(0x01, fp_data1)
            self.sensor.uploadCharacteristics(0x02, fp_data2)
            self.create_and_store_template(data["studentNumber"])

    # 버퍼에 저장된 지문 데이터 저장
    def create_and_store_template(self, student_number: str):
        self.sensor.createTemplate()
        self.sensor.storeTemplate()
        self.STUDENT_LIST.append(student_number)

    # 지문 등록
    def register_fingerprint(self, student_id):
        self.message.emit("첫 번째 지문을 스캔해주세요.")
        start_time = time.time()
        while time.time() - start_time < 5:
            if self.sensor.readImage():
                self.sensor.convertImage(0x01)
                break
        
        self.message.emit("두 번째 지문을 스캔해주세요.")
        start_time = time.time()
        while time.time() - start_time < 5:
            if self.sensor.readImage():
                self.sensor.convertImage(0x02)
                break

        if self.sensor.compareCharacteristics() == 0:
            self.message.emit("등록한 지문이 일치하지 않습니다.")
            return None

        salt = os.urandom(16)
        key = self.generate_key(self.PASSWORD, salt)

        fp_data1 = self.encode_and_encrypt(0x01, key)
        fp_data2 = self.encode_and_encrypt(0x02, key)
        salt_b64 = base64.b64encode(salt).decode("utf-8")

        self.sensor.createTemplate()
        self.sensor.storeTemplate()

        if register_fingerprint_api(student_id, fp_data1, fp_data2, salt):
            self.create_and_store_template(student_id)
   
    def verify_fingerprint(self, current_status):
        """지문 검증 처리"""
        if self.sensor.readImage() != False:
            self.sensor.convertImage(0x01)
            result = self.sensor.searchTemplate()
			
            if result[0] >= 0 and result[1] >= MATCH_THRESHOLD:
				# 일치하는 지문을 찾았을 때
                student_id = self.STUDENT_LIST[result[0]]

                if current_status == "문닫기":
					# 문 닫기 API 호출
                    close_door_api(student_id)
                    return
				
				# 로그 API 호출
                log_status_api(student_id, current_status)

if __name__ == "__main__":
    manager = FingerprintManager()
    if manager.sensor:
        manager.register_fingerprint()
