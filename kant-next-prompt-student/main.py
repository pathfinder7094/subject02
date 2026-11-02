"""KANT NEXT DevDesk. 정책 프롬프트부터 _todo(...) 한 곳씩 바꾸세요.

시작: uv run --frozen python main.py demo
확인: uv run --frozen python main.py check policy
실제 호출: uv run --frozen python main.py run policy --live

반복문, 파일 처리, 로그 형식은 준비되어 있습니다.
_todo(...)를 값, 조건식 또는 함수 호출로 바꾸면 해당 부분이 실행됩니다.
설명 주석에는 선택 이유를 1~2문장 남기세요. 별도 문서는 만들지 않습니다.
"""
import copy
import hashlib
import json
import re
import time

from jsonschema import Draft202012Validator, ValidationError

import support
# invalid_json, schema_error, blank_answer, unknown_source, duplicate_source, unsupported_answer
ERROR_MESSAGES= {
                "invalid_json" : "JSONDecodeError 에러 발생. json 문법에 맞지 않는 데이터가 입력되거나 laod 되었습니다. ",
                "schema_error" : "schema 에러가 발생하였습니다.",
                "blank_answer" : "반환할 answer의 값이 없습니다.",
                "unknown_source" : "찾고자 하는 source_id가 범위를 벗어나 존재하지 않습니다.",
                "duplicate_source" : "source_id가 중복값으로 존재합니다.",  
                "unsupported_answer" : "사용자가 전달할 답변은 지원 범위를 벗어납니다."   
                }


CATEGORY_VALUES = tuple(sorted({
    document["category"]
    for document in support.read_json(support.DATA / "documents.json")
}))


def _todo(label):
    raise NotImplementedError(label)


# 필수 1 / 정책 프롬프트. 문자열 두 개를 작성합니다.
def build_instructions(documents, variant):
    if variant not in {"baseline", "reasoning"}:
        raise ValueError("variant는 baseline 또는 reasoning입니다.")
    # 이유: Few-shot과 Self-Consistency는 각각 어떤 상황에 쓰는지,
    # 이번에는 왜 Reasoning을 쓰는지와 한계를 2~3문장으로 적으세요.
    # few-shot 같은 경우 특정 라벨에 대한 답변의 예시를 제시하여 응답 답변의 가이드라인으로 정제된 표현을 하고자 할때 사용
    # self-consistency 답변의 호출을 여러번 실행하여 환각으로 오답의 가능성을 줄이고자 함. 머신러닝의 앙상블 기법과 유사하다고 생각함 
    
# KANT NEXT 개발지원팀은 사내 문서와 티켓을 찾아 반복 문의에 답하는 DevDesk를 개선하고 있습니다. 근거가 있을 때 안내하고, 확인할 수 없는 내용은 담당자에게 연결하는 프로그램을 구현해 주세요.

# 문서, 티켓, 이미지는 동작 확인을 위한 테스트용 데이터입니다. 답변은 제공 정책과 조회 결과에 근거해야 합니다.

    policy ="사내지원팀의 담당자로써 사내 문서와 티켓을 찾아 반복 문의를 답하는 역할을 가지고 있습니다.\
        사내 직원들의 문의에 대해 근거가 있을 경우에는 안내하고 확인 할수 없을때는 담당자에게 연결하도록 하세요.\
        절대 비밀정보에 관해 답변을 해서는 아니되며, 비밀정보 누출에 대한 행위에 경고를 주세요." 
    if variant == "reasoning":
        policy += "답변이 제공 정책과 조회 결과에 근거하여 답변을 하였는지 체크를 하세요"
    corpus = json.dumps(sorted(documents, key=lambda item: item["doc_id"]),
                        ensure_ascii=False, sort_keys=True)
    return policy + "\n<reference_documents>\n" + corpus + "\n</reference_documents>"


# 필수 2 / 답변 검증과 수정. 스키마를 만든 뒤 값과 출처를 검사합니다.
def answer_format():
    # 스키마의 properties -> 타입 정의 
    # _todo("답변 검증과 수정: answer, source_ids, needs_human, category의 JSON Schema 속성 dict")
    properties = {
                    "answer" : { "type" : "string"},
                    "source_ids" : { "type" : "array", 
                                      "items" : {"type" : "string"}
                                    },
                    "needs_human" : { "type" : "boolean"}, 
                    "category" : {"type": "string", "enum": list(CATEGORY_VALUES)}
                 }
    schema = {"type": "object", "properties": properties,
              "required": ["answer", "source_ids", "needs_human", "category"],
              "additionalProperties": False}
    return {"format": {"type": "json_schema", "name": "devdesk_answer",
                       "strict": True, "schema": schema}}


def validate_answer(raw, known_ids):
    answer = json.loads(raw)
    schema = answer_format()["format"]["schema"]
    Draft202012Validator(schema).validate(answer)
    # 이유: 스키마를 통과해도 출처와 답변 본문을 따로 확인하는 이유를 적으세요.
    # answer 데이터가 전처리가 되지 않아서 데이터를 학습하거나 input data로 사용하기에 노이즈를 발생시킬수 있는 부분이라 예외처리를 함
    
    rules = [   
               (not answer["answer"].strip(), "blank answer"),
               (any(source_id not in known_ids for source_id in answer["source_ids"]), "unknown source_id"),
               (len(set(answer["source_ids"])) != len(answer["source_ids"]), "duplicate source_id"),
               ((not answer["source_ids"] and not answer["needs_human"]) or answer["category"] not in CATEGORY_VALUES, "unsupported answer requires human")
            ]
    
    for invalid, message in rules:
        if invalid:
            raise ValueError(message)
    return answer


def finish_answer(send, request, response, known_ids, events):
    request = copy.deepcopy(request)
    fallback = {"answer": "확인 가능한 답변을 만들지 못했습니다. 담당자 확인이 필요합니다.",
                "source_ids": [], "needs_human": True, "category": "general"}
    repair_used = False
    # 한 번 검사하고, 필요하면 한 번 수정한 뒤 같은 검사를 다시 합니다.
    for turn in range(2):
        if response is None:
            reason = "api_failure"
        elif response.get("status") == "round_limit":
            reason = "round_limit"
        elif response.get("status") != "completed":
            reason = "incomplete"
        elif support.has_refusal(response):
            reason = "refusal"
        else:
            try:
                answer = validate_answer(response["output_text"], known_ids)
                return {"answer": answer, "fallback_reason": None, "repair_used": repair_used}
            except (ValueError, ValidationError) as error:
                error_kind, field = support.validation_detail(error)
                events.append({"event": "validation_error", "repair_already_used": repair_used,
                               "error_kind": error_kind, "error_field": field})
                if turn == 1:
                    reason = "validation_failed"
                else:
                    # 종류: invalid_json, schema_error, blank_answer, unknown_source,
                    # duplicate_source, unsupported_answer. 종류에 맞게 안내를 만드세요.
                    # ERROR_MESSAGES["schema_error"]는 지정된 error_kind로 들어오지 않을때 default로 ERROR_MESSAGES["schema_error"]를 hint로 주입 

                    hint = ERROR_MESSAGES.get(error_kind, ERROR_MESSAGES["schema_error"])
                    repair_used = True
                    support.append_repair_input(request, response, hint)
                    response = send(request)
                    continue
        return {"answer": fallback, "fallback_reason": reason, "repair_used": repair_used}


# 필수 3 / 티켓 조회. 티켓 조회 조건과 모델에 돌려줄 값을 정합니다.
def tool_schema():
    # 힌트: 도구 호출 인자 스키마는 여기서 정의합니다. parameters는 object로 만들고,
    # ticket_id를 필수로 지정하며 추가 키를 금지하세요. ID 형식도 제한할 수 있습니다.
    
    parameters = { "type" : "object" ,
                   "properties" : {
                       
                       "ticket_id" : { 
                           "type" : "string",
                           "pattern" : "^IT-[0-9]{4}"
                           }
                        },
                    "required" : ["ticket_id"],
                    
                    "additionalProperties": False
                } 
          

    return {"type": "function", "name": "lookup_ticket", "strict": True,
            "description": "기존 티켓의 상태를 읽습니다. 티켓을 변경하지 않습니다.",
            "parameters": parameters}


def execute_tool(name, arguments, tickets):
    print ("schema checker" , name, tool_schema(), tool_schema()["name"])
    if name != tool_schema()["name"]:
        return {"ok": False, "error": "unknown_tool"}
    try:
        args = json.loads(arguments)
        # print(type({"dd":"ddd"}) , "type확인")
        print("타입체크", type(args) is dict ,type(args) ,"len(id)", len(args["ticket_id"])  )
        print("스키마필드 유무 체크 ", tool_schema().keys(),args.keys(), len(args.keys()) )

        # 힌트: 이 조건에서 파싱 결과가 dict인지, 키가 ticket_id 하나뿐인지 확인하세요.
        # 타입이 잘못됐거나 키가 빠지거나 추가된 경우에만 아래 ValueError를 발생시킵니다.
        if (type(args) is not dict or set(args) != {"ticket_id"} ) and (len(args.keys) ==0 and (tool_schema()["parameters"]["additionalProperties"] is True) ) : 
            print(type(args), len(args["ticket_id"]),"dddddd")
            raise ValueError("unexpected arguments")
        ticket_id = args["ticket_id"]
        if not isinstance(ticket_id, str) or not re.fullmatch(r"IT-[0-9]{4}", ticket_id):
            print(ticket_id)
            raise ValueError("invalid ticket_id")
    except (ValueError, TypeError):
        return {"ok": False, "error": "invalid_arguments"}
    if ticket_id not in tickets:
        return {"ok": False, "error": "not_found", "ticket_id": ticket_id}
    # 힌트: 테스트는 ticket_id 문자열이 아니라 tickets[ticket_id]의 티켓 dict를 기대합니다.
    # 원본을 보호하도록 반환 전에 사본을 만들어야 합니다.
    
    # dict는 단순히 기존의 딕셔너리를 값으로 감싸는게 아니라 기존 딕셔너리의 항목을 복사해서 새로운 딕셔너리를 만듬
    copy_ticket = dict(tickets[ticket_id])
    return {"ok": True, "ticket": copy_ticket }


def tool_roundtrip(send, request, tickets, events):
    request = copy.deepcopy(request)
    for _ in range(4):
        response = send(request)
        if response is None or response.get("status") != "completed" or support.has_refusal(response):
            return request, response
        output = response.get("output", [])
        # print("output", output)
        calls = [item for item in output if item.get("type") == "function_call"]
        if not calls:
            return request, response
        # 이유: 모델이 요청한 도구를 누가 실행하며 call_id를 왜 유지하는지 적으세요.
        # 힌트: 모델이 반환한 output(특히 reasoning과 function_call)을 통째로 다음 입력에 보존합니다.
        request["input"].extend(output)
        for call in calls:
            if not isinstance(call.get("call_id"), str) or not call["call_id"]:
                return request, {"status": "incomplete", "output": []}
            # print("debug---- call", call)
            result =execute_tool(call["name"], call["arguments"], tickets)
            events.append({"event": "tool_result", "name": call.get("name"),
                           "call_id": call["call_id"], "ok": result["ok"], "error": result.get("error")})
            request["input"].append({"type": "function_call_output",
                                    # 힌트: 요청한 function_call과 같은 call_id여야 모델이 결과와 호출을 연결합니다.
                                    "call_id": call["call_id"] ,
                                    "output": json.dumps(result, ensure_ascii=False)})
    return request, {"status": "round_limit", "output": []}


# 오류 화면 입력. 기존 텍스트 옆에 이미지 항목 하나를 추가합니다.
def image_content(question, image_path):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question is empty")
    content = [{"type": "input_text", "text": question}]
    if image_path is not None:
        # content.append(_todo("오류 화면 입력: input_image 항목. support.image_url(image_path), detail='high' 사용"))
        content.append(
             {
                 "type" : "input_image",
                 "image_url" : support.image_url(image_path), 
                 "detail" : "high"
             }
            )
    # 이유: 화면에서 본 오류와 실제 장애 원인을 구분해야 하는 이유를 적으세요.
    return content


# 호출 재시도. 반복과 기록은 준비되어 있습니다. 다시 시도할 조건을 작성합니다.
def call_with_retry(send, request, events, sleep=time.sleep):
    for attempt in range(1, 4):
        started = time.perf_counter()
        try:
            response = send(request)
        except support.TransportError as error:
            status = error.status_code
            print("error__status", status, "00000",error.kind)
            
            retryable =  ( error.kind in {"timeout", "connection"}
                           or (error.kind == "http" 
                                   and ( str(status) in {"408", "409", "429"} 
                                        or re.fullmatch(r"5\d{2}", str(status)) is not None)
                              )
            )
            #  _todo("호출 재시도: 다시 시도할 수 있고 아직 3번째 시도가 아닌지 판정하는 조건")
            # print(attempt, "attemp 확인")
            retry_now = ( attempt !=3 and retryable)
           
            delay = support.delay_for(attempt) if retry_now else 0
            support.append_attempt(events, attempt, started, error=error,
                                   retryable=retryable, wait_s=delay)
            if not retry_now:
                return None
            sleep(delay)
        else:
            support.append_attempt(events, attempt, started, response=response)
            return response
    # 이유: 출력 수정과 전송 재시도가 다른 이유를 적으세요.


# 사용량과 비용. 고정 입력을 연결하고, 토큰을 골라 비용을 계산합니다.
def cache_settings(documents, variant):

    print("documents  ---    ", documents)
    # instructions = _todo("사용량과 비용: 정책 프롬프트의 고정 지시문을 만드는 호출")

    instructions = build_instructions(documents, variant)
    fingerprint = hashlib.sha256(instructions.encode("utf-8")).hexdigest()[:16]
    # 같은 정책과 조건은 같은 키를 사용합니다. 질문이나 현재 시각을 섞지 않습니다.
    return {"instructions": instructions,
            "prompt_cache_key": f"kant-next-pe-{variant}-{fingerprint}"}


def usage_record(attempt, prices):
    response = attempt.get("response") or {}
    usage = response.get("usage") or {}
    details = usage.get("input_tokens_details") or {}
    it = usage.get("input_tokens")
    # _todo("사용량과 비용: usage에서 전체 입력 토큰 읽기. 없으면 None")
    ot = usage.get("output_tokens")
    # _todo("사용량과 비용: usage에서 전체 출력 토큰 읽기. 없으면 None")
    cached = details.get("cached_tokens")
    # _todo("사용량과 비용: details에서 캐시 읽기 토큰 읽기. 없으면 None")
    written = details.get("cache_write_tokens")
    reasoning = (usage.get("output_tokens_details") or {}).get("reasoning_tokens")
    support.validate_usage_counters(it, ot, cached, written, reasoning)
    estimate, assumption = None, None
    if it is not None and ot is not None and cached is not None:
        effective_write = written if written is not None else 0
        if it > prices["max_input_tokens"]:
            assumption = "input exceeds the supplied price tier; estimate unavailable"
        else:
            if written is None:
                assumption = "cache_write_tokens absent; assumed zero for estimate"
            ordinary = it - cached - effective_write
            #  _todo("사용량과 비용: 전체 입력에서 캐시 읽기와 쓰기를 뺀 일반 입력 수")
            # prices의 단가 키: input, cached, cache_write, output. 백만 토큰당 USD입니다.
            estimate = (ordinary * prices["input"] + cached * prices["cached"]
                        + effective_write * prices["cache_write"] + ot * prices["output"]) / 1_000_000
            # _todo("사용량과 비용: 일반 입력, 캐시 읽기, 캐시 쓰기, 출력 비용의 합을 백만으로 나누는 식")
    observation = "unavailable" if cached is None else ("hit" if cached > 0 else "miss")
    # _todo("사용량과 비용: cached가 None/양수/0일 때 unavailable/hit/miss를 고르는 식")
    # 이유: 캐시와 추론 토큰을 왜 중복 계산하지 않는지,
    # 두 요청의 비용이나 지연 차이를 전부 캐시 효과라 할 수 없는 이유를 적으세요.
    return support.pack_usage_record(attempt, response, prices, it, ot, cached, written,
                                     reasoning, observation, estimate, assumption)


# 전체 기능 연결. 준비된 실행 순서에 앞 함수들을 연결합니다.
def run_pipeline(send, question, documents, tickets, variant="reasoning",
                 image_path=None, prices=None, sleep=time.sleep):
    prices = support.load_prices() if prices is None else prices
    events = []
    started = time.perf_counter()
    #  _todo("전체 기능 연결: cache_settings 호출")
    settings =cache_settings(documents, variant)
    request = support.base_request(settings["instructions"], question, variant)
    request.update(settings)
    #  _todo("전체 기능 연결: 답변 형식을 만드는 함수 호출")
    request["text"] = answer_format()
    # _todo("전체 기능 연결: 도구 규격을 만드는 함수 호출")
    request["tools"] = [tool_schema()]
    request["parallel_tool_calls"] = False
    # _todo("전체 기능 연결: 질문과 image_path로 입력을 만드는 함수 호출")
    request["input"][0]["content"] = image_content(question, image_path)
    def reliable_send(current_request):
        return call_with_retry(send, current_request, events, sleep=sleep)
    #  _todo("전체 기능 연결: tool_roundtrip에 reliable_send, request, tickets, events 전달")
    final_request, response = tool_roundtrip(reliable_send, request, tickets, events)
    # _todo("전체 기능 연결: finish_answer에 reliable_send, final_request, response, 문서 ID 집합, events 전달")
    result = finish_answer(reliable_send, final_request, response, {doc["doc_id"] for doc in documents}, events)
    result["tool_calls"] = sum(event["event"] == "tool_result" for event in events)
    result["logs"] = [usage_record(event, prices) if event["event"] == "api_attempt" else event
                      for event in events]
    result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 3)
    return result


# 선택 심화 1. 골격 없이 두 대상의 프롬프트와 비교 함수를 설계합니다.
def build_audience_instructions(documents, variant, audience):
    """newcomer/operator 지시를 직접 설계. 다른 모드는 ValueError.

    공통 정책을 유지하고, 용어 풀이와 처리 순서를 대상에 맞추세요.
    """
    raise NotImplementedError("선택 심화: build_audience_instructions를 작성하세요.")


def audit_audience_pair(newcomer, operator):
    """같은 질문의 유효한 답변 dict 두 개를 비교합니다.

    반환: same_policy(bool), different_explanation(bool), issues(list[str]).
    category, needs_human, source_ids 집합은 같아야 합니다.
    answer는 앞뒤 공백을 뺀 값이 달라야 합니다.
    issues에는 다른 정책 필드명과 필요하면 same_explanation을 담으세요.
    본문이 다르다는 사실만으로 설명이 적절하다고 결론내리지는 마세요.
    """
    raise NotImplementedError("선택 심화: audit_audience_pair를 작성하세요.")


if __name__ == "__main__":
    import sys
    raise SystemExit(support.cli(sys.modules[__name__]))
