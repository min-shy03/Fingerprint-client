# 목 데이터를 만들어 지문인식기를 구현해보자
# 각 기능별 함수로 구현하기
# 기능 목록
# 1. 지문 등록
# 2. 지문 검증
# 3. 지문 삭제
# 4. 지문 전체 삭제

# 센서는 이미 연결되어있다고 가정한다.

# 각 지문을 표현하기 위해 알파벳 26자를 사용할 예정
# 2개의 지문을 입력받아 하나의 템플릿으로 만드는 과정은 
# 두 개의 소문자를 입력받아 하나의 대문자 알파벳으로 변환하여 표현한다.
# ex) 0x01 = a , 0x02 = a => A

import mock_sensor as sensor

# 정확도 최소점
MATCH_THRESHOLD = 50

# 지문 등록 함수
def register_fingerprint() :
    std_num = input("지문을 등록하실 분의 학번을 입력하세요. : ")
        
    print("첫 번째 지문 스캔 (소문자 알파벳)")
    if sensor.readImage() :
        sensor.convertImage(sensor.x01)
    else :
        print("지문 인식 실패")
        return 
        
    print("두 번째 지문 스캔 (이전과 같은 알파벳)")
    if sensor.readImage() :
        sensor.convertImage(sensor.x02)
    else :
        print("지문 인식 실패")
        return
    
    if sensor.compareCharacteristics() == 0 :
        print("등록한 지문이 일치하지 않습니다.")
        return
    
    sensor.createTemplate()
    
    # 저장된 인덱스 혹은 에러 반환
    register_result = sensor.storeTemplate()
    if isinstance(register_result, int) :
        sensor.student_lst[register_result] = std_num
        print("지문 등록 완료")
    else :
        print(register_result)
        
def verify_fingerprint() :
    print("지문 스캔 (소문자 알파벳)")
    if sensor.readImage() :
        sensor.convertImage(sensor.x01)
    else :
        print("지문 인식 실패")
        return
    
    search_result = sensor.searchTemplate()
    
    # 만약 같은 지문이 발견되고 정확도가 50이 넘으면 학번 가져오기
    if search_result[0] >= 0 and search_result[1] >= MATCH_THRESHOLD :
        student_id = sensor.student_lst[search_result[0]]
        print(student_id)
    else :
        print("일치하는 지문 없음")

def delete_all_data() :
    print("현재 등록된 지문 데이터 수 :",sensor.getTemplateCount())
        
    choice_del = input("모든 지문 데이터를 삭제할까요? (yes or no) : ")
    
    if choice_del == "yes" :
        # 센서에 저장된 지문 데이터 삭제
        sensor.clearDatabase()
        # 학번 리스트도 같이 삭제
        sensor.student_lst = [0] * 26
        print("모든 지문 데이터를 삭제했습니다.")
    else :
        print("지문 삭제를 취소합니다.")
    

# 메인으로 실행될 코드
print("센서 등록 완료")
while True :
    
    # 현재 센서 내 데이터 출력
    print(sensor.sensor)
    
    print("===== 메뉴 =====")
    print("1. 지문 등록\n2. 지문 검증\n3. 지문 전체 삭제\n4. 프로그램 종료")
    
    choice = input("메뉴 선택 : ")
    
    # 1. 지문 등록
    if choice == "1" :
        register_fingerprint()
        
    # 2. 지문 검증
    elif choice == "2" :
        verify_fingerprint()
        
    # 3. 지문 전체 삭제
    elif choice == "3" :
        delete_all_data()
    
    # 4. 프로그램 종료
    elif choice == "4" :
        print("프로그램 종료.")
        break
    
    # 5. 이상한거 입력 시
    else :
        print("다시 입력하세요.")
        
    print("")