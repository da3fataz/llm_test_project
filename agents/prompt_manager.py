"""
프롬프트 로더 모듈
- YAML 파일에서 에이전트별 프롬프트 및 평가 기준 로드
- 프롬프트 템플릿 관리
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

class PromptManager:
    """프롬프트 및 평가 기준 관리 클래스"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        프롬프트 관리자 초기화
        
        Args:
            prompts_dir: 프롬프트 YAML 파일들이 위치한 디렉토리 경로
        """
        self.prompts_dir = prompts_dir
        self.prompts_cache = {}  # 프롬프트 캐싱
        self.criteria_cache = {}  # 평가 기준 캐싱
    
    def load_prompt_file(self, file_path: str) -> Dict:
        """
        YAML 프롬프트 파일 로드
        
        Args:
            file_path: YAML 파일 경로
            
        Returns:
            Dict: 로드된 YAML 내용
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)
        
        return yaml_content
    
    def get_agent_prompt(self, agent_type: str, prompt_name: str) -> ChatPromptTemplate:
        """
        에이전트 프롬프트 가져오기
        
        Args:
            agent_type: 에이전트 타입 (evaluator, setup 등)
            prompt_name: 프롬프트 이름
            
        Returns:
            ChatPromptTemplate: 로드된 프롬프트 템플릿
        """
        cache_key = f"{agent_type}_{prompt_name}"
        
        # 캐시된 프롬프트가 있으면 반환
        if cache_key in self.prompts_cache:
            return self.prompts_cache[cache_key]
        
        # 프롬프트 파일 경로
        file_path = os.path.join(self.prompts_dir, f"{agent_type}.yaml")
        
        # YAML 파일 로드
        yaml_content = self.load_prompt_file(file_path)
        
        # 요청된 프롬프트 찾기
        if prompt_name not in yaml_content:
            raise ValueError(f"프롬프트를 찾을 수 없습니다: {prompt_name} (in {agent_type})")
        
        prompt_data = yaml_content[prompt_name]
        
        # 프롬프트 템플릿 생성
        messages = []
        
        if "system_message" in prompt_data:
            messages.append(SystemMessage(content=prompt_data["system_message"]))
            
        if "human_message" in prompt_data:
            messages.append(HumanMessage(content=prompt_data["human_message"]))
        
        prompt_template = ChatPromptTemplate.from_messages(messages)
        
        # 캐시에 저장
        self.prompts_cache[cache_key] = prompt_template
        
        return prompt_template
    
    def get_evaluation_criteria(self, domain: str = None) -> List[Dict]:
        """
        평가 기준 가져오기
        
        Args:
            domain: 도메인 이름 (news_curation, meeting_scheduler 등)
                   None이면 기본 평가 기준 반환
        
        Returns:
            List[Dict]: 평가 기준 목록
        """
        # 캐시된 평가 기준이 있으면 반환
        cache_key = domain or "default"
        if cache_key in self.criteria_cache:
            return self.criteria_cache[cache_key]
        
        # 평가 기준 파일 경로
        file_path = os.path.join(self.prompts_dir, "evaluation_criteria.yaml")
        
        # YAML 파일 로드
        yaml_content = self.load_prompt_file(file_path)
        
        # 기본 평가 기준
        default_criteria = yaml_content.get("default", [])
        
        # 도메인별 평가 기준 (있는 경우)
        domain_criteria = []
        if domain and domain in yaml_content:
            domain_criteria = yaml_content[domain]
        
        # 기본 기준과 도메인 기준 합치기
        all_criteria = default_criteria + domain_criteria
        
        # 중복 제거 (name 기준)
        unique_criteria = []
        names = set()
        for criterion in all_criteria:
            if criterion["name"] not in names:
                unique_criteria.append(criterion)
                names.add(criterion["name"])
        
        # 캐시에 저장
        self.criteria_cache[cache_key] = unique_criteria
        
        return unique_criteria