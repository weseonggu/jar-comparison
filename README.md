# JAR Comparison Tool

로컬 빌드 JAR 파일과 운영 서버 JAR 파일을 비교하여 누락·변경된 파일을 사전에 검출하는 GUI 도구입니다.

## 기능

- **누락 파일 검출**: 운영 JAR에는 있지만 로컬 JAR에 없는 파일 목록 표시
- **변경 파일 검출**: 양쪽에 모두 존재하지만 내용이 다른 파일 목록 표시
- **Diff 뷰어**: 변경된 파일의 내용을 좌우 분할 화면으로 비교
- **다중 접속 방식**: SFTP / FTP / 로컬 경로(네트워크 드라이브) 지원
- **접속 정보 저장**: 운영 서버 접속 정보를 암호화하여 로컬에 저장
- **리포트 내보내기**: 비교 결과를 CSV 또는 HTML 파일로 저장

## 요구사항

- Python 3.11 이상
- Windows 10/11 (64bit)

---

## 실행 방법 (exe 단독 실행)

Python 설치 없이 바로 실행할 수 있는 단독 실행 파일입니다.

1. `dist/JAR-Comparison-Tool.exe` 파일을 원하는 위치에 복사합니다.
2. 파일을 더블클릭하여 실행합니다.

> **참고**: 처음 실행 시 Windows 보안 경고가 표시될 수 있습니다.
> `추가 정보` → `실행` 을 클릭하면 정상 실행됩니다.

---

## exe 빌드 (개발자용)

소스 코드를 수정한 후 새로 exe를 빌드하려면 아래 과정을 따릅니다.

### 1. 가상 환경 준비

```bash
python -m venv venv
```

**Windows (cmd)**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell)**
```powershell
venv\Scripts\Activate.ps1
```

> PowerShell 실행 정책 오류 시:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 빌드 실행

```bash
python -m PyInstaller build.spec --clean
```

빌드 완료 후 `dist/JAR-Comparison-Tool.exe` 파일이 생성됩니다.

---

## 소스에서 직접 실행 (개발 환경)

### 1. 저장소 클론

```bash
git clone <repository-url>
cd jar-comparison
```

### 2. 가상 환경 생성

```bash
python -m venv venv
```

### 3. 가상 환경 활성화

**Windows (cmd)**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell)**
```powershell
venv\Scripts\Activate.ps1
```

> PowerShell에서 실행 정책 오류가 발생하면 아래 명령어를 먼저 실행하세요.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. 의존성 설치

```bash
pip install -r requirements.txt
```

### 5. 앱 실행

```bash
python main.py
```

### 6. 가상 환경 비활성화 (사용 종료 후)

```bash
deactivate
```

---

## 사용 방법

1. **로컬 JAR 선택**: `[파일 선택]` 버튼으로 로컬 빌드 JAR 파일을 선택합니다.
2. **운영 서버 설정**: 접속 방식(SFTP / FTP / 로컬 경로)을 선택하고 접속 정보를 입력합니다.
3. **JAR 목록 조회**: `[목록 조회]` 버튼으로 운영 서버의 JAR 파일 목록을 불러옵니다.
4. **비교 실행**: `[비교 실행]` 버튼(`F5`)을 클릭합니다.
5. **결과 확인**: 탭별로 누락·변경·로컬Only 파일을 확인합니다.
6. **Diff 보기**: 변경된 파일 행을 더블클릭하면 상세 Diff 뷰어가 열립니다.
7. **리포트 저장**: `[리포트 내보내기]`(`Ctrl+E`)로 CSV 또는 HTML 파일로 저장합니다.

---

## 프로젝트 구조

```
jar-comparison/
├── main.py                          # 애플리케이션 진입점
├── requirements.txt                 # 운영 의존성
├── requirements-dev.txt             # 개발 의존성 (pytest 포함)
│
├── src/
│   ├── models/                      # 데이터 모델
│   │   ├── jar_entry.py
│   │   ├── comparison_result.py
│   │   └── connection_config.py
│   ├── core/                        # 비교 핵심 로직
│   │   ├── jar_reader.py
│   │   ├── jar_comparator.py
│   │   └── diff_engine.py
│   ├── remote/                      # 서버 접근 핸들러
│   │   ├── base_handler.py
│   │   ├── sftp_handler.py
│   │   ├── ftp_handler.py
│   │   └── local_mount_handler.py
│   ├── utils/                       # 공통 유틸리티
│   │   ├── config_manager.py
│   │   ├── crypto_utils.py
│   │   ├── report_exporter.py
│   │   └── temp_file_manager.py
│   └── ui/                          # GUI 화면
│       ├── main_window.py
│       ├── connection_panel.py
│       ├── result_table.py
│       ├── diff_dialog.py
│       ├── settings_dialog.py
│       └── resources/styles/main.qss
│
└── tests/
    ├── create_fixtures.py
    ├── test_jar_reader.py
    ├── test_jar_comparator.py
    └── test_diff_engine.py
```

---

## 테스트 실행

가상 환경 활성화 후 아래 명령어를 실행합니다.

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

---

## 기술 스택

| 항목 | 버전 |
|------|------|
| Python | 3.11+ |
| PyQt6 | 6.6+ |
| paramiko | 3.4+ |
| cryptography | 42.0+ |
