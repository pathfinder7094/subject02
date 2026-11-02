# AI 사용 기록

허용 범위는 개념 질문과 자신이 작성한 코드의 디버깅입니다. 과제 함수의 정답이나 전체 구현을 대신 생성하게 해서는 안 됩니다. 먼저 현재 단계 검사를 실행하세요.

사용하지 않았다면 아래에 사용하지 않았다고 적습니다. 사용했다면 질문마다 기록합니다. API 키, 개인 이메일, 실제 회사 데이터는 입력하지 않습니다.

| 구분 | 질문 요약 | 공유한 자기 코드와 오류 범위 | 이해한 내용 | 직접 수정하고 검증한 결과 |
|---|---|---|---|---|
| 개념 또는 디버깅 | 작성 | 작성 | 작성 | 작성 |
| 기록 방식 설정 | 앞으로 질문에 답할 때 이 기록도 함께 작성해 달라고 요청함 | 없음 | 향후 AI 도움을 제공할 때마다 이 문서에 기록함 | 해당 없음 |
| 개발 도구 설정 | `uv run --frozen python main.py check ...` 다섯 명령을 VS Code에서 디버깅할 `launch.json` 구성 요청 | 없음 | VS Code 디버거에서 프로젝트 `.venv` Python으로 각 `check` 인자를 실행함 | `.vscode/launch.json`에 search, chain, history, stream, challenge 구성 추가 |
| 개념 | `RunnableParallel` 뒤에 `|`로 Runnable을 연결하고 `return`하는 이유 질문 | `main.py`의 `build_context_chain` 반환 부분 | `|`는 LangChain Runnable을 순차 연결하며, 전체 체인을 반환하면 호출부에서 `.invoke()`로 실행할 수 있음. `with_config(run_name=...)`는 추적 이름을 지정함 | 코드 변경 및 별도 검증 없음 |
| 개념 | 파이프라인에서 `yield`를 쓰는 효과와 `return`과의 차이 질문 | `build_context_chain`의 체인 반환 문맥 | `return`은 Runnable 체인 자체를 반환하지만, `yield`가 들어간 함수는 generator를 반환하므로 직접 `.invoke()`할 수 없음. 결과 스트리밍은 Runnable의 `.stream()` 사용 | 코드 변경 및 별도 검증 없음 |
| 디버깅 | LangChain `TraceHandler` 구현 방법 질문 | `main.py`의 `TraceHandler` 콜백과 `stream_answer`의 콜백 연결 문맥 | 콜백에서 run 시작·종료·오류·토큰 이벤트를 받아 기록하며, `run_id`로 실행을 구분함. 민감한 원문 대신 메타데이터만 기록하도록 함 | `error_type`과 텍스트 청크 수 계산을 구현함. `check stream`에서 run별 시간/오류 기록과 빈 청크 검사는 통과했으나 전체 스트림 trace 검사는 다른 미완성 항목으로 통과하지 못함 |
| 개념 | 파이썬 예외 클래스 이름을 얻는 방법 질문 | `TraceHandler._finish()`의 오류 기록 문맥 | `type(error).__name__`은 `ValueError` 같은 예외 클래스명만 반환하고, `str(error)`는 예외 메시지를 반환함. 민감 정보 노출을 피하려면 클래스명만 기록할 수 있음 | 별도 코드 변경 및 검증 없음 |

도구와 모델 이름:

AI의 설명이 틀렸거나 그대로 적용하지 않은 부분:

최종 코드와 설명을 스스로 설명할 수 있는지 확인:
