import sys
from game import QuizGame
from utils import get_valid_input

def main():
    """애플리케이션의 전체 실행 흐름을 제어하고 예외 상황을 최종적으로 방어함"""
    # 1. 게임 엔진 초기화 (데이터 로드 포함)
    app = QuizGame()
    
    print("=" * 40)
    print("   [ 파이썬 전문 퀴즈 시스템 v1.0 ]")
    print("=" * 40)

    try:
        while True:
            print("\n[ 메인 메뉴 ]")
            print("1. 퀴즈 플레이 시작")
            print("2. 새로운 퀴즈 추가")
            print("3. 퀴즈 목록 보기")
            print("4. 퀴즈 삭제하기")
            print("5. 게임 통계 확인")
            print("6. 종료 및 저장")
            
            # utils 모듈을 통한 무결성 숫자 입력 받기
            choice = get_valid_input("\n메뉴 선택 (1~6): ", 1, 6)
            
            if choice == 1:
                app.play_quiz()
            elif choice == 2:
                app.process_add_quiz()
            elif choice == 3:
                app.view_quizzes()
            elif choice == 4:
                app.process_delete_quiz()
            elif choice == 5:
                app.view_statistics()
            elif choice == 6:
                print("\n[알림] 안전하게 저장을 진행하고 종료함.")
                app.save_state()
                break
                
    except (KeyboardInterrupt, EOFError):
        # 2. 비절차적 비상 종료 발생 시 최후의 방어선 작동
        # utils에서 전달된 폭탄(raise)을 여기서 잡아내어 RAM 데이터를 하드디스크에 긴급 피신시킴
        print("\n\n[비상] 비정상 종료 감지! 데이터를 긴급 저장하고 종료함.")
        app.save_state()
        sys.exit(0)
    except Exception as e:
        # 예상치 못한 시스템 오류 발생 시에도 데이터 보존 시도
        print(f"\n[치명적 오류] 시스템 내부 결함: {e}")
        app.save_state()
        sys.exit(1)

if __name__ == "__main__":
    main()
