class Quiz:
    ''' 파일 저장 및 문제 관리 '''
    def __init__(self, question: str, choices: list, answer: int):
        # 문제 문자열 입력 검증 (공백 예방)
        if not question or not str(question).strip():
            raise ValueError("문제 내용 누락됨")
            
        # 선택지 리스트 타입 및 4개 구성 강제
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 리스트 형태이며 요소 개수가 4개여야 함")
            
        # 정답 번호 타입 치환 및 유효 범위(1~4) 강제
        # 문자열 비교 구조("1" == "1")에 비해 연산 통일성에 유리한 정수형(1 == 1).
        # 사용자 입력 숫자값 대조 시, 타입 불일치 차단.
        try:
            valid_answer = int(answer)
        except ValueError:
            raise ValueError("정답 번호는 숫자형 표기여야 함")
            
        if valid_answer < 1 or valid_answer > 4:
            raise ValueError("정답 번호 범위 오류 (1~4)")

        # 통합 검증 통과 후 인스턴스 속성 메모리 최종 할당 작업
        self.question = str(question).strip()
        self.choices = choices
        self.answer = valid_answer
        
    def display(self) -> None:
        """문제 문자열 및 4개의 선택지를 터미널 환경에 출력함"""
        print(f"\n[문제] {self.question}")
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")
            
    def check_answer(self, user_answer_int: int) -> bool:
        """
        외부망(utils)에서 전달된 정수 입력값을 받아, 정답 번호 속성과 대조 / (Boolean)
        """
        return self.answer == user_answer_int
        
    def to_dict(self) -> dict:
    
        """게임 종료 시 JSON 파일 기록 포맷에 맞추기 위해 내부 속성을 딕셔너리로 치환 반환함"""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"]
        )

        """
        (조립 팩토리 메서드) 하드디스크에서 불러온 JSON 데이터(딕셔너리)를 넘겨받아 객체 조립(불러오기).
        딕셔너리 구조 분해 및 파싱에 관한 책임을 오직 해당 Quiz 클래스 내부에 격리(캡슐화)
        """