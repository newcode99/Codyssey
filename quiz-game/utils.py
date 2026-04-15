def get_valid_input(prompt: str, min_val: int, max_val: int) -> int:
    """
    사용자로부터 유효한 정수 입력을 받아 정제하여 반환함.
    문자열, 빈칸, 범위 외 입력에 대한 방어벽 역할을 수행함.
    """
    while True:
        try:
            # 1. 입력 받기 및 양 끝 공백 제거 작업 (사용자 실수 방어)
            user_input = input(prompt).strip()
            
            # 2. 빈 문자열 입력 시 강제 에러 발생 (ValueError 유도)
            if not user_input:
                raise ValueError
            
            # 3. 정수형 변환 시도 (문자열 등이 들어오면 여기서 ValueError 발생)
            choice = int(user_input)
            
            # 4. 유효 범위(min_val ~ max_val) 검증 작업
            if min_val <= choice <= max_val:
                return choice
            else:
                print(f"[오류] {min_val}~{max_val} 사이의 숫자를 입력해야 함.")
                
        except ValueError:
            # 숫자가 아닌 문자나 빈칸이 입력된 경우의 예외 처리
            print("[오류] 올바른 숫자를 입력해 주어야 함.")
            
        except (KeyboardInterrupt, EOFError):
            # 사용자의 강제 종료(Ctrl+C, Ctrl+D) 시그널 감지 작업
            # 여기서 직접 죽지 않고, 상위 관리자(main/game)가 저장 로직을 수행하도록 폭탄을 토스함.
            print("\n[시스템] 종료 시그널 감지. 데이터 저장 모드로 전환함.")
            raise
