import os
import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List

class CurriculumReaderInput(BaseModel):
    curriculum_path: str = Field(description="The path to the curriculum YAML file to read.")

class CurriculumReaderTool(BaseTool):
    name: str = "CurriculumReaderTool"
    description: str = "Parses a curriculum YAML file to identify the modules, topics, and kb_tags. Returns the structured curriculum."
    args_schema: type[BaseModel] = CurriculumReaderInput

    def _run(self, curriculum_path: str) -> str:
        """Parses the YAML curriculum file."""
        try:
            with open(curriculum_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            # Return as a formatted string so the agent can read it
            return yaml.dump(data, default_flow_style=False)
        except Exception as e:
            return f"Error reading curriculum at {curriculum_path}: {str(e)}"


class KnowledgeBaseSearchInput(BaseModel):
    kb_tags: List[str] = Field(description="A list of knowledge base tags (e.g., ['math', 'percentages']) to search for.")
    kb_dirs: List[str] = Field(description="A list of directories containing the knowledge base markdown files.")

class KnowledgeBaseSearchTool(BaseTool):
    name: str = "KnowledgeBaseSearchTool"
    description: str = "Fetches the exact context from your markdown files based on active kb_tags."
    args_schema: type[BaseModel] = KnowledgeBaseSearchInput

    def _run(self, kb_tags: List[str], kb_dirs: List[str]) -> str:
        """Searches markdown files in the given directories for the specified tags."""
        matched_content = []
        try:
            for kb_dir in kb_dirs:
                if not os.path.exists(kb_dir):
                    continue
                
                # Recursively search through the directory
                for root, _, files in os.walk(kb_dir):
                    for file in files:
                        if file.endswith('.md'):
                            filepath = os.path.join(root, file)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Check if any of the provided tags exist in the file content
                                # We check in a case-insensitive manner
                                content_lower = content.lower()
                                tag_match = any(tag.lower() in content_lower for tag in kb_tags)
                                
                                if tag_match:
                                    matched_content.append(f"--- Context from {file} ---\n{content}\n")
            
            if matched_content:
                return "\n".join(matched_content)
            else:
                return f"No context found in the provided directories for tags: {kb_tags}"
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
