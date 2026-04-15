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

    def update_history(self, score: int) -> None:
        """플레이 결과를 타임스탬프와 함께 히스토리에 누적함"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.history.append({"date": now, "score": score})
        
        # 최고 점수 자동 갱신 로직
        if score > self.best_score:
            self.best_score = score
