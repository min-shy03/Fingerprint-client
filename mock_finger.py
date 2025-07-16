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

# 센서 내 메모리 공간은 리스트로 표현한다.
sensor = [0] * 26


# 지문 읽는 함수
def readImage() :
    image_buffer.append(input())
    
    # 지문이 잘못 들어왔으면 예외 처리
    return True if image_buffer[0].isalpha() else False

# 이미지 버퍼에 저장된 지문 이미지 문자열 형태로 변환 후 인자값으로 들어온 문자 버퍼에 저장하는 함수
def convertImage(buffer) :
    buffer[0] = image_buffer.pop()
    
    return True

# 현재 x01, x02 버퍼에 저장된 두 지문이 같은지 확인하는 함수
def compareCharacteristics() :
    # 버퍼에 등록 된 두 지문이 같은지 확인하여 같으면 True(1) 다르면 False(0) 리턴
    return x01[0] == x02[0]

# 문자 버퍼에 저장된 소문자 알파벳을 대문자 알파벳(템플릿) 으로 변환한 후 다시 문자 버퍼 1, 2에 저장하는 함수
def createTemplate() :
    template = x01[0].upper()
    
    x01[0] = template
    x02[0] = template
    
    return True

# 지정된 문자 버퍼의 템플릿을 주어진 위치에 저장 기본 값은 빈공간 가장 앞 자리로 지정
def storeTemplate(index = -1, buffer = 1) :
    if index == -1 :
        for i, v in enumerate(sensor) :
            if v == 0 :
                if buffer == 1 :
                    sensor[i] = x01[0]
                else :
                    sensor[i] = x02[0]
                break
        else :
            return "Exception : 버퍼 공간 최대" 
        
        return i
    else :
        if sensor[index] == 0 :
            if buffer == 1 :
                sensor[index] = x01[0]
            else :
                sensor[index] = x02[0]
        else :
            return "Exception"
        
        return index
    


print("센서 등록 완료")
while True :
    # 버퍼 공간은 임의의 리스트 공간으로 지정한다.
    image_buffer = []
    x01 = [""]
    x02 = [""]
    std_num = ""
    
    print(sensor)
    
    print("===== 메뉴 =====")
    print("1. 지문 등록\n2. 지문 검증\n3. 지문 삭제\n4. 지문 전체 삭제\n5. 프로그램 종료")
    
    choice = input("메뉴 선택 : ")
    
    # 1. 지문 등록
    if choice == "1" :
        std_num = input("지문을 등록하실 분의 학번을 입력하세요. : ")
        
        print("첫 번째 지문 스캔 (소문자 알파벳)")
        if readImage() :
            convertImage(x01)
        else :
            print("지문 인식 실패")
            continue
        
        print("두 번째 지문 스캔 (이전과 같은 알파벳)")
        if readImage() :
            convertImage(x02)
        else :
            print("지문 인식 실패")
            continue
        
        if compareCharacteristics() == 0 :
            print("등록한 지문이 일치하지 않습니다.")
            continue
        
        createTemplate()
        storeTemplate()
        print("지문 등록 완료")
        
    elif choice == "5" :
        break