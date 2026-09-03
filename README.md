# Lyrics Thread

Hooktheory의 chord thread처럼, 가사를 **문장 전개 구조**로 정규화해서 비교하는 실험적 웹앱이다.

예:

- `네가 돌아오면 나는 기다릴게`
- `네가 웃으면 나는 노래할게`

둘 다 `조건 → 반응 / [A]가 X하면 [B]는 Y` Thread로 묶인다.

## 기능

- 한국어 / 일본어 / 영어 기본 문장형 분석
- 가사 행 단위 Thread 표시
- 곡명 / 아티스트 / 섹션과 함께 SQLite 저장
- 입력 문장과 동일한 Thread를 가진 저장 가사 검색
- Thread 사용 빈도 통계

현재는 구조가 명확한 문장형만 규칙 기반으로 잡는 MVP다. 다음 단계에서 형태소/구문 분석과 임베딩을 추가하면 더 자유로운 가사도 묶을 수 있다.

## 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:5050` 접속.

## 테스트

```bash
python -m unittest discover -s tests -v
```
