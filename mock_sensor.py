import random

# 센서 내 메모리 공간은 리스트로 표현한다.
sensor = [0] * 26
student_lst = [0] * 26

# 버퍼 공간은 임의의 리스트 공간으로 지정한다.
image_buffer = []
x01 = [""]
x02 = [""]

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

# 현재 센서에 저장된 템플릿 갯수 반환하는 함수
def getTemplateCount() :
    count = 0
    for i in sensor :
        if i != 0 :
            count += 1
    
    return count

# 센서에 저장된 데이터베이스에서 현재 입력받은 지문 데이터가 존재하는지 검색하는 함수
def searchTemplate(charBufferNumber=1, positionStart=0 , count=-1) :
    target = x01[0].upper() if charBufferNumber == 1 else x02[0].upper()
    
    # 일치하는 지문이 있으면 그 위치값과 정확도 점수 반환 (정확도는 랜덤으로 반환 같은 데이터여도 실패할 확률 50%)
    for i in range(positionStart, len(sensor)) :
        if sensor[i] == target :
            return (i, random.randint(1,100))
    else :
        return (-1, 0)

# 센서에 저장된 데이터를 전부 삭제하는 함수
def clearDatabase() :
    for i in range(26) :
        sensor[i] = 0
    
    return True