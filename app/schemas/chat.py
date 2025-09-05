from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class StartRequest(BaseModel):
    message: str = Field(..., min_length=1)

class SendRequest(BaseModel):
    message: str = Field(..., min_length=1)

class FeedbackRequest(BaseModel):
    feedback: str = Field(..., min_length=1)

class TrendingKeyword(BaseModel):
    """Single trending keyword record aligned with `seo_trending_keywords_generated` table.
    
    Notes:
    - All fields except Category and Keyword are optional for generation flexibility.
    - Timestamps default to `datetime.utcnow()` so the LLM doesn't have to fabricate them.
    - Used for structured output of trending keyword suggestions.
    """
    Category: str = Field(..., description="Category of the keyword")
    Keyword: str = Field(..., description="The trending keyword phrase")
    Search_Intent: Optional[str] = Field(None, description="Search intent (commercial, informational, etc.)")
    Trend_Score: Optional[float] = Field(None, description="Trend score (0-100)")
    Keyword_Type: Optional[str] = Field(None, description="Type of keyword (primary, secondary, long_tail)")
    Geo_Focus: Optional[str] = Field(None, description="Geographic focus (global, local, regional)")
    Rationale: Optional[str] = Field(None, description="Why this keyword is trending")
    Platform_Source: Optional[str] = Field("AI_Generated", description="Source platform")
    Status: Optional[str] = Field("pending", description="Approval status")
    Created_At: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    Updated_At: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    model_config = {"extra": "ignore"}


class TrendingKeywordBatch(BaseModel):
    """Container model for multiple trending keyword records + optional metadata.
    
    This matches the keyword generation pattern:
    {
        "trending_keywords": [ { ...keyword row... }, ...],
        "summary": { ...optional aggregate... },
        "categories_analyzed": [...]
    }
    """
    trending_keywords: List[TrendingKeyword] = Field(..., description="List of trending keywords to persist")
    summary: Optional[Dict[str, Any]] = Field(None, description="Optional summary metrics")
    categories_analyzed: Optional[List[str]] = Field(None, description="Categories that were analyzed")
    
    model_config = {"extra": "ignore"}


class SEOOutcome(BaseModel):
    """Single SEO outcome record (row) aligned with `seo_outcomes` table.

    Notes:
    - All fields except `Page_Url` are optional for generation flexibility.
    - Timestamps default to `datetime.utcnow()` so the LLM doesn't have to fabricate them.
    - Used for structured output of a single improvement if/when needed.
    """
    Page_Url: str = Field(..., description="Page URL")
    Original_Title: Optional[str] = Field(None, description="Original title")
    Improved_Title: Optional[str] = Field(None, description="Improved title")
    Rationale: Optional[str] = Field(None, description="Rationale for improvement")
    Improvement_Score: Optional[float] = Field(None, description="Score of improvement")
    Issues_Found: Optional[str] = Field(None, description="Issues found during analysis (JSON or text)")
    Recommendations: Optional[str] = Field(None, description="Recommendations for improvement")
    Health_Score: Optional[float] = Field(None, description="Health score of the page")
    Created_At: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    Updated_At: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    model_config = {"extra": "ignore"}


class SEOOutcomeBatch(BaseModel):
    """Container model for multiple outcome records + optional metadata.

    This better matches the agent's JSON block pattern:
    {
        "updates": [ { ...outcome row... }, ...],
        "summary": { ...optional aggregate... },
        "flagged_issues": { ...optional flags ... }
    }
    """
    updates: List[SEOOutcome] = Field(..., description="List of outcome rows to persist")
    summary: Optional[Dict[str, Any]] = Field(None, description="Optional summary metrics (health scores, counts)")
    flagged_issues: Optional[Dict[str, Any]] = Field(None, description="Optional flagged issues object from audit")
    
    model_config = {"extra": "ignore"}


class HighPriorityTask(BaseModel):
    """Single high priority SEO task record aligned with `seo_high_priority` table."""
    Page_Url: str = Field(..., description="Page URL")
    Is_Outdated_Year: bool = Field(False, description="Contains outdated year reference")
    Is_Very_Low_Score: bool = Field(False, description="Very low improvement score (<60)")
    Is_Critical_Page: bool = Field(False, description="Critical business page identified")
    Priority_Score: float = Field(..., description="Calculated priority score 1-100")
    Priority_Level: str = Field("high", description="Priority level (high/medium/low)")
    Status: str = Field("pending", description="Task status (pending/in_progress/resolved/ignored)")
    Trigger_Details: Optional[str] = Field(None, description="JSON string explaining why flagged as high priority")
    
    model_config = {"extra": "ignore"}


class HighPriorityBatch(BaseModel):
    """Container for multiple high priority tasks with metadata."""
    high_priority_tasks: List[HighPriorityTask] = Field(..., description="List of high priority tasks to create")
    summary: Optional[str] = Field(None, description="Summary of analysis (e.g., 'Found 3 high priority tasks')")
    analysis_context: Optional[str] = Field(None, description="Context from audit analysis")
    
    model_config = {"extra": "ignore"}