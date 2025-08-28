import requests
import os
import sys
from PyQt5.QtCore import QObject, pyqtSignal
from Fingerprint_status import Status

# 테스트용 전역 변수 (실사용 시 환경 변수에 저장)
SERVER_URL = "http://210.101.236.158:8081/api/fingerprint"
SERVER_KEY = "dev"

# 메세지 화면에 출력하는 용도 클래스
class APImessage(QObject) :
    message = pyqtSignal(str)

api_message = APImessage()


def init_api() :
    # 환경 변수 초기화
    global SERVER_URL
    global SERVER_KEY

    try :
        SERVER_URL = os.getenv("FP_URL")
        SERVER_KEY = os.getenv("FP_KEY")

        if SERVER_URL is None :
            raise ValueError("FP_URL 환경 변수 설정되지 않음.")
        if SERVER_KEY is None :
            raise ValueError("FP_KEY 환경 변수 설정되지 않음.")
    except Exception as e :
        print(e)
        sys.exit(1)


def get_all_fingerprint_api() :
    # 서버에 있는 지문 데이터 가져오는 API
    try :
        responce = requests.get(f"{SERVER_URL}/students")

        # 서버 요청 성공 시 학번, 지문 데이터, salt 정보 리턴 실패 시 빈 리스트 리턴
        if api_success_check_api(responce) :
            return responce.json()["data"]
        else :
            return []
    except requests.exceptions as e :
        api_message.message.emit(f"요청 과정 중 오류 발생\n{str(e)}")
        return []
    except Exception as e :
        api_message.message.emit(f"지문 정보 조회 중 오류 발생\n{str(e)}")
        return []
    
def check_student_registration(student_id) :
    # 가입 가능한 학번인지 검증
    print("체크 스튜던트 레지스트리")
    try :
        responce = requests.get(f"{SERVER_URL}/students/{student_id}")

        print(responce.json())
        return api_success_check_api(responce)
    except Exception as e :
        api_message.message.emit(f"학번 검증 중 오류 발생\n{str(e)}")
        return False

def register_fingerprint_api(fp_data1, fp_data2, std_num, salt) :
    # 지문 등록 api 호출
    try :
        data_json = {
            "fingerprint1" : fp_data1,
            "fingerprint2" : fp_data2,
            "std_num" : std_num,
            "salt" : salt
        }

        responce = requests.post(f"{SERVER_URL}/students", data=data_json)

        return api_success_check_api(responce)
    except Exception as e :
        api_message.message.emit(f"지문 등록 중 오류 발생\n{str(e)}")
        return False

def log_status(std_num, status) :
    try :
        data_json = {
            "std_num" : std_num,
            "action" : status.value
        }
        
        responce = requests.post(f"{SERVER_URL}/logs", data_json)

        return api_success_check_api(responce)
    
    except Exception as e :
        api_message.message.emit(f"로그 기록 중 오류 발생\n{str(e)}")
        return False

def close_door(std_num) :
    # 문 닫기 API
    try :
        data_json = {
            "closingMember" : std_num
        }

        responce = requests.post(f"{SERVER_URL}/close", data_json)

        return api_success_check_api(responce)
    except Exception as e :
        api_message.message.emit(f"문 닫기 중 오류 발생\n{str(e)}")
        return False
    
def api_success_check_api(responce) :
    # API 요청이 성공인지 실패인지 결과를 반환하는 함수
    try :
        # responce의 결과값이 딕셔너리 형태로 대입됨
        responce_data = responce.json()

        print(responce_data["success"])
        print(type(responce_data["success"]))
        # 서버에 요청 성공 시
        if responce.status_code == 200 or responce.status_code == 400 :
            api_message.message.emit(responce_data["message"])
            return responce_data["success"]
        elif responce.status_code == 404 :
            api_message.message.emit("404, 엔드포인트를 찾을 수 없습니다.")
            return False
    except KeyError as e :
        api_message.message.emit("응답 형식이 올바르지 않습니다.")
        return False
    except Exception as e :
        api_message.message.emit(f"오류 발생\n{str(e)}")
        return False