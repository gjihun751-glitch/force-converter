from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SPECIMEN_AREA_MM2 = 100
REFERENCE_STRESS_MPA = 6


def main() -> None:
    csv_path = Path(__file__).resolve().with_name("load_data.csv")
    raw_data = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

    required_columns = {"time_s", "force_N"}
    missing_columns = required_columns.difference(raw_data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV에 필요한 열이 없습니다: {missing}")

    numeric_data = {
        column: pd.to_numeric(raw_data[column].str.strip(), errors="coerce")
        for column in ("time_s", "force_N")
    }
    valid_mask = numeric_data["time_s"].notna() & numeric_data["force_N"].notna()

    for row_position in range(len(raw_data)):
        for column in ("time_s", "force_N"):
            if pd.isna(numeric_data[column].iloc[row_position]):
                raw_value = raw_data.iloc[row_position][column]
                problem_value = "빈칸" if not raw_value.strip() else repr(raw_value)
                print(
                    f"문제값: CSV {row_position + 2}행, "
                    f"{column}={problem_value} (빈칸 또는 숫자가 아님)"
                )

    valid_data = pd.DataFrame(
        {
            "time_s": numeric_data["time_s"].loc[valid_mask],
            "force_N": numeric_data["force_N"].loc[valid_mask],
        }
    )
    valid_count = len(valid_data)
    excluded_count = len(raw_data) - valid_count
    print(f"제외한 행 수: {excluded_count}")
    print(f"유효한 데이터 수: {valid_count}")

    if valid_data.empty:
        print("유효한 데이터가 없어 계산과 그래프 생성을 중단합니다.")
        return

    valid_data["stress_MPa"] = valid_data["force_N"] / SPECIMEN_AREA_MM2

    maximum_index = valid_data["force_N"].idxmax()
    maximum_force = valid_data.at[maximum_index, "force_N"]
    maximum_time = valid_data.at[maximum_index, "time_s"]
    maximum_stress = valid_data.at[maximum_index, "stress_MPa"]
    exceeding_count = int(
        (valid_data["stress_MPa"] > REFERENCE_STRESS_MPA).sum()
    )

    print(f"최대하중: {maximum_force} N")
    print(f"해당시간: {maximum_time} s")
    print(f"최대응력: {maximum_stress} MPa")
    print(
        f"기준응력 {REFERENCE_STRESS_MPA} MPa 초과 데이터 개수: "
        f"{exceeding_count}개"
    )

    figure, axis = plt.subplots()
    axis.plot(valid_data["time_s"], valid_data["stress_MPa"], marker="o")
    axis.scatter(
        maximum_time,
        maximum_stress,
        color="red",
        s=70,
        zorder=3,
        label="Maximum stress",
    )
    axis.annotate(
        f"{maximum_time:g} s, {maximum_stress:g} MPa",
        (maximum_time, maximum_stress),
        xytext=(8, 8),
        textcoords="offset points",
    )
    axis.set_xlabel("time(s)")
    axis.set_ylabel("stress (mpa)")
    figure.tight_layout()
    plot_path = Path(__file__).resolve().with_name("stress_plot.png")
    figure.savefig(plot_path)
    plt.close(figure)
    print(f"그래프 저장: {plot_path.name}")


if __name__ == "__main__":
    main()