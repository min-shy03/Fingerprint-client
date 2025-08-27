from enum import Enum

# 열거 타입
class Status(Enum) :
    WAITING = "대기"
    REGISTER = "등록"
    ATTENDANCE = "등교"
    LEAVE = "하교"
    LIB = "도서관"
    EATING = "식사"
    ETC = "기타"
    RETURN = "복귀"
    CLOSE = "문닫기"

status = Status.WAITING     # 기본 상태 대기
sensor_active = False       # 지문 인식기 활성화 상태
student_id = ""             # 현재 입력된 학번

# Getter/Setter 메소드
def get_status() -> Status :
    # 현재 어플리케이션 상태 반환
    return status

def set_status(new_status : Status) -> None :
    # 어플리케이션 상태 변경, 반환값 없음
    # 매개 변수 Status 변수로만 받음
    # 대기 (WATTING) 상태일 때는 센서를 비활성화하고, 
    # 다른 상태일 때는 센서 활성화
    global status
    status = new_status

    if new_status == Status.WAITING :
        set_sensor_active(False)
    elif new_status == Status.REGISTER :
        set_sensor_active(True)
    else :
        set_sensor_active(True)
        clear_student_id()
        
def is_sensor_active() -> bool :
    # 센서가 활성화 상태인지 반환하는 함수
    return sensor_active

def set_sensor_active(active : bool) -> None :
    # 지문 인식기 활성화 상태 설정
    # 매개 변수 bool 타입 (True or False) 으로만 받음
    global sensor_active
    sensor_active = active

def get_student_id() -> str :
    # 현재 입력된 학번 반환
    return student_id

def set_student_id(new_student_id : str) -> None :
    # 학번 설정, 반환값 없음
    global student_id
    student_id = new_student_id

def clear_student_id() -> None :
    # 학번 초기화
    global student_id
    student_id = ""