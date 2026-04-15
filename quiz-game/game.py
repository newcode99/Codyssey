import json
import os
from datetime import datetime
from quiz import Quiz
from utils import get_valid_input

class QuizGame:
    """게임의 상태 관리, 파일 입출력, 핵심 비즈니스 로직을 담당하는 뇌(Brain) 역할"""

    def __init__(self, data_path="state.json"):
        # 1. 시스템 설정 및 데이터 경로 초기화 작업
        self.data_path = data_path
        self.quizzes = []
        self.best_score = 0
        self.history = []
        
        # 2. 인스턴스 생성 시 자동으로 하드디스크 데이터 로드 시도
        self.load_state()

    def load_state(self) -> None:
        """하드디스크에서 데이터를 읽어와 RAM(quizzes, history)에 적재함"""
        if not os.path.exists(self.data_path):
            # 파일이 없는 경우(최초 실행) 빈 상태로 시작함
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.best_score = data.get("best_score", 0)
                self.history = data.get("history", [])
                
                # 딕셔너리 리스트를 Quiz 객체 리스트로 복원하는 변환 작업
                raw_quizzes = data.get("quizzes", [])
                self.quizzes = [Quiz.from_dict(q) for q in raw_quizzes]
                
        except (json.JSONDecodeError, KeyError):
            # 파일이 훼손된 경우 백업본을 만들고 시스템 리셋을 시도함
            backup_path = self.data_path + ".bak"
            os.replace(self.data_path, backup_path)
            print(f"[경고] 데이터 파일 훼손 감지. 기존 파일은 {backup_path}로 격리됨.")

    def save_state(self) -> None:
        """아토믹 쓰기(Atomic Write) 기법을 사용하여 데이터의 물리적 무결성을 보장하며 저장함"""
        # 1. 저장할 데이터를 딕셔너리 형태로 가공하는 직렬화 작업
        save_data = {
            "best_score": self.best_score,
            "history": self.history,
            "quizzes": [q.to_dict() for q in self.quizzes]
        }

        # 2. 원자적 쓰기: 임시 파일에 먼저 기록하여 파일 파손을 방지함
        tmp_path = self.data_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            
            # 3. 쓰기가 완료되면 원본 파일과 안전하게 교체 시킴
            os.replace(tmp_path, self.data_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

    def add_quiz(self, question: str, choices: list, answer: int) -> None:
        """사용자가 입력한 데이터를 바탕으로 새로운 Quiz 객체를 생성하여 목록에 추가함"""
        new_quiz = Quiz(question, choices, answer)
        self.quizzes.append(new_quiz)
        # 추가 즉시 저장하지 않고 RAM에만 유지함 (종료 시 일괄 저장)

    def delete_quiz(self, index: int) -> bool:
        """인덱스 번호를 기반으로 특정 퀴즈를 목록에서 소거함"""
        if 0 <= index < len(self.quizzes):
            self.quizzes.pop(index)
            return True
        return False

    def process_add_quiz(self) -> None:
        """사용자로부터 입력을 받아 새로운 퀴즈를 생성하는 일련의 과정을 제어함"""
        print("\n--- 새 퀴즈 추가 (질문 입력 시 빈칸이면 취소됨) ---")
        
        # 1. 질문 입력 및 취소 로직
        question = input("질문 내용: ").strip()
        if not question:
            print("[알림] 질문이 입력되지 않아 추가가 취소됨.")
            return

        # 2. 4개의 선택지 수집 작업
        choices = []
        for i in range(1, 5):
            while True:
                choice = input(f"선택지 {i}: ").strip()
                if choice:
                    choices.append(choice)
                    break
                print("[오류] 선택지 내용은 비어있을 수 없음.")

        # 3. 정답 번호 입력 (utils 필터링 활용)
        print("\n[정답 번호 설정]")
        answer = get_valid_input("정답 번호 (1~4): ", 1, 4)

        # 4. 검증 완료된 부품들로 최종 Quiz 객체 생성 및 리스트 추가
        try:
            self.add_quiz(question, choices, answer)
            print("\n[성공] 새로운 퀴즈가 목록에 추가됨.")
        except ValueError as e:
            print(f"\n[오류] 퀴즈 생성 실패: {e}")

    def update_history(self, score: int) -> None:
        """플레이 결과를 타임스탬프와 함께 히스토리에 누적함"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.history.append({"date": now, "score": score})
        
        # 최고 점수 자동 갱신 로직
        if score > self.best_score:
            self.best_score = score

    def play_quiz(self) -> None:
        """저장된 퀴즈 목록을 순회하며 게임을 진행하고 점수를 집계함"""
        if not self.quizzes:
            print("[알림] 등록된 퀴즈가 없음. 먼저 퀴즈를 추가해 주어야 함.")
            return

        current_score = 0
        total_quizzes = len(self.quizzes)

        print("\n--- 퀴즈 플레이 시작 (5번 입력 시 중도 포기 및 정산) ---")
        
        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[문제 {i}/{total_quizzes}]")
            quiz.display()
            print("5. [중도 포기 및 현재까지의 점수 정산]")

            # utils 필터를 통해 정제된 숫자(1~5) 확보 작업
            user_choice = get_valid_input("\n정답 선택: ", 1, 5)

            # 1. 5번 입력 시 루프를 탈정하여 현재까지의 점수만 인정함
            if user_choice == 5:
                print("\n[알림] 중도 포기 감지. 현재까지 맞춘 점수로 정산을 진행함.")
                break

            # 2. 채점 및 결과 출력 작업
            if quiz.check_answer(user_choice):
                print(">> 정답임! (+1점)")
                current_score += 1
            else:
                print(f">> 오답임. (정답: {quiz.answer}번)")

        # 3. 최종 플레이 결과 출력 및 데이터 갱신 작업
        print("\n--- 게임 종료 ---")
        print(f"최종 결과: {current_score} / {total_quizzes}")
        
        # 히스토리 누적 및 최고 점수 비교 갱신 진행
        self.update_history(current_score)
