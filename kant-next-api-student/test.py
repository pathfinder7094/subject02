import httpx
from bs4 import BeautifulSoup


import support
from pathlib import Path

def test_github_html_parsing():
    print("--- GitHub API HTML 파싱 테스트 시작 ---")
    
    # 1. 실제 요청 전송 (필요시 헤더 추가 가능)
    response = httpx.get("https://api.github.com/repos/astral-sh/uv/releases", timeout=10)
    response.raise_for_status()

    print("reponse.links 확인" , response.links)
    # 2. BeautifulSoup 파싱 및 출력
    soup = BeautifulSoup(response.text, "html.parser")
    print("bs all (일부 출력):", str(soup)[:200] + "...")
    print("-" * 76)

    
    
    # 타이틀 출력 검증
    if soup.title:
        title_text = soup.title.get_text(strip=True)
        print("Title:", title_text)
    else:
        print("Title 태그가 존재하지 않습니다.")




# collect_releases에 사용하기 위한 함수정의 : 폴더 내 생성할 파일 존재 유무 체크후 함수를 실행하기 전  clean 작업으로 작업상태 초기화 
def dir_clean_json(target_path, NameList=None, clean_all=False):
    dir_path = Path(target_path)
    if not dir_path.exists():
        return
        
    if NameList:
        # 리스트에 있는 정확한 파일 이름들만 삭제
        for filename in NameList:
            file_path = dir_path / filename
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
    elif clean_all:
        # 리스트가 없고 clean_all=True면 폴더 내 모든 json 삭제
        for f in dir_path.glob("*.json"):
            f.unlink()




def dir_clean_execute(path):

    output_dir = Path("temp") / path
    RAW_PAGE_FILE_NM="raw_pages.json"
    COLLECT_REPORT_FILE_NM="collection_report.json"

    output_dir.mkdir(parents=True, exist_ok=True)

    support.dir_clean_json(output_dir, 
                           NameList=[RAW_PAGE_FILE_NM,COLLECT_REPORT_FILE_NM], 
                           clean_all=False)

if __name__ == "__main__":
    test_github_html_parsing()
    #dir_clean("git_release")