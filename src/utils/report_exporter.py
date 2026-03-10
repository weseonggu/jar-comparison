import csv
from datetime import datetime
from pathlib import Path

from src.models.comparison_result import ComparisonResult


def export_csv(result: ComparisonResult, dest_path: str) -> None:
    """비교 결과를 CSV 파일로 내보낸다."""
    with open(dest_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["구분", "파일 경로", "운영 크기", "로컬 크기", "상태"])

        for entry in result.missing_in_local:
            writer.writerow(["누락(운영→로컬)", entry.path, entry.size_str(), "-", "운영에만 존재"])

        for remote_e, local_e in result.modified_files:
            writer.writerow([
                "내용 변경", remote_e.path,
                remote_e.size_str(), local_e.size_str(), "내용 다름"
            ])

        for entry in result.local_only:
            writer.writerow(["로컬 Only", entry.path, "-", entry.size_str(), "로컬에만 존재"])


def export_html(result: ComparisonResult, dest_path: str) -> None:
    """비교 결과를 HTML 리포트로 내보낸다."""
    now = result.compared_at.strftime("%Y-%m-%d %H:%M:%S")

    def _rows_missing() -> str:
        rows = []
        for e in result.missing_in_local:
            rows.append(
                f"<tr class='missing'><td>누락</td><td>{e.path}</td>"
                f"<td>{e.size_str()}</td><td>-</td><td>운영에만 존재</td></tr>"
            )
        return "\n".join(rows)

    def _rows_modified() -> str:
        rows = []
        for re, le in result.modified_files:
            rows.append(
                f"<tr class='modified'><td>변경</td><td>{re.path}</td>"
                f"<td>{re.size_str()}</td><td>{le.size_str()}</td><td>내용 다름</td></tr>"
            )
        return "\n".join(rows)

    def _rows_local_only() -> str:
        rows = []
        for e in result.local_only:
            rows.append(
                f"<tr class='local'><td>로컬 Only</td><td>{e.path}</td>"
                f"<td>-</td><td>{e.size_str()}</td><td>로컬에만 존재</td></tr>"
            )
        return "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>JAR 비교 리포트</title>
<style>
body {{ font-family: 'Malgun Gothic', sans-serif; padding: 20px; }}
h1 {{ color: #2c3e50; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 13px; }}
th {{ background: #2c3e50; color: white; }}
tr.missing {{ background: #ffeaea; }}
tr.modified {{ background: #fff3cd; }}
tr.local {{ background: #e8f5e9; }}
.summary {{ background: #f8f9fa; padding: 12px; border-radius: 4px; margin-bottom: 16px; }}
</style>
</head>
<body>
<h1>JAR 비교 리포트</h1>
<div class="summary">
  <b>비교 일시:</b> {now}<br>
  <b>로컬 JAR:</b> {result.local_jar_path}<br>
  <b>운영 JAR:</b> {result.remote_jar_path}<br>
  <b>요약:</b> {result.summary}
</div>
<table>
<thead><tr><th>구분</th><th>파일 경로</th><th>운영 크기</th><th>로컬 크기</th><th>상태</th></tr></thead>
<tbody>
{_rows_missing()}
{_rows_modified()}
{_rows_local_only()}
</tbody>
</table>
</body>
</html>"""

    Path(dest_path).write_text(html, encoding="utf-8")
