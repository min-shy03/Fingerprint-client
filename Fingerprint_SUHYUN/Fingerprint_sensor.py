from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from PyQt5.QtCore import QThread, pyqtSignal
from Fingerprint_api import get_all_fingerprint_api, check_student_registration, register_fingerprint_api, close_door, log_status
from Fingerprint_status import Status, get_student_id, get_status, is_sensor_active, set_status, clear_student_id
import os
import sys
import base64
import time

MATCH_THRESHOLD = 50

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

    def run(self) :
        while self.running :
            self.scan_fingerprint()

    def scan_fingerprint(self) :
        # 지문이 스캔 될 때까지 기다리는 함수

        try :
            # 센서가 비활성화 상태면 None 반환
            if not is_sensor_active() :
                return
            
            current_status = get_status()

            if current_status == Status.REGISTER :
                return self.register_fingerprint()
            else :
                return self.verify_fingerprint(current_status)
            
        except Exception as e :
            self.message.emit(f"지문 스캔 중 오류 발생\n{str(e)}")

    def register_fingerprint(self) :
        # 지문 등록 함수

        student_id = get_student_id()

        # 등록 가능한 학생인지 서버에 확인
        if not check_student_registration(student_id) :
            # 실패 시 상태를 WAITING으로 되돌리고 종료
            set_status(Status.WAITING)
            clear_student_id()
            return

        # --- 첫 번째 지문 스캔 ---
        self.message.emit("첫 번째 지문을 스캔해주세요.")
        start_time = time.time()
        finger_detected = False
        while time.time() - start_time < 5:  # 5초 제한
            if self.sensor.readImage():
                self.sensor.convertImage(0x01)
                finger_detected = True
                break
            
        if not finger_detected:
            self.message.emit("시간 초과. 등록을 취소합니다.")
            set_status(Status.WAITING) # 상태 되돌리기
            clear_student_id()
            return

        # --- 두 번째 지문 스캔 ---
        self.message.emit("두 번째 지문을 스캔해주세요.")
        start_time = time.time()
        finger_detected = False
        while time.time() - start_time < 5: # 5초 제한
            if self.sensor.readImage():
                self.sensor.convertImage(0x02)
                finger_detected = True
                break

        if not finger_detected:
            self.message.emit("시간 초과. 등록을 취소합니다.")
            set_status(Status.WAITING) # 상태 되돌리기
            clear_student_id()
            return

        # --- 지문 비교 및 서버 전송 ---
        if self.sensor.compareCharacteristics() == 0:
            self.message.emit("지문이 일치하지 않습니다.")
            set_status(Status.WAITING) # 상태 되돌리기
            clear_student_id()
            return
        
        # 테스트용 끝나면 지워도 됨
        print("지문 등록 완료")

        raw_salt = os.urandom(16)
        key = self.generate_key(self.PASSWORD, raw_salt)

        fp_data1 = self.encode_and_encrypt(0x01, key)
        fp_data2 = self.encode_and_encrypt(0x02, key)
        salt = base64.b64encode(raw_salt).decode("utf-8")

        # API 호출
        if register_fingerprint_api(fp_data1, fp_data2, student_id, salt) :
            # 테스트용 끝나면 지워도 됨
            print("지문 등록 api 호출 완료")
            self.create_and_store_template(student_id)
    
    def verify_fingerprint(self, current_status) :
        # 지문 검증 처리
        if self.sensor.readImage() != False :
            self.sensor.convertImage(0x01)
            result = self.sensor.searchTemplate()


            if result[0] >= 0 and result[1] >= MATCH_THRESHOLD :
                # 일치하는 지문 찾았을 때
                student_id = self.STUDENT_LIST[result[0]]

                if current_status == Status.CLOSE :
                    # 문 닫기 API 호출
                    close_door(student_id)
                    return
                
                log_status(student_id, current_status)

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
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
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