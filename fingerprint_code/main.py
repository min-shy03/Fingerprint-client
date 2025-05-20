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
        
        # 외출 시 사유 저장 변수
        self.outside_reason = None 
        
        # 각 화면 변경 코드
        self.move_registration_page_button.clicked.connect(self.on_register_clicked)
        self.back_main_button.clicked.connect(self.on_back_main_clicked)
        self.move_enter_page_button.clicked.connect(self.on_enter_clicked)
        self.move_outside_page_button.clicked.connect(self.on_outside_clicked)
        self.move_return_page_button.clicked.connect(self.on_return_clicked)
        self.move_leave_page_button.clicked.connect(self.on_leave_clicked)
        self.eating_button.clicked.connect(self.outside_reason_eating)
        self.gs25_button.clicked.connect(self.outside_reason_gs25)
        self.gym_button.clicked.connect(self.outside_reason_gym)
        self.etc_button.clicked.connect(self.outside_reason_etc)
        
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
        self.current_action = "register"
        self.student_id = ""
        self.registration_msg_label.setText("")
        self.stackedWidget.setCurrentWidget(self.page_registration)
        
    # 등교 버튼 함수
    def on_enter_clicked(self) :
        self.current_action = "enter"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
    
    # 외출 버튼 함수
    def on_outside_clicked(self) :
        self.current_action = "outside"
        self.stackedWidget.setCurrentWidget(self.page_outside)
    
    # 복귀 버튼 함수
    def on_return_clicked(self) :
        self.current_action = "return"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
    
    # 하교 버튼 함수
    def on_leave_clicked(self) :
        self.current_action = "leave"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
        
    # 외출 사유별 버튼
    def outside_reason_eating(self) :
        self.outside_reason = "eating"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
    
    def outside_reason_gs25(self) :
        self.outside_reason = "gs25"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
        
    def outside_reason_gym(self) :
        self.outside_reason = "gym"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
        
    def outside_reason_etc(self) :
        self.outside_reason = "etc"
        self.stackedWidget.setCurrentWidget(self.page_fingerprint)
    
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

# 서버 요청 담당 클래스
class FingerprintWorker(QThread):
    finished = pyqtSignal(str)  # 결과 메시지 전달용 시그널

    def __init__(self, student_id, action, reason=None):
        super().__init__()
        self.student_id = student_id
        self.action = action
        self.reason = reason
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FingerprintUI()
    sys.exit(app.exec_())