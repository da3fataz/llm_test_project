# test_prompt_manager.py
import os
import yaml
import sys

# 현재 디렉토리 기준으로 agents 폴더 경로 추가
sys.path.append(".")  # 현재 디렉토리 추가

# prompt_manager 모듈 임포트
from agents.prompt_manager import PromptManager

def main():
    print("======= PromptManager 테스트 =======")
    
    # PromptManager 인스턴스 생성
    manager = PromptManager(prompts_dir="prompts")
    
    # 1. nc_judge.yaml 파일 직접 로드
    print("\n------- NC Judge YAML 파일 로드 -------")
    nc_judge_path = os.path.join("prompts", "nc_judge.yaml")
    
    if not os.path.exists(nc_judge_path):
        print(f"Error: File not found: {nc_judge_path}")
        return
    
    try:
        # 파일을 직접 열어서 내용 확인
        with open(nc_judge_path, 'r', encoding='utf-8') as f:
            print(f"파일 '{nc_judge_path}'를 읽고 있습니다...")
            raw_content = f.read()
            print(f"파일 크기: {len(raw_content)} bytes")
        
        # PromptManager를 통해 로드
        print("\nPromptManager를 통해 로드 중...")
        yaml_data = manager.load_prompt_file(nc_judge_path)
        
        # 주요 정보 출력
        print(f"YAML 타입: {type(yaml_data)}")
        
        if "input_variables" in yaml_data:
            print(f"\n입력 변수: {yaml_data['input_variables']}")
        
        if "messages" in yaml_data:
            messages = yaml_data["messages"]
            print(f"\n메시지 수: {len(messages)}")
            
            for i, msg in enumerate(messages):
                print(f"\n메시지 {i+1}:")
                print(f"  역할: {msg.get('role', 'unknown')}")
                content = msg.get('content', '')
                preview = content[:100] + '...' if len(content) > 100 else content
                print(f"  내용: {preview}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 2. evaluation_criteria.yaml 파일 로드
    print("\n------- 평가 기준 파일 로드 -------")
    criteria_path = os.path.join("prompts", "evaluation_criteria.yaml")
    
    if not os.path.exists(criteria_path):
        print(f"Error: File not found: {criteria_path}")
        return
    
    try:
        # PromptManager를 통해 로드
        criteria_data = manager.load_prompt_file(criteria_path)
        
        # 주요 정보 출력
        print(f"YAML 타입: {type(criteria_data)}")
        
        # 각 섹션 확인
        for section, items in criteria_data.items():
            print(f"\n섹션: {section} ({len(items)}개 항목)")
            
            for i, item in enumerate(items[:3]):  # 처음 3개만 보여줌
                print(f"  항목 {i+1}: {item['name']} (가중치: {item['weight']})")
                print(f"    설명: {item['description']}")
            
            if len(items) > 3:
                print(f"    ... 외 {len(items)-3}개 항목")
        
        # get_evaluation_criteria 메서드 테스트
        print("\nget_evaluation_criteria 메서드 테스트:")
        
        # 기본 기준
        default_criteria = manager.get_evaluation_criteria()
        print(f"\n기본 평가 기준 ({len(default_criteria)}개):")
        for i, criterion in enumerate(default_criteria):
            print(f"  {i+1}. {criterion['name']}: {criterion['description']} (가중치: {criterion['weight']})")
        
        # 뉴스 큐레이션 기준
        news_criteria = manager.get_evaluation_criteria("news_curation")
        print(f"\n뉴스 큐레이션 평가 기준 ({len(news_criteria)}개):")
        for i, criterion in enumerate(news_criteria):
            print(f"  {i+1}. {criterion['name']}: {criterion['description']} (가중치: {criterion['weight']})")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()