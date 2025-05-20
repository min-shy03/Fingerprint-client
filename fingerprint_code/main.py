import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi  # 핵심: .ui 파일을 직접 불러옴
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtCore import QDateTime
import requests
from PyQt5.QtCore import QThread, pyqtSignal

# UI 담당 클래스
class FingerprintUI(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("fingerprint_code/fingerprint_gui.ui", self)  # Qt Designer로 만든 .ui 파일을 불러옴
        self.show()
        
        # 타이머 세팅
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1000ms = 1초
        self.update_time()
        
        # 등교, 하교, 외출 복귀 시 같은 페이지로 이동하지만 페이지는 같음으로 구분하는 변수
        self.current_action = None
        
        # 각 화면 변경 코드
        self.move_enter_page_button.clicked.connect(lambda: self.on_action_selected("등교", self.page_fingerprint))
        self.move_leave_page_button.clicked.connect(lambda: self.on_action_selected("하교", self.page_fingerprint))
        self.move_return_page_button.clicked.connect(lambda: self.on_action_selected("복귀", self.page_fingerprint))
        self.move_outside_page_button.clicked.connect(lambda: self.on_action_selected("외출", self.page_outside))
        self.move_registration_page_button.clicked.connect(self.on_register_clicked)
        
        # 외출 사유 실행 코드
        self.eating_button.clicked.connect(lambda: self.on_action_selected("식사", self.page_fingerprint))
        self.gs25_button.clicked.connect(lambda: self.on_action_selected("편의점", self.page_fingerprint))
        self.gym_button.clicked.connect(lambda: self.on_action_selected("운동", self.page_fingerprint))
        self.etc_button.clicked.connect(lambda: self.on_action_selected("기타", self.page_fingerprint))
        
        # 메인화면 복귀 코드
        self.back_main_button.clicked.connect(self.on_back_main_clicked)

        # 코파일럿 수정 버전 학번 입력 버튼 딕셔너리화
        digit_buttons = {
            self.zero_button: "0",
            self.one_button: "1",
            self.two_button: "2",
            self.three_button: "3",
            self.four_button: "4",
            self.five_button: "5",
            self.six_button: "6",
            self.seven_button: "7",
            self.eight_button: "8",
            self.nine_button: "9",
        }
        
        for button, digit in digit_buttons.items():
            button.clicked.connect(lambda _, d=digit: self.on_digit_button_clicked(d))
        
        # 백스페이스 키와 엔터 키 함수
        self.backspace_button.clicked.connect(self.on_delete_clicked)
        self.enter_button.clicked.connect(self.on_enter_button_clicked)
        
    
    # 현재 시각을 업데이트 함수
    def update_time(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.current_time_label.setText(f"현재 시각 : {now}")
    
    # 메인 화면으로 돌아가기 버튼 함수
    def on_back_main_clicked(self) :
        self.stackedWidget.setCurrentWidget(self.page_main)
        
    # 지문 등록 버튼 함수
    def on_register_clicked(self):
        self.current_action = "등록"
        self.student_id = ""
        self.registration_msg_label.setText("")
        self.stackedWidget.setCurrentWidget(self.page_registration)

    # 등교, 외출, 복귀, 하교 버튼 클릭시 실행될 함수        
    def on_action_selected(self, action_name, page_widget):
        self.current_action = action_name
        self.stackedWidget.setCurrentWidget(page_widget)
        
    # 각 숫자 버튼 클릭 함수
    def on_digit_button_clicked(self, digit) :
        current = self.registration_msg_label.text()
        updated = current + digit
        self.registration_msg_label.setText(updated)
        self.student_id = updated
        
    # 뒤로 가기 버튼 함수
    def on_delete_clicked(self) :
        current = self.registration_msg_label.text()
        updated = current[:-1]
        self.registration_msg_label.setText(updated)
        self.student_id = updated
    
    # 엔터 버튼 함수
    def on_enter_button_clicked(self) : 
        self.worker = FingerprintWorker(self.student_id, self.current_action)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
    
    # 서버 응답 결과 
    def on_worker_finished(self, result):
        self.registration_msg_label.setText(result)

# 서버 요청 담당 클래스
class FingerprintWorker(QThread):
    finished = pyqtSignal(str)  # 결과 메시지 전달용 시그널

    def __init__(self, student_id, action):
        super().__init__()
        self.student_id = student_id
        self.action = action
        
    def run(self):
        try:
            # api 형식
            data = {
                "std_num": self.student_id,
                "action": self.action
            }
            
            # 서버에 요청 보내기
            res = requests.post("http://210.101.236.158:8081/api/fingerprint/logs", json=data)

            if res.status_code == 200:
                self.finished.emit("서버 응답: 성공")
            else:
                self.finished.emit(f"서버 오류: {res.status_code}")
        except Exception as e:
            self.finished.emit(f"예외 발생: {str(e)}")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FingerprintUI()
    sys.exit(app.exec_())