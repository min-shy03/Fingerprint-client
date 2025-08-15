from PyQt5.QtCore import QThread, pyqtSignal
import os
import sys

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