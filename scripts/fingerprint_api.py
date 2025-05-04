from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from os import urandom
import requests
import base64
import json

# 키 생성 함수
def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password)

# 암호화 함수
def encrypt(data, key):
    iv = urandom(16)  # 초기화 벡터 생성
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return iv + encrypted_data  # IV와 암호화된 데이터를 함께 반환

# 복호화 함수
def decrypt(encrypted_data, key):
    iv = encrypted_data[:16]  # IV 추출
    encrypted_data = encrypted_data[16:]  # 실제 암호화된 데이터
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()

# 상수 정의
SERVER_URL = "http://210.101.236.158:8081/api"
headers = {
    'Content-Type': 'application/json'
}

# 더미 데이터
DUMMY_BYTE_DATA1 = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
DUMMY_BYTE_DATA2 = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'

def check_student(student_number):
    """가입 가능한 학번인지 체크"""
    try:
        res = requests.get(f"{SERVER_URL}/fingerprint/students/{student_number}")
        print(f"응답: {res.status_code}")
        print(res.json() if res.status_code == 200 else "응답 없음")
    except Exception as e:
        print(f"학번 체크 중 오류 발생: {e}")

def register_fingerprint(student_number):
    """학번 및 지문 데이터 등록"""
    try:
        data = {
            "fingerprint1": base64.b64encode(DUMMY_BYTE_DATA1).decode("utf-8"),
            "fingerprint2": base64.b64encode(DUMMY_BYTE_DATA2).decode("utf-8"),
            "std_num": student_number
        }
        res = requests.post(f"{SERVER_URL}/fingerprint/students", data=json.dumps(data), headers=headers)
        print(f"응답: {res.status_code}")
        print(res.json() if res.status_code == 200 else "응답 없음")
    except Exception as e:
        print(f"지문 등록 중 오류 발생: {e}")

def send_log(student_number, action):
    """로그 전송"""
    try:
        data = {
            "std_num": student_number,
            "action": action
        }
        res = requests.post(f"{SERVER_URL}/fingerprint/logs", data=json.dumps(data), headers=headers)
        print(f"응답: {res.status_code}")
        print(res.json() if res.status_code == 200 else "응답 없음")
    except Exception as e:
        print(f"로그 전송 중 오류 발생: {e}")

def get_all_fingerprints():
    """전체 지문 데이터 조회"""
    try:
        res = requests.get(f"{SERVER_URL}/fingerprint/students")
        if res.status_code == 200:
            jsonData = res.json()
            dataList = jsonData["data"]
            print(f"총 {len(dataList)}개의 지문 데이터가 있습니다.")
            for data in dataList:
                print(f"학번: {data['studentNumber']}")
                print(base64.b64decode(data["fingerPrintImage1"].encode("utf-8")))
        else:
            print("데이터 조회 실패")
    except Exception as e:
        print(f"지문 데이터 조회 중 오류 발생: {e}")

def print_menu():
    """메뉴 출력"""
    print("\n=== 지문 인식 시스템 API 테스트 ===")
    print("1. 학번 체크")
    print("2. 지문 등록")
    print("3. 로그 전송")
    print("4. 전체 지문 데이터 조회")
    print("5. 종료")

def main():
    while True:
        print_menu()
        try:
            select = int(input("\n요청할 번호를 입력하세요: "))
            
            if select == 1:
                student_number = input("체크할 학번을 입력하세요: ")
                check_student(student_number)
                
            elif select == 2:
                student_number = input("등록할 학번을 입력하세요: ")
                register_fingerprint(student_number)
                
            elif select == 3:
                student_number = input("학번을 입력하세요: ")
                action = input("행동을 입력하세요 (등교/하교/식사/도서관/기타/복귀): ")
                send_log(student_number, action)
                
            elif select == 4:
                get_all_fingerprints()
                
            elif select == 5:
                print("프로그램을 종료합니다.")
                break
                
            else:
                print("잘못된 번호를 입력했습니다.")
                
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
