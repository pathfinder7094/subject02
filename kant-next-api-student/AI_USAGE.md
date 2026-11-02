# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 디버깅에만 사용할 수 있습니다. 사용하지 않았다면 아래에 `사용하지 않음`이라고 적습니다. 사용량을 늘릴 필요는 없습니다.

| 허용되는 도움 | 예시 |
|---|---|
| 개념 이해 | HTTP 404와 422의 차이, await의 의미를 다른 예시로 설명해 달라고 질문 |
| 자신의 코드 디버깅 | 직접 작성한 짧은 함수와 오류를 보여 주고 원인과 확인 방법을 질문 |

과제 전체 풀이, TODO의 완성 코드, 참고 답안을 요청하지 않습니다. 디버깅 답변도 이해한 원인과 수정 내용을 자신의 말로 기록하고 다시 실행합니다. API 키, `.env`와 인증 헤더를 질문에 포함하지 않습니다.

## 사용 여부

- 사용 여부: 사용함
- 사용한 도구: Copilot

## 도움 기록

도움을 받은 건마다 표의 행을 추가합니다. 대화 전문보다 질문과 직접 확인한 결과를 구체적으로 적습니다.

| 단계/함수 | 직접 시도한 내용과 문제 | 질문 요약 | 받은 설명 | 내가 수정하거나 확인한 내용 | 재실행 결과 |
|---|---|---|---|---|---|
| 기록 형식 | 해당 없음 | 앞으로 질문하는 내용을 이 파일 형식에 맞춰 업데이트해 달라고 요청 | 파일의 기록 형식을 확인했고, 이후 질문에서 받은 도움을 이 표에 반영하기로 함 | 사용 여부와 도구를 표시하고 이 요청을 기록함 | 해당 없음 |
| 파이썬 HTTP 요청 개념 | 해당 없음 | 파이썬으로 페이지를 크롤링하거나 curl처럼 응답 JSON을 받는 예시 요청 | JSON API는 HTTP 클라이언트의 응답을 JSON으로 파싱하고, HTML 페이지는 HTML 파서로 필요한 요소를 추출한다고 설명. curl은 파이썬 라이브러리가 아닌 명령줄 도구임 | 아직 직접 수정하거나 실행한 내용 없음 | 아직 재실행하지 않음 |
| `dir_clean_execute()` | 출력 경로가 빈 문자열로 설정되어 있었음 | `output_dir`을 임시 디렉토리를 만드는 상대 경로로 설정 요청 | `Path("temp") / "github_releases"`처럼 현재 작업 디렉토리 기준 상대 경로를 사용할 수 있다고 설명 | `output_dir`을 해당 경로로 변경하고 기존 `mkdir(parents=True, exist_ok=True)`를 유지함 | 아직 재실행하지 않음 |
| `bs4` 모듈 설치 | `ModuleNotFoundError: No module named 'bs4'` 발생 | MCP가 필요한 이유와 uv 설치 명령 요청 | MCP는 이 질문에 필요하지 않으며, 프로젝트가 uv를 사용하고 `pyproject.toml`에서 의존성을 관리하므로 `uv add --dev beautifulsoup4`로 추가하면 됨 | 아직 명령을 실행하지 않음 | 아직 확인하지 않음 |
| VS Code Python 디버깅 | `uv run --frozen python app.py run documents`로 실행하는 프로젝트 | uv 환경에서 위 명령을 디버깅하도록 launch 설정 요청 | uv가 프로젝트 `.venv`를 관리하므로 해당 가상환경의 Python 인터프리터로 `app.py`를 직접 디버깅할 수 있음. 실행 인자는 `run documents` | `.vscode/launch.json`에 인터프리터, 작업 폴더, 인자를 설정함 | 설정 파일 JSON 형식만 확인함 |
| VS Code 문서 검사 디버깅 | 기존 설정이 `run documents`를 인자로 사용함 | 실행 명령을 `uv run --frozen python app.py check documents`로 변경 요청 | `app.py`에 `check` 명령과 `documents` 단계가 등록되어 있음 | launch 설정 이름과 인자를 `check documents`로 변경함 | JSON 및 인자 `check documents`, Python 인터프리터 경로 확인 완료 |
| 파이썬 리스트 교집합 | 두 리스트에서 공통 원소가 있는지 확인하는 방법을 질문함 | 리스트 간 교집합에 원소가 있는지 확인하는 방법 질문 | `set(list1) & set(list2)`의 결과가 비어 있지 않은지 조건문으로 검사할 수 있고, 해시 불가능한 원소에는 `any(x in list2 for x in list1)`을 쓸 수 있다고 설명 | 코드에 적용하거나 실행한 내용 없음 | 아직 재실행하지 않음 |
| `call_model_once()` 출처 ID 검사 | `reply.source_ids`와 `selected_ids` 검사 코드가 있음 | 차집합으로 공통되지 않는 원소를 확인하는 방법 질문 | `set(reply.source_ids) - selected_ids`가 비어 있지 않으면 응답에 선택되지 않은 ID가 있다는 뜻이라고 설명 | 기존 조건식이 같은 차집합 검사를 하고 있음을 확인함 | 코드 재실행은 하지 않음 |
| 비동기 `await` | `call_model_once()`와 `query_with_retry()`에 `await`가 있음 | 파이썬의 `await` 및 비동기 대기 상태 질문 | 비동기 작업의 완료를 기다리는 동안 이벤트 루프에 다른 작업을 처리할 기회를 주며, `await` 자체가 새 작업을 병렬 실행하는 것은 아니라고 설명 | 코드 수정 없이 해당 사용 위치를 확인함 | 코드 재실행은 하지 않음 |
| `admit_query()` 키워드 전용 인자 | 함수 정의가 `admit_query(state, now, *, limit=30, window=60)`임 | 매개변수 사이의 `*`가 의미하는 것 질문 | `*` 뒤의 `limit`, `window`는 키워드 인자로만 전달할 수 있고, 생략 시 기본값을 사용한다고 설명 | 코드 수정 없이 함수 시그니처를 확인함 | 코드 재실행은 하지 않음 |
| 함수 정의의 단독 `*` | `admit_query(state, now, *, limit=30, window=60)`에서 `*`의 의미를 재확인함 | `*` 인자가 무엇인지 질문 | 단독 `*`는 인자 자체가 아니라 구분 기호이며, 뒤의 매개변수들을 키워드 전용으로 지정한다고 설명. `*args`와 구별됨 | 코드 수정 없음 | 해당 없음 |
| `admit_query()` 키워드 전용 제한값 | `limit`, `window`가 기본값을 가짐 | 키워드 전용 구분자 `*`가 왜 필요한지, 생략 가능한지 질문 | 생략 가능하며, 생략하면 두 매개변수에 위치 인자도 허용됨. `*`를 두면 호출할 때 `limit=...`, `window=...`라고 이름을 밝혀 인자 순서 혼동을 막을 수 있음 | 코드 수정 없음 | 해당 없음 |
| `admit_query()` 위치 인자 호출 | 시그니처에 `limit=30`, `window=60`이 있음 | 단독 `*`를 제거하면 `admit_query(state, now, 10, 30)` 호출이 가능한지 질문 | 가능함. `*`가 없으면 세 번째와 네 번째 위치 인자가 각각 `limit`, `window`에 전달됨 | 코드 수정 없음 | 해당 없음 |
| `admit_query()` 시작 시각 검사 | 초기 상태에서 `state["start"]`가 `None`일 수 있음 | `now - state["start"]`에서 정수와 `None`을 뺄 수 있는지 질문 | 불가능하며 실행하면 `TypeError`가 발생함. `state["start"] is None or ...`처럼 먼저 검사하면 `or`의 단락 평가로 None일 때 오른쪽 뺄셈을 건너뛸 수 있음 | 코드 수정 없음 | 해당 없음 |
| 요청 제한 상태와 시계 | `support.create_service()`에서 `application.state.rate`를 만들고 `/query`에서 `module.admit_query()`를 호출함 | `now`의 타입과 출처, 요청 제한 상태가 어디서 초기화·관리되는지 질문 | 기본 `clock=time.monotonic`의 반환값은 단조 증가하는 초 단위 실수이며 호출 때마다 `/query`에서 전달됨. 제한 상태는 앱 생성 시 `{"start": None, "count": 0}`으로 초기화되어 해당 프로세스 메모리에 유지됨. 현재 `admit_query()`에는 `support.todo()` 미완성 부분도 남아 있음 | 호출 경로와 초기화 위치를 코드에서 확인함 | 실행 검증은 하지 않음 |
| FastAPI 앱 상태와 `module` | `support.py`의 앱 생성 함수가 `module` 객체를 매개변수로 받고 요청 제한 상태를 초기화함 | `application.state.rate`가 어디서 관리되는지, `module`이 전역 객체인지 질문 | `application.state.rate`는 `create_service()`가 생성한 FastAPI 애플리케이션 객체에 저장되는 앱별 메모리 상태이며, `/query`에서 같은 딕셔너리를 `admit_query()`에 전달함. `module`은 `app.py`의 `sys.modules[__name__]`로 전달한 모듈 객체로, 함수/모델을 `module.admit_query`처럼 찾아 쓰기 위한 참조이지 요청 제한 상태를 보관하는 전역 싱글톤이 아님 | `create_app()`에서 `create_service()`로 넘기는 경로와 앱 상태 초기화 코드를 확인함 | 실행 검증은 하지 않음 |
| FastAPI와 `admit_query()` | 요청 핸들러가 `module.admit_query()`를 호출함 | FastAPI에서 함수 정의나 설명, 사용 예제를 볼 수 있는지 질문 | `admit_query()`는 FastAPI 내장 함수가 아니라 프로젝트가 `app.py`에 정의한 요청 제한 도우미 함수임. FastAPI 문서는 앱 상태와 라우트 작성법을 참고하고, 이 함수의 구체 동작은 프로젝트 코드에서 확인한다고 설명 | 코드 변경이나 실행 없이 관련 위치를 안내함 | 해당 없음 |
| FastAPI `application.state` 문서 | 제한 상태가 `application.state.rate`에 저장됨 | `application.state.rate`를 FastAPI 문서에서 확인할 수 있는지 질문 | 확인 가능함. FastAPI 앱은 Starlette 기반이므로 `app.state`의 일반적인 사용은 Starlette 애플리케이션 문서에서 다루며, `rate`라는 속성과 그 딕셔너리 구조는 프로젝트가 추가한 값임 | 공식 문서의 범위와 프로젝트 고유 속성의 차이를 정리함 | 해당 없음 |
