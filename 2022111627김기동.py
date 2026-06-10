import json
import os

# =====================================================================
# [졸업학점 및 환산 기준 설정]
# 학교 홈페이지 졸업 요건 보고 그대로 하드코딩해둠! 변경 시 여기만 수정하면 됨.
# =====================================================================
REQ_MAJOR = 60      # 졸업에 필요한 최소 전공 학점
REQ_SUB_MAJOR = 21  # 졸업에 필요한 최소 부전공 학점
REQ_CULTURE = 30    # 졸업에 필요한 최소 교양 학점

# 우리 학교에서 쓰는 표준 4.3 만점 기준 알파벳-학점 매핑 테이블
GRADE_TO_43 = {
    "A+": 4.3, "A0": 4.0, "A-": 3.7,
    "B+": 3.3, "B0": 3.0, "B-": 2.7,
    "C+": 2.3, "C0": 2.0, "C-": 1.7,
    "D+": 1.3, "D0": 1.0, "D-": 0.7, "F": 0.0
}

# 취업이나 타교 제출용 4.5 만점 기준으로 변환할 때 쓰는 1:1 매핑 테이블
CONVERT_43_TO_45 = {
    4.3: 4.5, 4.0: 4.2, 3.7: 4.0,
    3.3: 3.7, 3.0: 3.5, 2.7: 3.2,
    2.3: 2.7, 2.0: 2.5, 1.7: 2.2,
    1.3: 1.7, 1.0: 1.5, 0.7: 1.0, "0.0": 0.0, 0.0: 0.0
}

FILENAME = "grades.json"
my_subjects = []  # 사용자가 입력한 모든 수강 과목 데이터가 딕셔너리 형태로 누적되는 리스트


# =====================================================================
# [데이터 초기화 및 파일 입출력 함수]
# 처음 실행할 때 심심하지 않게 79학점 분량의 리얼한 가짜 데이터를 넣어둠.
# =====================================================================
SAMPLE_DATA = [
    {"name": "일반수학1", "semester": "1-1", "type": "교양", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "일반물리학1", "semester": "1-1", "type": "교양", "credit": 3, "grade_43": 4.3, "letter": "A+"},
    {"name": "일반화학1", "semester": "1-1", "type": "교양", "credit": 3, "grade_43": 3.7, "letter": "A-"},
    {"name": "공학설계입문", "semester": "1-1", "type": "전공", "credit": 3, "grade_43": 4.3, "letter": "A+"},
    {"name": "대학영어", "semester": "1-1", "type": "교양", "credit": 2, "grade_43": 3.3, "letter": "B+"},
    {"name": "컴퓨터프로그래밍", "semester": "1-1", "type": "교양", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "새내기세미나", "semester": "1-1", "type": "교양", "credit": 1, "grade_43": 4.3, "letter": "A+"},
    {"name": "일반수학2", "semester": "1-2", "type": "교양", "credit": 3, "grade_43": 3.3, "letter": "B+"},
    {"name": "일반물리학2", "semester": "1-2", "type": "교양", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "공학해석", "semester": "1-2", "type": "전공", "credit": 3, "grade_43": 3.7, "letter": "A-"},
    {"name": "철학의이해", "semester": "1-2", "type": "교양", "credit": 3, "grade_43": 4.3, "letter": "A+"},
    {"name": "과학기술글쓰기", "semester": "1-2", "type": "교양", "credit": 3, "grade_43": 3.0, "letter": "B0"},
    {"name": "경제학원론", "semester": "1-2", "type": "부전공", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "고체역학", "semester": "2-1", "type": "전공", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "열역학", "semester": "2-1", "type": "전공", "credit": 3, "grade_43": 4.3, "letter": "A+"},
    {"name": "공업수학1", "semester": "2-1", "type": "전공", "credit": 3, "grade_43": 3.0, "letter": "B0"},
    {"name": "미적분학학습", "semester": "2-1", "type": "교양", "credit": 2, "grade_43": 4.3, "letter": "A+"},
    {"name": "경영학개론", "semester": "2-1", "type": "부전공", "credit": 3, "grade_43": 3.7, "letter": "A-"},
    {"name": "마케팅원론", "semester": "2-1", "type": "부전공", "credit": 3, "grade_43": 3.3, "letter": "B+"},
    {"name": "창업론", "semester": "2-1", "type": "부전공", "credit": 4, "grade_43": 4.0, "letter": "A0"},
    {"name": "재료역학", "semester": "2-2", "type": "전공", "credit": 3, "grade_43": 3.7, "letter": "A-"},
    {"name": "유체역학", "semester": "2-2", "type": "전공", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "동역학", "semester": "2-2", "type": "전공", "credit": 3, "grade_43": 3.3, "letter": "B+"},
    {"name": "공업수학2", "semester": "2-2", "type": "전공", "credit": 3, "grade_43": 3.0, "letter": "B0"},
    {"name": "기계공학실험1", "semester": "2-2", "type": "전공", "credit": 2, "grade_43": 4.3, "letter": "A+"},
    {"name": "미시경제학", "semester": "2-2", "type": "부전공", "credit": 3, "grade_43": 4.0, "letter": "A0"},
    {"name": "재무관리", "semester": "2-2", "type": "부전공", "credit": 4, "grade_43": 3.7, "letter": "A-"}
]

def save_file_data():
    """ 현재까지 리스트에 쌓인 모든 성적 데이터를 JSON 파일로 깔끔하게 저장하는 함수 """
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(my_subjects, f, ensure_ascii=False, indent=4)

def load_file_data():
    """ 프로그램을 켤 때 이전 데이터를 불러오는 함수. 
        만약 저장된 파일이 없거나 텅 비어있으면 준비해둔 샘플 데이터를 기본으로 세팅함 """
    global my_subjects
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            my_subjects = json.load(f)
            if len(my_subjects) == 0:
                my_subjects = SAMPLE_DATA.copy()
                save_file_data()
    else:
        my_subjects = SAMPLE_DATA.copy()
        save_file_data()


# =====================================================================
# [메인 기능 함수들]
# =====================================================================

def input_new_subject():
    """ 1. 새 과목 성적 입력하기
        유저가 오타를 내거나 잘못된 값을 입력했을 때 팅기지 않도록 각 단계별로 예외 처리를 꼼꼼하게 해둔 함수.
        중간에 '종료'를 치면 언제든 메인 메뉴로 탈출이 가능함 """
    print("\n📝 [성적 입력 모드] (언제든지 '종료'를 입력하면 메뉴로 돌아갑니다.)")
    
    while True:
        # 1) 과목명 입력 단계
        name = input("\n과목명 입력: ").strip()
        if name == "종료":
            print("🏠 메뉴 창으로 복귀합니다.")
            break

        # 2) 이수 학기 입력 단계 (예: 2-1)
        semester = input("이수 학기 (예: 1-1, 2-2): ").strip()
        if semester == "종료":
            print("🏠 메뉴 창으로 복귀합니다.")
            break

        # 3) 이수 구분 검증 단계 (전공/부전공/교양 셋 중 하나만 입력할 때까지 무한 반복)
        is_canceled = False
        while True:
            sub_type = input("구분 (전공 / 부전공 / 교양 중 택1): ").strip()
            if sub_type == "종료":
                is_canceled = True
                break
            if sub_type in ["전공", "부전공", "교양"]:
                break
            print("❌ 글자 틀렸음! '전공', '부전공', '교양' 중에 정확히 입력 바람.")
        if is_canceled:
            print("🏠 메뉴 창으로 복귀합니다.")
            break

        # 4) 학점 수 검증 단계 (정수형 숫자가 들어올 때까지 예외 처리)
        while True:
            user_input = input("학점 수 (숫자만): ").strip()
            if user_input == "종료":
                is_canceled = True
                break
            try:
                credit = int(user_input)
                break
            except ValueError:
                print("❌ 숫자만 치라고 친구야...")
        if is_canceled:
            print("🏠 메뉴 창으로 복귀합니다.")
            break

        # 5) 성적 기호 검증 단계 (매핑 테이블에 있는 평점 기호인지 체크)
        while True:
            letter = input("성적 기호 (예: A+, B0, F): ").upper().strip()
            if letter == "종료":
                is_canceled = True
                break
            if letter in GRADE_TO_43:
                grade_value = GRADE_TO_43[letter]
                break
            print("❌ 성적 기호 오타남. 다시 제대로 입력해봐.")
        if is_canceled:
            print("🏠 메뉴 창으로 복귀합니다.")
            break

        # 검증 완료된 최종 데이터를 하나의 딕셔너리로 묶어서 리스트에 추가 후 파일 저장
        my_subjects.append({
            "name": name,
            "semester": semester,
            "type": sub_type,
            "credit": credit,
            "grade_43": grade_value,
            "letter": letter
        })
        save_file_data()
        print(f"✅ [{name}] 입력 및 저장 완료!")

        # 연속으로 다음 과목을 입력할지 여부 체크
        choice = input("\n🔄 다음 과목도 바로 입력할래? (Y/N): ").strip().upper()
        if choice != "Y" or choice == "종료":
            print("🏠 메뉴 창으로 복귀합니다.")
            break


def print_all_subjects():
    """ 2. 전체 과목 조회하기
        현재까지 수강한 과목들을 '이수 학기' 순으로 먼저 정렬하고, 그 안에서 다시 '구분' 순으로 예쁘게 정렬해서 보여주는 대시보드식 조회 함수 """
    if len(my_subjects) == 0:
        print("\n데이터가 텅 비었습니다.")
        return

    print("\n==================== 내가 수강한 과목 목록 ====================")
    # 학기(1-1, 1-2 등)순으로 1차 정렬, 전공/교양 등 구분으로 2차 정렬 진행
    sorted_data = sorted(my_subjects, key=lambda x: (x["semester"], x["type"]))
    
    count = 1
    for s in sorted_data:
        print(f"{count}. [{s['semester']}] {s['name']} | {s['type']} | {s['credit']}학점 | {s['letter']} ({s['grade_43']})")
        count += 1


def delete_one_subject():
    """ 3. 특정 과목 지우기
        전체 리스트를 한 번 쭉 띄워준 다음, 유저가 입력한 번호에 해당하는 과목을 리스트에서 안전하게 팝(pop)하고 자동 저장하는 함수 """
    print_all_subjects()
    if len(my_subjects) == 0:
        return
        
    try:
        select_num = int(input("\n삭제하고 싶은 과목 번호 입력: "))
        if 1 <= select_num <= len(my_subjects):
            # 사용자가 본 번호는 1부터 시작하므로 인덱스는 -1 해줌
            deleted = my_subjects.pop(select_num - 1)
            save_file_data()
            print(f"🗑️ [{deleted['name']}] 과목 정상적으로 지워짐!")
        else:
            print("❌ 없는 번호잖아..")
    except ValueError:
        print("❌ 숫자 번호를 입력해야지!!")


def show_my_dashboard():
    """ 4. 현재 학점 및 평점 대시보드 출력
        수강한 과목들을 전공/부전공/교양 카테고리별로 완벽하게 분류해서 각각의 이수 학점과 가중 평균 평점(4.3 및 4.5 기준)을 연산하고, 
        졸업 요건 대비 부족한 학점이 몇 학점인지 실시간으로 브리핑해주는 핵심 분석 함수 """
    if len(my_subjects) == 0:
        print("\n데이터가 없습니다.")
        return

    # 누적 계산을 위한 변수 초기화 (총합 / 전공 / 부전공 / 교양 분리)
    total_credits = 0
    total_weight_43 = total_weight_45 = 0

    major_credits = 0
    major_weight_43 = major_weight_45 = 0

    sub_major_credits = 0
    sub_major_weight_43 = sub_major_weight_45 = 0

    culture_credits = 0
    culture_weight_43 = culture_weight_45 = 0

    # 각 과목을 돌면서 학점 및 (학점 * 평점) 가중치 합산 진행
    for s in my_subjects:
        c = s["credit"]
        g43 = s["grade_43"]
        g45 = CONVERT_43_TO_45[g43]

        total_credits += c
        total_weight_43 += c * g43
        total_weight_45 += c * g45

        if s["type"] == "전공":
            major_credits += c
            major_weight_43 += c * g43
            major_weight_45 += c * g45
        elif s["type"] == "부전공":
            sub_major_credits += c
            sub_major_weight_43 += c * g43
            sub_major_weight_45 += c * g45
        elif s["type"] == "교양":
            culture_credits += c
            culture_weight_43 += c * g43
            culture_weight_45 += c * g45

    # 제로디비전(0으로 나누기) 에러 방지용 예외 처리와 함께 최종 평점 계산
    avg_total_43 = total_weight_43 / total_credits if total_credits > 0 else 0
    avg_total_45 = total_weight_45 / total_credits if total_credits > 0 else 0

    avg_major_43 = major_weight_43 / major_credits if major_credits > 0 else 0
    avg_major_45 = major_weight_45 / major_credits if major_credits > 0 else 0

    avg_sub_43 = sub_major_weight_43 / sub_major_credits if sub_major_credits > 0 else 0
    avg_sub_45 = sub_major_weight_45 / sub_major_credits if sub_major_credits > 0 else 0

    avg_culture_43 = culture_weight_43 / culture_credits if culture_credits > 0 else 0
    avg_culture_45 = culture_weight_45 / culture_credits if culture_credits > 0 else 0

    print("\n======================================")
    print("      📊 [현재 내 학점 대시보드]")
    print("======================================")
    print(f"[전체 평균 평점] 4.3기준: {avg_total_43:.2f} / 4.5기준: {avg_total_45:.2f}")
    print(f"[전공 평균 평점] 4.3기준: {avg_major_43:.2f} / 4.5기준: {avg_major_45:.2f}")
    print(f"[부전공 평균 평점] 4.3기준: {avg_sub_43:.2f} / 4.5기준: {avg_sub_45:.2f}")
    print(f"[교양 평균 평점] 4.3기준: {avg_culture_43:.2f} / 4.5기준: {avg_culture_45:.2f}")
    
    print("\n--------------------------------------")
    print("📋 [이수 완료 학점 현황]")
    print(f" • 전공   : {major_credits} / {REQ_MAJOR} 학점 (부족한 학점: {max(0, REQ_MAJOR - major_credits)}학점)")
    print(f" • 부전공 : {sub_major_credits} / {REQ_SUB_MAJOR} 학점 (부족한 학점: {max(0, REQ_SUB_MAJOR - sub_major_credits)}학점)")
    print(f" • 교양   : {culture_credits} / {REQ_CULTURE} 학점 (부족한 학점: {max(0, REQ_CULTURE - culture_credits)}학점)")
    print("======================================")


def run_simulation():
    """ 5. 미래 목표 학점 시뮬레이션
        유저가 원하는 최종 졸업 학점을 달성하기 위해 '앞으로 남은 학기 동안 평균 몇 평점을 받아야 하는지' 역산해주는 시뮬레이터.
        수학적으로 불가능한 수치(예: 남은 학기 평점 5.2 필요 등)가 나오거나 이미 목표를 달성한 경우 상황별 맞춤 멘트를 날려줌 """
    if len(my_subjects) == 0:
        print("\n데이터가 없어서 시뮬레이션 돌릴 수 없음.")
        return

    print("\n======================================")
    print("   🎯 목표 졸업 평점 & 학점 시뮬레이터")
    print("======================================")

    current_major = current_sub = current_culture = 0

    for s in my_subjects:
        if s["type"] == "전공":
            current_major += s["credit"]
        elif s["type"] == "부전공":
            current_sub += s["credit"]
        elif s["type"] == "교양":
            current_culture += s["credit"]

    print("\n📋 [졸업 필수 학점 기준 대비 현황]")
    need_major = max(0, REQ_MAJOR - current_major)
    need_sub = max(0, REQ_SUB_MAJOR - current_sub)
    need_culture = max(0, REQ_CULTURE - current_culture)
    
    print(f" • 전공   : 현재 {current_major}학점 / 졸업기준 {REQ_MAJOR}학점 (최소 {need_major}학점 더 채워야 함)")
    print(f" • 부전공 : 현재 {current_sub}학점 / 졸업기준 {REQ_SUB_MAJOR}학점 (최소 {need_sub}학점 더 채워야 함)")
    print(f" • 교양   : 현재 {current_culture}학점 / 졸업기준 {REQ_CULTURE}학점 (최소 {need_culture}학점 더 채워야 함)")
    
    total_need_credits = need_major + need_sub + need_culture
    print("--------------------------------------")
    print(f"💡 졸업 조건 맞추려면 앞으로 최소 총 {total_need_credits}학점 더 이수해야 합니다!")
    print("======================================")

    print("\n⚙️ 시뮬레이션 설정창")
    print("1. 우리 학교 4.3 학점 시스템")
    print("2. 취업용/타교 4.5 학점 시스템")
    system_choice = input("선택 (1번 또는 2번 입력): ").strip()
    
    max_limit = 4.3 if system_choice == "1" else 4.5

    try:
        my_goal = float(input(f"내가 원하는 최종 졸업 평점 (최대 {max_limit}): "))
        if my_goal > max_limit or my_goal < 0:
            print(f"❌ 점수 범위가 이상합니다. 0 ~ {max_limit} 사이로 적어주세요.")
            return

        left_semesters = int(input("졸업까지 남은 학기 수: "))
        if left_semesters <= 0:
            print("❌ 남은 학기는 최소 1학기 이상이어야 합니다.")
            return

        min_credit_per_semester = total_need_credits / left_semesters
        print(f"\n💡 졸업 조건 채우려면 매 학기 최소 {min_credit_per_semester:.1f}학점 이상 수강 신청 해야 해!")
        
        plan_credit_per_semester = int(input("너가 매 학기 실제로 들을 계획 학점 수: "))

    except ValueError:
        print("❌ 인풋에 문자가 들어갔거나 숫자가 이상해!")
        return

    # 가중치 계산을 위한 현재 상태 파악
    now_total_credits = sum(s["credit"] for s in my_subjects)
    if system_choice == "1":
        now_total_weight = sum(s["credit"] * s["grade_43"] for s in my_subjects)
    else:
        now_total_weight = sum(s["credit"] * CONVERT_43_TO_45[s["grade_43"]] for s in my_subjects)

    # 미래에 들을 총 학점과 졸업 시 예상 최종 누적 학점 계산
    future_total_credits = left_semesters * plan_credit_per_semester
    final_grad_credits = now_total_credits + future_total_credits

    # 목표 도달을 위해 미래에 채워야 하는 가중치 총점 계산
    target_total_weight = my_goal * final_grad_credits
    needed_future_weight = target_total_weight - now_total_weight

    # 앞으로 매 학기 받아야 하는 평균 평점 역산
    required_gpa = needed_future_weight / future_total_credits if future_total_credits > 0 else 0

    print("\n======================================")
    print("               📊 시뮬레이션 분석 결과")
    print("======================================")
    print(f"• 현재까지 채운 학점: {now_total_credits} 학점")
    print(f"• 앞으로 채울 학점  : {future_total_credits} 학점 (학기당 {plan_credit_per_semester}학점씩 {left_semesters}학기)")
    print(f"• 졸업할 때 최종 학점: {final_grad_credits} 학점")
    print(f"• 나의 졸업 목표 평점: {my_goal} / {max_limit}")
    print("--------------------------------------")

    # 계산 결과에 따른 분기 처리 및 피드백 출력
    if required_gpa > max_limit:
        print("❌ [달성 불가능...]")
        print(f" 남은 학기 동안 평점 평균을 {required_gpa:.2f} 받아야 함..")
        print(f" 올 A+을 넘어서는 수치라 현실적으로 목표 달성이 불가능합니다. 목표 평점을 낮추세요. 😥")
    elif required_gpa <= 0:
        print("🎉 [이미 달성!!]")
        print(f" 앞으로 전부 F를 받아도 목표 학점 {my_goal}점은 무조건 넘깁니다. 축하해!! 🥳")
    else:
        print("🔥 [달성 가능! 가이드라인]")
        print(f" 남은 {left_semesters}학기 동안 매 학기 평균 ** {required_gpa:.2f} / {max_limit} ** 이상")
        print(f" 성적을 받아내면 목표 평점 {my_goal} 달성할 수 있어! 조금만 더 힘내자! 💪")
    print("======================================")


# =====================================================================
# [프로그램 메인 엔진 루프]
# 사용자가 6번을 눌러 안전하게 종료할 때까지 터미널 창을 계속 띄워두고 입력을 받음
# =====================================================================
def main():
    load_file_data()  # 켜자마자 기존 성적 로그 자동 로드

    while True:
        print("\n===== 에브리타임+ (내가 만든 학점 계산기) =====")
        print("1. 새 과목 성적 입력")
        print("2. 전체 과목 조회")
        print("3. 특정 과목 삭제")
        print("4. 현재 이수 학점 및 평점 대시보드")
        print("5. 미래 목표 학점 시뮬레이션")
        print("6. 프로그램 안전 종료")

        menu_choice = input("기능 선택 (1~6): ").strip()

        if menu_choice == "1":
            input_new_subject()
        elif menu_choice == "2":
            print_all_subjects()
            input("\n↩️ 엔터 누르면 메뉴판으로 돌아감...")
        elif menu_choice == "3":
            delete_one_subject()
            input("\n↩️ 엔터 누르면 메뉴판으로 돌아감...")
        elif menu_choice == "4":
            show_my_dashboard()
            input("\n↩️ 엔터 누르면 메뉴판으로 돌아감...")
        elif menu_choice == "5":
            run_simulation()
            input("\n↩️ 엔터 누르면 메뉴판으로 돌아감...")
        elif menu_choice == "6":
            save_file_data()  # 데이터 유실 방지용 강제 저장
            print("성적 데이터 grades.json 에 잘 저장함! 종강 축하해!! Bye 👋")
            break
        else:
            print("❌ 번호 잘못 입력했어. 1번부터 6번 중에서 골라줘.")


if __name__ == "__main__":
    main()