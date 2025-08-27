import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi  # 핵심: .ui 파일을 직접 불러옴
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from Fingerprint_status import Status, get_status, set_status, get_student_id ,set_student_id, set_sensor_active, clear_student_id

# UI 담당 클래스
class FingerprintUI(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Fingerprint_SUHYUN/fingerprint_gui.ui", self)  # Qt Designer로 만든 .ui 파일을 불러옴
        self.show()
        self.showFullScreen()
        self.threads = []
        
        # 타이머 세팅
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1000ms = 1초
        self.update_time()
        
        # 등교, 하교, 외출, 복귀 시 같은 페이지로 이동하지만 페이지는 같음으로 구분하는 변수
        self.current_action = None
        
        self.action_buttons = {
            Status.ATTENDANCE: self.move_enter_page_button,
            Status.LEAVE: self.move_leave_page_button,
            Status.RETURN: self.move_return_page_button,
            Status.EATING: self.eating_button,
            Status.LIB: self.gs25_button,
            Status.ETC: self.etc_button,
            Status.CLOSE: self.yes_button,
        }
        
        self.move_registration_page_button.clicked.connect(self.go_to_registration_page)
        self.move_outside_page_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_outside))
        self.no_button.clicked.connect(lambda: self.on_status_button_clicked(Status.LEAVE))

        for status, button in self.action_buttons.items():
            button.clicked.connect(lambda _, s=status: self.on_status_button_clicked(s))

        # 백스페이스 키와 엔터 키 함수
        self.backspace_button.clicked.connect(self.on_delete_clicked)
        self.enter_button.clicked.connect(self.on_enter_button_clicked)
        
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
        
    
    # 수정된 코드 (모든 페이지의 메시지 라벨을 업데이트하고, 3초 뒤 초기화)
    def on_message_received(self, msg: str):
        # 스레드로부터 메시지를 받아 모든 관련 라벨에 표시하는 슬롯
        # 여러 페이지에 메시지 라벨이 있다면 모두 업데이트
        self.fingerprint_msg_label.setText(msg)
        self.registration_msg_label.setText(msg)

        # 3초 후에 메시지를 다시 기본 상태로 되돌리는 타이머
        QTimer.singleShot(3000, self.clear_all_messages)

    def clear_all_messages(self):
        # 모든 메시지 라벨을 기본 텍스트로 초기화
        self.fingerprint_msg_label.setText("지문을 입력하세요")
        self.registration_msg_label.setText("학번을 입력하세요")

    def keyPressEvent(self, event):  # ESC 키보드 핸들러 추가
        if event.key() == Qt.Key_Escape:
            self.close()
    
    # 현재 시각을 업데이트 함수
    def update_time(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.current_time_label.setText(f"현재 시각 : {now}")
    
    def on_status_button_clicked(self, status: Status):
        # 상태(Status)를 인자로 받아 모든 버튼의 클릭 이벤트를 처리하는 중앙 핸들러
        set_status(status)  # 어떤 버튼이 눌렸든 먼저 상태부터 설정합니다.
        print(f"상태 변경: {get_status()}") # 정상 동작하는지 확인용

        # 상태에 따라 페이지를 전환하고 필요한 작업을 수행합니다.
        if status == Status.REGISTER:
            self.stackedWidget.setCurrentWidget(self.page_registration)
            self.registration_msg_label.setText(get_student_id())
            
        elif status == Status.LEAVE:
            # '예/아니오' 페이지가 아닐 때만 last_member 페이지로 이동합니다.
            if self.stackedWidget.currentWidget() != self.page_last_member:
                self.stackedWidget.setCurrentWidget(self.page_last_member)
            else: # '아니오'를 눌렀을 때는 지문 페이지로 이동합니다.
                self.stackedWidget.setCurrentWidget(self.page_fingerprint)
        else: 
            # GO_TO_SCHOOL, RETURN, EATING, GS25, ETC, CLOSE 등 나머지는 모두 지문 페이지로 이동
            self.stackedWidget.setCurrentWidget(self.page_fingerprint)

    # 메인 화면으로 돌아가기 버튼 함수
    def on_back_main_clicked(self) :
        self.stackedWidget.setCurrentWidget(self.page_main)
        self.fingerprint_msg_label.setText("지문을 입력하세요")

    def go_to_registration_page(self):
        # 등록 페이지로 이동하고, 학번을 초기화하며, 센서는 끈 상태를 유지합니다.
        self.stackedWidget.setCurrentWidget(self.page_registration)
        clear_student_id()
        self.registration_msg_label.setText(get_student_id()) # 빈 학번으로 라벨 업데이트
        set_sensor_active(False) # 페이지 이동 시에는 센서를 확실히 끈다.

    # 각 숫자 버튼 클릭 함수
    def on_digit_button_clicked(self, digit) :
        # status 파일에서 현재 학번을 가져와서 수정합니다.
        current_id = get_student_id()
        updated_id = current_id + digit
        set_student_id(updated_id)
        # 화면 라벨에도 최신 학번을 표시합니다.
        self.registration_msg_label.setText(get_student_id())
    
    # 뒤로 가기 버튼 함수
    def on_delete_clicked(self) :
        # status 파일에서 현재 학번을 가져와서 수정합니다.
        current_id = get_student_id()
        updated_id = current_id[:-1]
        set_student_id(updated_id)
        # 화면 라벨에도 최신 학번을 표시합니다.
        self.registration_msg_label.setText(get_student_id())

    def on_enter_button_clicked(self):
        # 엔터 버튼: 학번 입력을 완료하고 'REGISTER' 상태로 전환하여 스캔을 시작합니다.
        current_id = get_student_id()

        # 학번 유효성 검사
        if len(current_id) != 7:
            self.registration_msg_label.setText("학번 7자리를 입력하세요.")
            QTimer.singleShot(2000, lambda: self.registration_msg_label.setText(current_id))
            return

        # ✨ 엔터 키를 누르는 순간, 'REGISTER' 상태로 변경하라고 신호를 보냅니다.
        set_status(Status.REGISTER)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FingerprintUI()
    sys.exit(app.exec_())