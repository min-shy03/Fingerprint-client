from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
from PyQt5.QtCore import QThread, pyqtSignal
import os
import sys
from Fingerprint_api import get_all_fingerprint_api

class FingerprintSensor(QThread) :
    message = pyqtSignal(str)

    # 센서 및 모듈 초기화
    def __init__(self):
        super().__init__()
        self.running = True
        # 암호화, 복호화용 패스워드 
        self.PASSWORD = None
        # 학번 저장용 리스트
        self.STUDENT_LIST = []

        from pyfingerprint.pyfingerprint import PyFingerprint

        # 환경 변수 초기화 (라즈베리파이 내에 환경변수로 비밀번호 설정)
        password = os.getenv("FP_PASSWORD")

        # 환경 변수에서 아무 값도 오지 않았다면
        if password is None :
            # 에러를 강제로 발생시키는 코드
            raise ValueError("FP_PASSWORD 환경 변수 설정되지 않음.")
        
        # 문자열을 바이트로 변환 (인코딩) 후 변수에 담기
        self.PASSWORD = password.encode("utf-8")

        try :
            self.sensor = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)
            print("지문 인식기 연결 성공")
        except Exception as e :
            print("지문 인식기 연결 실패 :", e)
            # 코드가 비정상적으로 끝났음을 알려주는 1 표시
            sys.exit(1)

    def register_fingerprint(self) :
        # 지문 등록 함수
        self.message.emit("테스트")

    
    def generate_key(self, password, salt):
        # 암호화 전용 키 생성 함수
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
		)
        return kdf.derive(password)
    
    def encrypt(self, data, key) :
        # 암호화 함수
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return iv + encrypted_data
    
    def decrypt(self, encrypted_data, key):
        # 복호화 함수
        iv = encrypted_data[:16]  # IV 추출
        encrypted_data = encrypted_data[16:]  # 실제 암호화된 데이터
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()
    
    def encode_and_encrypt(self, charBufferId, key):
		# 지문 데이터 암호화 및 인코딩 함수
        # 현재 각 버퍼에 있는 지문 데이터를 바이트화
        fingerprint_data = bytes(self.sensor.downloadCharacteristics(charBufferId))
        encrypted_data = self.encrypt(fingerprint_data, key)
        encoded_data = base64.b64encode(encrypted_data)
        return encoded_data
    
    def decode_and_decrypt(self, encoded_data, salt_b64) :
        # 서버에서 받아온 데이터 복호화 및 디코딩 함수
        raw_data = base64.b64decode(encoded_data.encode("utf-8"))
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        # 지정 된 salt 값으로 암호화 시 만든 키 그대로 재생성 후 복호화에 사용
        key = self.generate_key(self.PASSWORD, salt)
        decrypted = self.decrypt(raw_data, key)
        return list(decrypted)
   
    def get_fingerprint_list(self) :
        # 서버 내에서 지문 데이터 가져오는 함수

        # 센서 내의 메모리 초기화
        self.sensor.clearDatabase()
        # 학번 담을 리스트 초기화
        self.STUDENT_LIST.clear()

        # 센서 내의 메모리와 학번 리스트를 초기화 함으로써 같은 인덱스 위치에 각각 지문 데이터와 학번을 저장한다.
        # ex) 0번 인덱스 조회시 같은 학생의 지문과 학번이 나옴

        # api 호출 데이터 리스트에는 각 학생의 암호화 된 지문 데이터, 학번, salt 값이 딕셔너리 형태로 저장됨
        data_list = get_all_fingerprint_api()

        # data에 각각의 학생 정보가 담긴 딕셔너리가 나옴
        for data in data_list :
            # 암호화 된 지문 데이터 복호화 
            fp_data1 = self.decode_and_decrypt(data["fingerPrintImage1"], data["salt"])
            fp_data2 = self.decode_and_decrypt(data["fingerPrintImage2"], data["salt"])

            # 각각의 범퍼에 지문 데이터 올리기
            self.sensor.uploadCharacteristics(0x01,fp_data1)
            self.sensor.uploadCharacteristics(0x02,fp_data2)

            self.create_and_store_template(data["studentNumber"])

    def create_and_store_template(self, std_num) :
        # 현재 버퍼에 저장된 지문 데이터 템플릿으로 생성 후 메모리에 저장, 센서 메모리와 동일한 인덱스에 학번 리스트에 학번 저장
        self.sensor.createTemplate()
        self.sensor.storeTemplate()
        self.STUDENT_LIST.append(std_num)