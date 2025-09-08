from typing import Dict, Any, List, Optional
from langchain.agents import create_react_agent, AgentExecutor, tool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver 
import re
import json
from datetime import datetime
from sqlalchemy import select
from app.db.session import  get_sync_sessionmaker
from app.models.models import SeoTitle, SeoKeywordsTrending
from langchain_core.runnables import RunnableConfig
from sqlalchemy import insert
from app.models.models import SeoOutcomes, SeoGeneratedKeywords, SeoHighPriority
from datetime import datetime
from langchain.agents import tool
from app.schemas.chat import SEOOutcome, SEOOutcomeBatch,TrendingKeywordBatch,HighPriorityBatch

# Initialize LLM with better model for complex tasks
openai = ChatOpenAI(model="gpt-5", temperature=0.1)
# Base LLM for ReAct reasoning (avoid constraining to single-row structured schema)
llm = openai
# Structured variant for batch extraction
llm_title_batch = openai.with_structured_output(SEOOutcomeBatch)
llm_keyword_batch = openai.with_structured_output(TrendingKeywordBatch)
llm_high_priority=openai.with_structured_output(HighPriorityBatch)
# memory = MemorySaver()
# config = RunnableConfig(configurable={"thread_id": "1"})


@tool
def seo_db_stats() -> Dict[str, Any]:
    """Get aggregate statistics about titles & keyword trends.

        Input: None
        Process:
            1. Load all rows from `SeoTitle`.
            2. Determine latest `Last_Updated` timestamp.
            3. Load all rows from `SeoKeywordsTrending` & count by `Trend_Status`.
            4. Derive declining count & positive (Emerging/Peaking/Rising) aggregate.
        Output (dict):
            {
                "source": "mysql",
                "total_titles": int,
                "latest_title_update": str|None (ISO8601),
                "trending_keywords_total": int,
                "declining_trends": int,
                "positive_trends": int,
                "trend_status_breakdown": {status: count}
            }
        """
    print("Running seo_db_stats tool...")
    SessionLocal = get_sync_sessionmaker()
    with SessionLocal() as session:
        # Titles
        titles_result = session.execute(select(SeoTitle))
        titles = titles_result.scalars().all()
        total_titles = len(titles)
        latest_update = None
        if total_titles:
            latest_update = max([t.Last_Updated for t in titles if t.Last_Updated])

        # Trends
        trends_result = session.execute(select(SeoKeywordsTrending))
        trends = trends_result.scalars().all()
        status_counts: Dict[str, int] = {}
        for tr in trends:
            st = (tr.Trend_Status or "Unknown").strip()
            status_counts[st] = status_counts.get(st, 0) + 1

        declining = status_counts.get("Declining", 0)
        positive = sum(status_counts.get(s, 0) for s in ["Emerging", "Peaking", "Rising"])
        print("Seo DB stats computed....\n")
    return f"""
        "output":"It fetched all seo titles and trending keywords from database.",
        "source": "mysql",
        "total_titles": {total_titles},
        "latest_title_update": "{latest_update.isoformat() if latest_update else None}",
        "trending_keywords_total": {len(trends)},
        "declining_trends": {declining},
        "positive_trends": {positive},
        "trend_status_breakdown": {status_counts},"""
        




@tool
def metadata_validator() -> Dict[str, Any]:
    """Validate quality/freshness of both SEO titles AND keywords.
        Output:
            {
                "source": "mysql",
                "titles": {total_rows, issues, details},
                "keywords": {total_rows, issues, details}, 
                "summary": {total_issues, combined_health_score},
                "improvements_needed": {title_improvements: [...], keyword_improvements: [...]}
            }
        """
    try:
        SessionLocal = get_sync_sessionmaker()
        with SessionLocal() as session:
            # Get SEO Titles
            titles_res = session.execute(select(SeoTitle))
            title_rows = titles_res.scalars().all()
            
            # Get SEO Keywords
            keywords_res = session.execute(select(SeoKeywordsTrending))
            keyword_rows = keywords_res.scalars().all()

        current_year = datetime.now().year
        current_date = datetime.now()
        
        # TITLE VALIDATION
        title_incomplete: List[Dict[str, Any]] = []
        title_unnormalized: List[Dict[str, Any]] = []
        title_outdated: List[Dict[str, Any]] = []
        titles_need_improvement: List[str] = []

        for idx, row in enumerate(title_rows):
            title = row.SEO_Optimized_Title or ""
            last_updated = row.Last_Updated

            if not title or len(title.strip()) < 10:
                title_incomplete.append({
                    "row": idx + 1,
                    "page_url": row.Page_Url,
                    "title": title[:50] if title else "EMPTY",
                    "issue": "Too short or missing"
                })
                titles_need_improvement.append(title if title else row.Page_Url)

            if title and (title.isupper() or title.islower() or re.search(r'[!@#$%^&*()]{2,}', title)):
                title_unnormalized.append({
                    "row": idx + 1,
                    "page_url": row.Page_Url,
                    "title": title[:50],
                    "issue": "Poor formatting"
                })
                titles_need_improvement.append(title)

            if last_updated:
                try:
                    if last_updated.year < current_year - 1:
                        title_outdated.append({
                            "row": idx + 1,
                            "page_url": row.Page_Url,
                            "title": title[:50],
                            "last_updated": last_updated.isoformat(),
                            "issue": f"Outdated (from {last_updated.year})"
                        })
                        titles_need_improvement.append(title)
                except Exception:
                    pass

        # KEYWORD VALIDATION
        keyword_stale: List[Dict[str, Any]] = []
        keyword_low_score: List[Dict[str, Any]] = []
        keyword_missing_intent: List[Dict[str, Any]] = []
        keyword_declining: List[Dict[str, Any]] = []
        keywords_need_improvement: List[str] = []

        for idx, row in enumerate(keyword_rows):
            keyword = row.Trending_Keyword or ""
            trend_score = row.Trend_Score or 0
            search_intent = row.Search_Intent or ""
            trend_status = row.Trend_Status or ""
            updated_at = row.Updated_At
            category = row.Category or "Unknown"

            # Stale keywords (>6 months old)
            if updated_at:
                try:
                    months_old = (current_date - updated_at).days / 30
                    if months_old > 6:
                        keyword_stale.append({
                            "row": idx + 1,
                            "keyword": keyword,
                            "category": category,
                            "months_old": round(months_old, 1),
                            "issue": "Stale data (>6 months)"
                        })
                        keywords_need_improvement.append(category)
                except Exception:
                    pass

            # Low trend score
            if trend_score < 50:
                keyword_low_score.append({
                    "row": idx + 1,
                    "keyword": keyword,
                    "category": category,
                    "trend_score": trend_score,
                    "issue": "Low trend score"
                })
                keywords_need_improvement.append(category)

            # Missing search intent
            if not search_intent.strip():
                keyword_missing_intent.append({
                    "row": idx + 1,
                    "keyword": keyword,
                    "category": category,
                    "issue": "Missing search intent"
                })
                keywords_need_improvement.append(category)

            # Declining trends
            if trend_status.lower() == 'declining':
                keyword_declining.append({
                    "row": idx + 1,
                    "keyword": keyword,
                    "category": category,
                    "trend_status": trend_status,
                    "issue": "Declining trend"
                })
                keywords_need_improvement.append(category)

        # Calculate health scores
        title_issue_count = len(title_incomplete) + len(title_unnormalized) + len(title_outdated)
        keyword_issue_count = len(keyword_stale) + len(keyword_low_score) + len(keyword_missing_intent) + len(keyword_declining)
        total_issues = title_issue_count + keyword_issue_count
        total_records = len(title_rows) + len(keyword_rows)
        
        title_health = max(0, 100 - (title_issue_count * 100 // len(title_rows))) if title_rows else 0
        keyword_health = max(0, 100 - (keyword_issue_count * 100 // len(keyword_rows))) if keyword_rows else 0
        combined_health = max(0, 100 - (total_issues * 100 // total_records)) if total_records else 0

        return {
            "source": "mysql",
            "titles": {
                "total_rows": len(title_rows),
                "issues": {
                    "incomplete_count": len(title_incomplete),
                    "unnormalized_count": len(title_unnormalized),
                    "outdated_count": len(title_outdated),
                    "total_issues": title_issue_count
                },
                "details": {
                    "incomplete": title_incomplete[:5],
                    "unnormalized": title_unnormalized[:5],
                    "outdated": title_outdated[:5]
                },
                "health_score": title_health
            },
            "keywords": {
                "total_rows": len(keyword_rows),
                "issues": {
                    "stale_count": len(keyword_stale),
                    "low_score_count": len(keyword_low_score), 
                    "missing_intent_count": len(keyword_missing_intent),
                    "declining_count": len(keyword_declining),
                    "total_issues": keyword_issue_count
                },
                "details": {
                    "stale": keyword_stale[:5],
                    "low_score": keyword_low_score[:5],
                    "missing_intent": keyword_missing_intent[:5],
                    "declining": keyword_declining[:5]
                },
                "health_score": keyword_health
            },
            "summary": {
                "total_records": total_records,
                "total_issues": total_issues,
                "combined_health_score": combined_health,
                "title_health": title_health,
                "keyword_health": keyword_health
            },
            "improvements_needed": {
                "title_improvements": list(set(titles_need_improvement))[:10],
                "keyword_improvements": list(set(keywords_need_improvement))[:10]
            }
        }
    except Exception as e:
        return {"error": f"Validation failed: {str(e)}"}


@tool
def seo_flagging_catalyst() -> Dict[str, Any]:
    """Flag SEO issues using titles + trend data.

        Input: (ignored)
        Flags produced:
            - declining
            - missing_trends
            - outdated
            - low_performing
        Output includes summary counts, top 5 sample rows per flag, and recommendations.
        """
    try:
        SessionLocal = get_sync_sessionmaker()
        with SessionLocal() as session:
            titles_res = session.execute(select(SeoTitle))
            titles = titles_res.scalars().all()
            trends_res = session.execute(select(SeoKeywordsTrending))
            trends = trends_res.scalars().all()

        declining_keywords = {t.Trending_Keyword.lower() for t in trends if (t.Trend_Status == 'Declining' and t.Trending_Keyword)}
        positive_trends = [t for t in trends if t.Trend_Status in ['Emerging', 'Peaking', 'Rising']]

        flagged = {"declining": [], "missing_trends": [], "outdated": [], "low_performing": []}
        current_year = datetime.now().year

        for idx, row in enumerate(titles):
            title = row.SEO_Optimized_Title or ""
            title_lower = title.lower()
            primary_kw = (row.Primary_Keyword or "").lower()
            last_updated = row.Last_Updated

            # Declining keyword occurrences
            found_declining = [kw for kw in declining_keywords if kw in title_lower]
            if found_declining:
                flagged["declining"].append({
                    "row": idx + 1,
                    "title": title[:60],
                    "declining_keywords": found_declining
                })

            # Missing trends (category heuristic based on primary keyword first token)
            if primary_kw:
                category_word = primary_kw.split()[0] if primary_kw.split() else ''
                if category_word and len(category_word) > 2:
                    relevant = [tr for tr in positive_trends if (tr.Category or '').lower().find(category_word) != -1]
                    missing = []
                    for tr in relevant:
                        trend_kw = (tr.Trending_Keyword or '').lower()
                        if trend_kw and trend_kw not in title_lower:
                            missing.append(trend_kw)
                    if missing:
                        flagged["missing_trends"].append({
                            "row": idx + 1,
                            "title": title[:60],
                            "category": category_word,
                            "missing_keywords": missing[:3]
                        })

            # Outdated
            if last_updated:
                try:
                    if last_updated.year < current_year - 1:
                        flagged["outdated"].append({
                            "row": idx + 1,
                            "title": title[:60],
                            "last_updated": last_updated.isoformat(),
                            "years_old": current_year - last_updated.year
                        })
                except Exception:
                    pass

            # Low performing
            low_issues = []
            if len(title) < 30:
                low_issues.append("Too short")
            if primary_kw and primary_kw not in title_lower:
                low_issues.append("Missing primary keyword")
            if low_issues:
                flagged["low_performing"].append({
                    "row": idx + 1,
                    "title": title[:60],
                    "issues": low_issues
                })

        total_issues = sum(len(v) for v in flagged.values())
        return {
            "analysis_complete": True,
            "source": "mysql",
            "summary": {
                "total_rows_analyzed": len(titles),
                "total_issues_found": total_issues,
                "declining_count": len(flagged['declining']),
                "missing_trends_count": len(flagged['missing_trends']),
                "outdated_count": len(flagged['outdated']),
                "low_performing_count": len(flagged['low_performing'])
            },
            "flagged_issues": {
                "declining": flagged['declining'][:5],
                "missing_trends": flagged['missing_trends'][:5],
                "outdated": flagged['outdated'][:5],
                "low_performing": flagged['low_performing'][:5]
            },
            "recommendations": {
                "high_priority": f"Update {len(flagged['declining'])} titles with declining keywords",
                "medium_priority": f"Add trending keywords to {len(flagged['missing_trends'])} titles",
                "low_priority": f"Refresh {len(flagged['outdated'])} outdated titles"
            }
        }
    except Exception as e:
        return {"error": f"Flagging analysis failed: {str(e)}"}


@tool
def generate_title_improvements(titles_json: str) -> Dict[str, Any]:
    """Generate improved SEO titles with structured output."""
    try:
        if titles_json.strip().startswith('{'):
            data = json.loads(titles_json)
        else:
            titles_list = titles_json.strip().strip('[]').split(',')
            data = {"titles": [t.strip().strip('"\'') for t in titles_list]}
        titles = data.get("titles", [])
        if not titles:
            return {"error": "No titles provided"}

        titles = titles[:5]
        structured = llm_title_batch.invoke(f"""titles": {titles}""")
        return structured.dict()

    except Exception as e:
        return {"error": f"Title improvement failed: {str(e)}"}


@tool
def generate_keyword_improvements(keywords_json: str) -> Dict[str, Any]:
    """Generate improved SEO keyword suggestions with structured output.
    
    Accepts either:
    - Raw keyword list: ["kw1", "kw2", ...]
    - Dict with {"keywords": [...]} or {"trending_keywords": [...]}
    - Full metadata_validator output (extracts improvements_needed.keyword_improvements)
    """
    import json
    try:
        raw = keywords_json.strip()
        base_items = []

        # Parse JSON input
        parsed = None
        if raw.startswith('{') or raw.startswith('['):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON provided"}

        # Case 1: Full metadata_validator output
        if isinstance(parsed, dict) and "improvements_needed" in parsed:
            kw_list = parsed["improvements_needed"].get("keyword_improvements", [])
            base_items = [{"Category": "General", "Keyword": kw} for kw in kw_list]

        # Case 2: keywords/trending_keywords field
        elif isinstance(parsed, dict):
            kw_list = parsed.get("keywords") or parsed.get("trending_keywords") or []
            base_items = [{"Category": "General", "Keyword": kw} for kw in kw_list]

        # Case 3: Raw list
        elif isinstance(parsed, list):
            base_items = [{"Category": "General", "Keyword": kw} for kw in parsed if isinstance(kw, str)]

        # Case 4: Comma-separated string
        else:
            base_items = [{"Category": "General", "Keyword": kw.strip()} for kw in raw.split(',') if kw.strip()]

        if not base_items:
            return {"error": "No keywords provided"}

        # Limit to 25 items
        base_items = base_items[:10]

        # Call LLM
        structured = llm_keyword_batch.invoke(f"trending_keywords: {base_items}")
        return structured.dict()

    except Exception as e:
        return {"error": f"keyword_generation_failed: {str(e)}"}

@tool
def update_seo_outcomes_db(updates: list, summary: dict = None) -> dict:
    """Persist structured SEOOutcomeBatch data into `seo_outcomes`."""
    from sqlalchemy import insert
    from app.models.models import SeoOutcomes
    import json
    SessionLocal = get_sync_sessionmaker()

    if not updates:
        return {"status": "no_data", "rows_inserted": 0, "message": "No updates provided"}

    with SessionLocal() as session:
        try:
            now = datetime.utcnow()
            rows = []
            for upd in updates:
                rows.append({
                    "Page_Url": upd.get("Page_Url", "N/A"),
                    "Original_Title": upd.get("Original_Title","N/A"),
                    "Improved_Title": upd.get("Improved_Title",""),
                    "Rationale": upd.get("Rationale"),
                    "Improvement_Score": upd.get("Improvement_Score"),
                    "Issues_Found": upd.get("Issues_Found"),
                    "Recommendations": upd.get("Recommendations"),
                    "Health_Score": upd.get("Health_Score"),
                    "Created_At": upd.get("Created_At", now),
                    "Updated_At": upd.get("Updated_At", now),
                })
            session.execute(insert(SeoOutcomes), rows)
            session.commit()
            return {"status": "success", "rows_inserted_seo_outcome": len(rows)}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}

@tool
def update_trending_keywords_db(agent_output: dict = None, **kwargs) -> dict:
    """Persist structured TrendingKeywordBatch data into `seo_trending_keywords_generated`."""
    SessionLocal = get_sync_sessionmaker()

    # Allow both flat and nested payloads
    data = agent_output or kwargs
    trending_keywords = data.get("trending_keywords", [])

    if not trending_keywords:
        return {"status": "no_data", "rows_inserted": 0, "message": "No keywords provided"}

    with SessionLocal() as session:
        try:
            now = datetime.utcnow()
            rows = [
                {
                    "Category": kw.get("Category"),
                    "Keyword": kw.get("Keyword"),
                    "Search_Intent": kw.get("Search_Intent"),
                    "Trend_Score": kw.get("Trend_Score"),
                    "Keyword_Type": kw.get("Keyword_Type"),
                    "Geo_Focus": kw.get("Geo_Focus"),
                    "Rationale": kw.get("Rationale"),
                    "Platform_Source": kw.get("Platform_Source", "AI_Generated"),
                    "Status": kw.get("Status", "pending"),
                    "Created_At": kw.get("Created_At", now),
                    "Updated_At": kw.get("Updated_At", now),
                }
                for kw in trending_keywords
            ]

            session.execute(insert(SeoGeneratedKeywords), rows)
            session.commit()
            return {"status": "success", "rows_inserted_trending_keyword": len(rows)}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}

@tool
def analyze_high_priority_tasks(audit_data: str) -> dict:
    """Analyze audit results to identify high priority SEO tasks using structured LLM output.

    Input: JSON string or text containing audit results (flagging, outcomes, improvements)
    Process: 
        - Use LLM to analyze which tasks need immediate attention
        - Generate priority scores based on multiple factors
        - Create structured high priority task records
    Output: HighPriorityBatch dict with high_priority_tasks list
    """

    try:
        result = llm_high_priority.invoke(f"{audit_data}")
        return result.dict()
    except Exception as e:
        return {"high_priority_tasks": [], "error": f"analysis_failed: {e}"}


@tool
def insert_high_priority_tasks(priority_data: dict | list | str) -> dict:
    """Insert high priority SEO tasks into seo_high_priority table ONLY."""
    import json
    from sqlalchemy import insert
    from app.models.models import SeoHighPriority
    from datetime import datetime
    SessionLocal = get_sync_sessionmaker()

    # Parse input if string
    if isinstance(priority_data, str):
        try:
            priority_data = priority_data.replace('True', 'true').replace('False', 'false')
            priority_data = json.loads(priority_data)
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"Invalid JSON: {str(e)}",
                "received_data": priority_data[:200]
            }

    # Normalize priority_data to a list of tasks
    if isinstance(priority_data, dict):
        tasks = priority_data.get("high_priority_tasks", [])
    elif isinstance(priority_data, list):
        tasks = priority_data
    else:
        return {"status": "error", "message": "priority_data must be dict, list, or valid JSON string"}

    if not tasks:
        return {"status": "no_data", "tasks_inserted": 0, "message": "No tasks provided"}

    with SessionLocal() as session:
        try:
            now = datetime.utcnow()
            rows, rejected = [], []

            for task in tasks:
                if not isinstance(task, dict):
                    rejected.append({"reason": "invalid task format", "task": task})
                    continue

                page_url = task.get("Page_Url")
                if not page_url:
                    rejected.append({"reason": "missing Page_Url", "task": task})
                    continue
                outcome_result= session.execute(select(SeoOutcomes).where(SeoOutcomes.Page_Url==page_url))
                outcomes=outcome_result.scalar_one_or_none()
                if outcomes:
                    outcome_id=outcomes.id
                else:
                    outcome_id=None

                trigger_details = task.get("Trigger_Details", "")
                if isinstance(trigger_details, dict):
                    trigger_details = json.dumps(trigger_details)

                rows.append({
                    "Page_Url": page_url,
                    "outcome_id": outcome_id,
                    "Is_Outdated_Year": task.get("Is_Outdated_Year", False),
                    "Is_Very_Low_Score": task.get("Is_Very_Low_Score", False),
                    "Is_Critical_Page": task.get("Is_Critical_Page", False),
                    "Priority_Score": task.get("Priority_Score", 70),
                    "Priority_Level": task.get("Priority_Level", "high"),
                    "Status": task.get("Status", "pending"),
                    "Trigger_Details": trigger_details,
                    "Last_Evaluated": now,
                    "Created_At": now,
                    "Updated_At": now
                })

            if rows:
                session.execute(insert(SeoHighPriority), rows)
                session.commit()

            return {
                "status": "success",
                "tasks_inserted": len(rows),
                "rejected_tasks": len(rejected),
                "rejected_sample": rejected[:3]
            }

        except Exception as e:
            session.rollback()
            return {"status": "error", "message": f"Insert failed: {str(e)}"}
