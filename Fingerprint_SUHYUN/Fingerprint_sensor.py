from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from PyQt5.QtCore import QThread, pyqtSignal
import os
import sys
from Fingerprint_api import get_all_fingerprint

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

    # def register_fingerprint(self) :

    
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
   
    def get_fingerprint_list(self) :
        # 서버 내에서 지문 데이터 가져오는 함수

        # 센서 내의 메모리 초기화
        self.sensor.clearDatabase()
        # 학번 담을 리스트 초기화
        self.STUDENT_LIST.clear()

        # 센서 내의 메모리와 학번 리스트를 초기화 함으로써 같은 인덱스 위치에 각각 지문 데이터와 학번을 저장한다.
        # ex) 0번 인덱스 조회시 같은 학생의 지문과 학번이 나옴

        # api 호출 데이터 리스트에는 각 학생의 암호화 된 지문 데이터, 학번, salt 값이 딕셔너리 형태로 저장됨
        data_list = get_all_fingerprint()

        # data에 각각의 학생 정보가 담긴 딕셔너리가 나옴
        for data in data_list :
            # 암호화 된 지문 데이터 복호화 
            fp_data1 = 


        

    