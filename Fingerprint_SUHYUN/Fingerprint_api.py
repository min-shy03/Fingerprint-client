import requests

# 서버 주소 및 인증키 (임시값, 나중에 .env에서 불러오게 가능)
SERVER_URL = "http://210.101.236.158:8081/api/fingerprint"
SERVER_KEY = "dev"

HEADERS = {
    "Authorization": f"Bearer {SERVER_KEY}"
}

def get_all_fingerprint_data() :
    """서버에서 모든 지문 데이터를 가져옴"""
    url = f"{SERVER_URL}/students"
    
    try:
        res = requests.get(url, headers=HEADERS)
        
        if send_post(res) :
            return res.json().get("data", [])
        else:
            return []
    except requests.exceptions as e :
        print(f"요청 과정에서 오류 발생 (코드: {e})")
        return []
    except Exception as e:
        print(f"지문 정보 조회 중 오류 발생 {str(e)}")
        return []

def register_fingerprint_api(std_num, fp1, fp2, salt):
    """지문 등록 API"""
    try :
        url = f"{SERVER_URL}/students"
        data = {
            "std_num": std_num,
            "fingerprint1": fp1,
            "fingerprint2": fp2,
            "salt": salt
        }
        
        res = requests.post(url, headers=HEADERS, json=data)
        return send_post(res)
    except Exception as e :
        print(f"지문 등록 중 오류 발생 {str(e)}")
        return False

# 가입 가능한 학번인지 검증
def check_register(std_num):
    url = f"{SERVER_URL}/students/{std_num}"
    try :
        res = requests.get(url, headers=HEADERS)
        return send_post(res)
    except Exception as e :
        print(f"학번 검증 중 오류 발생 {str(e)}")
        return False

def log_status_api(std_num, action):
    """출결 로그 전송 API"""
    try :
        url = f"{SERVER_URL}/logs"
        data = {
            "std_num": std_num,
            "action": action
        }
        
        res = requests.post(url, headers=HEADERS, json=data)
        return send_post(res)
    except Exception as e :
        print(f"로그 기록 중 오류 발생 {str(e)}")
        return False


def close_door_api(std_num):
    """마지막 인원 문닫기 API"""
    try :
        url = f"{SERVER_URL}/close"
        data = {
            "closingMember": std_num
        }
        
        res = requests.post(url, headers=HEADERS, json=data)
        return send_post(res)
    except Exception as e :
        print(f"문닫기 중 오류 발생 {str(e)}")
        return False


def send_post(res) :
    """공통 POST 요청 처리 함수"""
    try:
        res_data = res.json()
        if res.status_code == 200 or res.status_code == 400 :
            print(res_data["message"])
            return res_data["success"]
        elif res.status_code == 404 :
            # 실패 시 서버 메시지 반환
            print("404, 엔드포인트를 찾을 수 없습니다.")
            return False
    except KeyError as e :
        print("응답 형식이 올바르지 않습니다.")
        return False
    
    except Exception as e:
        print(f"오류 발생 {str(e)}")
        return False
        