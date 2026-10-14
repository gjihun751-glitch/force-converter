import tkinter as tk
from math import isfinite, pi
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


SECTION_FIELDS = {
    "사각형": (("폭 b (mm)", "b"), ("높이 h (mm)", "h")),
    "원형봉": (("지름 d (mm)", "d"),),
    "원형관": (("외경 D (mm)", "D"), ("두께 t (mm)", "t")),
    "사각형관": (
        ("외측 폭 B (mm)", "B"),
        ("외측 높이 H (mm)", "H"),
        ("두께 t (mm)", "t"),
    ),
    "H형강": (
        ("전체 높이 H (mm)", "H"),
        ("플랜지 폭 B (mm)", "B"),
        ("웨브 두께 tw (mm)", "tw"),
        ("플랜지 두께 tf (mm)", "tf"),
    ),
}


def parse_section_dimensions(shape: str, raw_dimensions: dict[str, str]) -> dict[str, float]:
    fields = {key: label for label, key in SECTION_FIELDS[shape]}
    dimensions = {}
    for key, label in fields.items():
        raw_value = raw_dimensions.get(key, "").strip()
        if not raw_value:
            raise ValueError(f"{label} 값을 입력하세요.")
        try:
            value = float(raw_value)
        except ValueError as error:
            raise ValueError(f"{label}은(는) 숫자로 입력하세요.") from error
        if not isfinite(value):
            raise ValueError(f"{label}은(는) 유한한 숫자로 입력하세요.")
        if value == 0:
            raise ValueError(f"{label}은 0보다 커야 합니다.")
        if value < 0:
            raise ValueError(f"{label}은 음수가 될 수 없습니다. 0보다 큰 값을 입력하세요.")
        dimensions[key] = value
    return dimensions


def calculate_section_area(shape: str, dimensions: dict[str, float]) -> float:
    if any(not isfinite(value) for value in dimensions.values()):
        raise ValueError("모든 치수는 유한한 숫자로 입력해야 합니다.")
    if any(value <= 0 for value in dimensions.values()):
        raise ValueError("모든 치수는 0보다 커야 합니다.")

    if shape == "사각형":
        return dimensions["b"] * dimensions["h"]
    if shape == "원형봉":
        diameter = dimensions["d"]
        return pi * diameter**2 / 4
    if shape == "원형관":
        outer_diameter = dimensions["D"]
        thickness = dimensions["t"]
        if 2 * thickness >= outer_diameter:
            raise ValueError("원형관은 내부 공간이 생기도록 2t < D여야 합니다.")
        inner_diameter = outer_diameter - 2 * thickness
        return pi * (outer_diameter**2 - inner_diameter**2) / 4
    if shape == "사각형관":
        outer_width = dimensions["B"]
        outer_height = dimensions["H"]
        thickness = dimensions["t"]
        if 2 * thickness >= outer_width or 2 * thickness >= outer_height:
            raise ValueError("사각형관은 2t < B이고 2t < H여야 합니다.")
        return outer_width * outer_height - (outer_width - 2 * thickness) * (
            outer_height - 2 * thickness
        )
    if shape == "H형강":
        total_height = dimensions["H"]
        flange_width = dimensions["B"]
        web_thickness = dimensions["tw"]
        flange_thickness = dimensions["tf"]
        if 2 * flange_thickness >= total_height:
            raise ValueError("H형강은 내부 웨브 공간이 생기도록 2tf < H여야 합니다.")
        if web_thickness >= flange_width:
            raise ValueError("H형강은 웨브 두께 tw가 플랜지 폭 B보다 작아야 합니다.")
        return (
            2 * flange_width * flange_thickness
            + (total_height - 2 * flange_thickness) * web_thickness
        )
    raise ValueError(f"지원하지 않는 단면 종류입니다: {shape}")


def main() -> None:
    root = tk.Tk()
    root.title("하중 데이터 분석")
    root.geometry("900x700")
    root.minsize(700, 520)

    selected_path = tk.StringVar()
    valid_count = tk.StringVar(value="유효 데이터 수: -")
    shape_type = tk.StringVar(value="사각형")
    dimension_vars = {
        (shape, key): tk.StringVar()
        for shape, fields in SECTION_FIELDS.items()
        for _, key in fields
    }
    area_text = tk.StringVar(value="단면적 A: - mm²")
    result_text = tk.StringVar(value="최대 응력: - MPa    해당 시간: - s")
    loaded_data: pd.DataFrame | None = None

    main_frame = ttk.Frame(root, padding=12)
    main_frame.pack(fill="both", expand=True)

    file_frame = ttk.Frame(main_frame)
    file_frame.pack(fill="x", pady=(0, 10))
    ttk.Button(file_frame, text="CSV 찾아보기", command=lambda: browse_csv()).pack(
        side="left", padx=(0, 8)
    )
    path_entry = ttk.Entry(file_frame, textvariable=selected_path, state="readonly")
    path_entry.pack(side="left", fill="x", expand=True)
    ttk.Label(main_frame, textvariable=valid_count).pack(anchor="w", pady=(0, 8))

    section_frame = ttk.LabelFrame(main_frame, text="단면 설정", padding=8)
    section_frame.pack(fill="x", pady=(0, 8))
    ttk.Label(section_frame, text="단면 종류").grid(row=0, column=0, padx=4, pady=4)
    shape_box = ttk.Combobox(
        section_frame,
        textvariable=shape_type,
        values=tuple(SECTION_FIELDS),
        state="readonly",
        width=10,
    )
    shape_box.grid(row=0, column=1, padx=4, pady=4)
    ttk.Label(section_frame, textvariable=area_text).grid(
        row=0, column=2, padx=12, pady=4, sticky="w"
    )
    dimension_frame = ttk.Frame(section_frame)
    dimension_frame.grid(row=1, column=0, columnspan=7, sticky="w")

    figure = Figure(figsize=(7, 4), dpi=100)
    axis = figure.add_subplot(111)
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Force (N)")
    figure.tight_layout()

    graph_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
    graph_frame.pack(fill="both", expand=True)
    canvas = FigureCanvasTkAgg(figure, master=graph_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()

    def reset_analysis_view() -> None:
        result_text.set("최대 응력: - MPa    해당 시간: - s")
        axis.clear()
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Force (N)")
        if loaded_data is not None and not loaded_data.empty:
            axis.plot(loaded_data["time_s"], loaded_data["force_N"], marker="o")
        figure.tight_layout()
        canvas.draw()

    result_frame = ttk.Frame(main_frame)
    result_frame.pack(fill="x", pady=(8, 0))
    ttk.Button(result_frame, text="분석", command=lambda: analyze()).pack(side="left")
    ttk.Label(result_frame, textvariable=result_text).pack(side="left", padx=12)

    def get_active_dimensions() -> dict[str, float]:
        shape = shape_type.get()
        raw_dimensions = {
            key: dimension_vars[(shape, key)].get()
            for _, key in SECTION_FIELDS[shape]
        }
        return parse_section_dimensions(shape, raw_dimensions)

    def update_area_display(*_args: str) -> None:
        reset_analysis_view()
        try:
            area_mm2 = calculate_section_area(
                shape_type.get(), get_active_dimensions()
            )
        except ValueError:
            area_text.set("단면적 A: - mm²")
            return
        area_text.set(f"단면적 A: {area_mm2:.2f} mm²")

    def refresh_dimension_fields(_event: tk.Event | None = None) -> None:
        for child in dimension_frame.winfo_children():
            child.destroy()
        shape = shape_type.get()
        for column, (label, key) in enumerate(SECTION_FIELDS[shape]):
            field_row = column // 2
            field_column = (column % 2) * 4
            ttk.Label(dimension_frame, text=label).grid(
                row=field_row, column=field_column, padx=4, pady=4, sticky="w"
            )
            ttk.Entry(
                dimension_frame,
                textvariable=dimension_vars[(shape, key)],
                width=9,
            ).grid(row=field_row, column=field_column + 1, padx=4, pady=4)
        update_area_display()

    shape_box.bind("<<ComboboxSelected>>", refresh_dimension_fields)
    for variable in dimension_vars.values():
        variable.trace_add("write", update_area_display)
    refresh_dimension_fields()

    def browse_csv() -> None:
        nonlocal loaded_data
        file_path = filedialog.askopenfilename(
            title="CSV 파일 선택",
            filetypes=(("CSV 파일", "*.csv"), ("모든 파일", "*.*")),
        )
        if not file_path:
            return

        selected_path.set(file_path)
        loaded_data = None
        result_text.set("최대 응력: - MPa    해당 시간: - s")
        try:
            raw_data = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            required_columns = {"time_s", "force_N"}
            missing_columns = required_columns.difference(raw_data.columns)
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(f"CSV에 필요한 열이 없습니다: {missing}")

            numeric_data = {
                column: pd.to_numeric(raw_data[column].str.strip(), errors="coerce")
                for column in ("time_s", "force_N")
            }
            valid_mask = numeric_data["time_s"].notna() & numeric_data[
                "force_N"
            ].notna()
            valid_data = pd.DataFrame(
                {
                    "time_s": numeric_data["time_s"].loc[valid_mask],
                    "force_N": numeric_data["force_N"].loc[valid_mask],
                }
            )

            loaded_data = valid_data
            valid_count.set(f"유효 데이터 수: {len(valid_data)}")
            axis.clear()
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Force (N)")
            if not valid_data.empty:
                axis.plot(valid_data["time_s"], valid_data["force_N"], marker="o")
            figure.tight_layout()
            canvas.draw()
        except (OSError, pd.errors.ParserError, UnicodeError, ValueError) as error:
            valid_count.set("유효 데이터 수: -")
            axis.clear()
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Force (N)")
            canvas.draw()
            messagebox.showerror("CSV 읽기 오류", str(error), parent=root)

    def analyze() -> None:
        if loaded_data is None:
            messagebox.showerror("분석 오류", "먼저 CSV 파일을 선택하세요.", parent=root)
            return
        if loaded_data.empty:
            messagebox.showerror(
                "분석 오류", "유효한 데이터가 없습니다.", parent=root
            )
            return

        try:
            area_mm2 = calculate_section_area(shape_type.get(), get_active_dimensions())
        except ValueError as error:
            reset_analysis_view()
            messagebox.showerror(
                "입력 오류", str(error) or "필요한 치수를 숫자로 입력하세요.", parent=root
            )
            return

        stress_data = loaded_data.copy()
        stress_data["stress_MPa"] = stress_data["force_N"] / area_mm2
        maximum_index = stress_data["stress_MPa"].idxmax()
        maximum_stress = stress_data.at[maximum_index, "stress_MPa"]
        maximum_time = stress_data.at[maximum_index, "time_s"]
        result_text.set(
            f"최대 응력: {maximum_stress:g} MPa    해당 시간: {maximum_time:g} s"
        )

        axis.clear()
        axis.plot(stress_data["time_s"], stress_data["stress_MPa"], marker="o")
        axis.scatter(maximum_time, maximum_stress, color="red", zorder=3)
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Stress (MPa)")
        figure.tight_layout()
        canvas.draw()

    root.mainloop()


if __name__ == "__main__":
    main()