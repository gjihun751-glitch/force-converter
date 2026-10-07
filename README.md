# 힘 단위 변환 프로그램

## 용도

힘 값을 뉴턴(N), 킬로뉴턴(kN), 킬로그램힘(kgf) 단위로 변환하는 Python 프로그램입니다. 두 가지 실행 방식이 있습니다.

- `force_converter.py`: 콘솔에서 kN 값을 입력하고 N과 kgf 결과를 확인합니다.
- `force_converter gui.py`: GUI에서 N, kN, kgf 중 입력 단위를 선택하고 세 단위의 결과를 확인합니다.

## 필요한 환경

- Python 3
- GUI 프로그램은 Tkinter를 사용할 수 있는 Python 환경이 필요합니다.
- 코드에서 사용하는 모듈은 Python 표준 라이브러리(`tkinter`)뿐이며, 별도의 외부 패키지는 없습니다.

## 실행 방법

터미널에서 이 폴더로 이동한 뒤 원하는 프로그램 하나를 실행합니다. Windows에서는 다음 명령을 사용할 수 있습니다.

```powershell
py "force_converter.py"
```

GUI 버전은 다음과 같이 실행합니다.

```powershell
py "force_converter gui.py"
```

`py` 명령을 사용할 수 없는 환경에서는 `python`으로 바꿔 실행합니다.

## 입력 예시

### 콘솔 프로그램

힘을 kN 단위로 입력합니다. 예를 들어 `2`를 입력하면 다음 결과가 출력됩니다.

```text
- N   : 2000.00 N
- kgf : 약 203.87 kgf
```

`0`도 숫자 입력으로 처리됩니다. `q`를 입력하면 프로그램을 종료합니다.

### GUI 프로그램

입력값에 `2`를 입력하고 단위로 `kN`을 선택한 뒤 **변환**을 누르면 다음 값이 표시됩니다.

```text
N   : 2,000.00 N
kN  : 2.00 kN
kgf : 203.87 kgf
```

GUI는 N, kN, kgf를 입력 단위로 선택할 수 있으며 0 이상의 숫자를 입력받습니다. **입력 지우기**를 누르면 입력값이 지워지고 단위가 kN으로 돌아갑니다.

## 오류 입력 예시

- 콘솔 프로그램에서 `abc`처럼 숫자로 변환할 수 없는 값을 입력하면 `[오류] 올바른 숫자를 입력하세요.`가 표시됩니다.
- GUI에서 입력값을 비워 두면 `값이 비어 있습니다.` 오류가 표시됩니다.
- GUI에서 `abc`처럼 숫자가 아닌 값을 입력하면 변환 오류가 표시됩니다.
- GUI에서 `-1`처럼 음수를 입력하면 `힘은 0 이상으로 입력하세요.` 오류가 표시됩니다.

콘솔 프로그램은 숫자로 변환할 수 있는 음수도 별도 거부하지 않습니다.

## CSV 하중 분석 프로그램

`load_analyzer.py`는 같은 폴더의 `load_data.csv`를 읽어 하중과 응력을 분석합니다. 원본 CSV는 수정하지 않습니다.

### 입력 파일

CSV 첫 행에는 다음 열 이름이 필요합니다.

```csv
time_s,force_N
```

- `time_s`: 시간(초, s)
- `force_N`: 하중(뉴턴, N)

두 열의 값은 숫자여야 합니다. CSV에 `stress_MPa` 열이 있어도 분석기는 `time_s`와 `force_N`만 사용합니다.

### 필요한 라이브러리

- Python 3
- pandas
- matplotlib

프로젝트 가상환경에서 아직 라이브러리를 설치하지 않았다면 PowerShell에서 다음 명령을 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m pip install pandas matplotlib
```

### 단면적 설정

`load_analyzer.py`의 `SPECIMEN_AREA_MM2` 값을 시편의 단면적(mm²)으로 설정합니다. 현재 기본값은 `100`입니다. 응력은 다음 식으로 계산하며, N/mm²는 MPa와 같습니다.

```text
stress_MPa = force_N / SPECIMEN_AREA_MM2
```

기준응력은 `REFERENCE_STRESS_MPA`에서 설정하며 현재 값은 `6 MPa`입니다. 이 값보다 큰 응력 데이터의 개수를 출력합니다.

### 실행 방법

프로젝트 폴더에서 PowerShell을 열고 실행합니다.

```powershell
.\.venv\Scripts\python.exe load_analyzer.py
```

### 출력

콘솔에 유효 데이터 수, 제외한 행 수, 최대하중과 해당 시간, 최대응력, 기준응력 초과 데이터 수를 표시합니다. 시간-응력 그래프는 점과 선으로 그리고 최대응력점에 값과 시간을 표시해 `stress_plot.png`로 저장합니다. 그래프의 축 이름은 `time(s)`와 `stress (mpa)`입니다.

### 오류 및 제외 규칙

- `time_s` 또는 `force_N` 열이 없으면 필요한 열 이름을 표시하며 `ValueError`로 중단합니다.
- 두 열 중 값이 빈칸이거나 숫자가 아니면 CSV의 원래 행 번호(헤더 포함), 열 이름, 문제 값을 표시하고 해당 행을 계산과 그래프에서 제외합니다.
- 유효한 데이터가 하나도 없으면 안내를 출력하고 계산과 그래프 생성을 중단합니다.