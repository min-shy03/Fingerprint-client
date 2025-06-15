from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pyfingerprint.pyfingerprint import PyFingerprint
import os
import base64
import time
import requests


# 🔐 암호화 키 생성 (PBKDF2)
def generate_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


# 🔐 암호화 (AES-CFB, IV 포함 반환)
def encrypt(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return iv + encrypted_data


# 🔓 복호화
def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
    iv = encrypted_data[:16]
    data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(data) + decryptor.finalize()

# 데이터 복호화
def decode_and_decrypt(encoded_data_b64: str, key: bytes) -> bytes :
    encrypted_data = base64.b64decode(encoded_data_b64.encode("utf-8"))
    return decrypt(encrypted_data,key)

# 📦 지문 특징 추출 + 암호화 + 인코딩
def encode_and_encrypt(sensor, buffer_id: int, key: bytes) -> str:
    fingerprint_data = bytes(sensor.downloadCharacteristics(buffer_id))
    encrypted = encrypt(fingerprint_data, key)
    return base64.b64encode(encrypted).decode(), fingerprint_data

# 🔄 지문 등록 전체 처리
def register_fingerprint():
    # 1. 센서 연결
    try:
        sensor = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)
        if not sensor.verifyPassword():
            raise ValueError("지문 센서 비밀번호 오류")
    except Exception as e:
        print("❌ 센서 연결 실패:", e)
        return

    # 2. 지문 스캔
    print("첫 번째 지문을 스캔해주세요.")
    start_time = time.time()

    while time.time() - start_time < 5 :
        if sensor.readImage() != False :
            sensor.convertImage(0x01)
            break
    print("첫 번째 지문이 등록되었습니다. \n두 번째 지문을 스캔해주세요.")
    start_time = time.time()
    
    while time.time() - start_time < 5 :
        if sensor.readImage() != False :
            sensor.convertImage(0x02)
            break
    
    if sensor.compareCharacteristics() == 0:
        raise Exception("등록한 지문이 일치하지 않습니다.")

    # 3. 키 생성 (password + salt)
    password = "your_project_password"
    salt = os.urandom(16)
    key = generate_key(password, salt)
    
    # 4. 지문 암호화 (같은 키로 둘 다)
    fp_data1, original_fp1 = encode_and_encrypt(sensor, 0x01, key)
    fp_data2, original_fp2 = encode_and_encrypt(sensor, 0x02, key)
    salt_b64 = base64.b64encode(salt).decode("utf-8")

    sensor.createTemplate()
    sensor.storeTemplate()
    
    decrypted_fp1 = decode_and_decrypt(fp_data1,key)
    decrypted_fp2 = decode_and_decrypt(fp_data2,key)

    print("원본 fp1 길이 :", len(original_fp1))
    print("복호화 된 fp1 길이 :", len(decrypted_fp1))
    print("두 값이 같은가?", original_fp1 == decrypted_fp1)

    print("원본 fp2 길이 :", len(original_fp2))
    print("복호화 된 fp2 길이 :", len(decrypted_fp2))
    print("두 값이 같은가?", original_fp2 == decrypted_fp2)

    print("지문 등록 완료")
    
if __name__ == "__main__":
    register_fingerprint()