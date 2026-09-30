def main():
    print("=" * 40)
    print("        힘 단위 변환 프로그램")
    print("=" * 40)

    while True:
        user_input = input("\n힘을 kN 단위로 입력하세요 (종료: q): ").strip()

        if user_input.lower() == "q":
            print("프로그램을 종료합니다.")
            break

        try:
            force_kn = float(user_input)
            force_n = force_kn * 1000.0
            force_kgf = force_n / 9.81

            print(f"- N   : {force_n:.2f} N")
            print(f"- kgf : 약 {force_kgf:.2f} kgf")

        except ValueError:
            print("[오류] 올바른 숫자를 입력하세요.")


if __name__ == "__main__":
    main()