import tkinter as tk
from tkinter import ttk


UNIT_TO_N = {
    "N": 1.0,
    "kN": 1000.0,
    "kgf": 9.81,
}


def convert_force(value, unit):
    """입력한 힘을 N, kN, kgf로 변환한다."""
    force_n = value * UNIT_TO_N[unit]
    return force_n, force_n / 1000.0, force_n / 9.81


def main():
    root = tk.Tk()
    root.title("힘 단위 변환 계산기")
    root.geometry("430x360")
    root.resizable(False, False)

    input_value = tk.StringVar()
    input_unit = tk.StringVar(value="kN")
    result_text = tk.StringVar(value="값과 단위를 입력한 뒤 변환 버튼을 누르세요.")

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="힘 단위 변환 계산기", font=("맑은 고딕", 16, "bold")).pack(pady=(0, 18))

    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x")
    ttk.Label(input_frame, text="입력값").grid(row=0, column=0, padx=(0, 8), pady=6, sticky="w")
    value_entry = ttk.Entry(input_frame, textvariable=input_value, width=20)
    value_entry.grid(row=0, column=1, padx=(0, 8), pady=6)
    unit_box = ttk.Combobox(
        input_frame,
        textvariable=input_unit,
        values=list(UNIT_TO_N),
        state="readonly",
        width=7,
    )
    unit_box.grid(row=0, column=2, pady=6)

    result_label = ttk.Label(
        frame,
        textvariable=result_text,
        justify="left",
        anchor="w",
        relief="groove",
        padding=12,
    )
    result_label.pack(fill="x", pady=18)

    def calculate():
        try:
            text = input_value.get().strip()
            if not text:
                raise ValueError("값이 비어 있습니다.")
            value = float(text)
            if value < 0:
                raise ValueError("힘은 0 이상으로 입력하세요.")
            force_n, force_kn, force_kgf = convert_force(value, input_unit.get())
            result_text.set(
                f"변환 결과\n"
                f"N   : {force_n:,.2f} N\n"
                f"kN  : {force_kn:,.2f} kN\n"
                f"kgf : {force_kgf:,.2f} kgf"
            )
            copy_button.state(["!disabled"])
        except (ValueError, KeyError) as error:
            result_text.set(f"오류: {error}")
            copy_button.state(["disabled"])
            value_entry.focus_set()

    def copy_result():
        root.clipboard_clear()
        root.clipboard_append(result_text.get())

    def clear_input():
        input_value.set("")
        input_unit.set("kN")
        result_text.set("값과 단위를 입력한 뒤 변환 버튼을 누르세요.")
        copy_button.state(["disabled"])
        value_entry.focus_set()

    button_frame = ttk.Frame(frame)
    button_frame.pack()
    ttk.Button(button_frame, text="변환", command=calculate).grid(row=0, column=0, padx=4)
    ttk.Button(button_frame, text="입력 지우기", command=clear_input).grid(row=0, column=1, padx=4)
    copy_button = ttk.Button(button_frame, text="결과 복사", command=copy_result, state="disabled")
    copy_button.grid(row=0, column=2, padx=4)

    value_entry.bind("<Return>", lambda event: calculate())
    value_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()