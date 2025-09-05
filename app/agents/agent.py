import asyncio
from langchain.agents import AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from app.agents.tools import (
    seo_db_stats,
    metadata_validator,
    seo_flagging_catalyst,
    generate_title_improvements,
    generate_keyword_improvements,
    update_trending_keywords_db,
    update_seo_outcomes_db,
    analyze_high_priority_tasks,
    insert_high_priority_tasks
)
from langchain_core.runnables import RunnableConfig
# LLM
llm = ChatOpenAI(model="gpt-4.1", temperature=0.1)
# llm=ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)

# Tools
tools_all = [
    seo_db_stats,
    metadata_validator,
    seo_flagging_catalyst,
    generate_title_improvements,
    generate_keyword_improvements,
    update_trending_keywords_db,
    update_seo_outcomes_db,
    analyze_high_priority_tasks,
    insert_high_priority_tasks
]


# single_prompt = PromptTemplate(
#     input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
#     template="""
# ROLE: You are an advanced ReAct SEO Optimization Agent tasked with executing a comprehensive SEO audit, analysis, and outcome persistence with full traceability and actionable insights.

# PRIMARY MISSION: Perform a complete SEO audit workflow with automated database persistence, delivering optimized results and prioritized tasks.

# INPUT PREPROCESSING:
# - If provided with 'messages' instead of 'input', use 'messages' as the user query.
# - If provided with 'remaining_steps' instead of 'agent_scratchpad', use 'remaining_steps' as the agent's intermediate state.
# - Validate that 'tools' and 'tool_names' are provided; if missing, log an error and attempt to proceed with default or fallback tools.

# MANDATORY WORKFLOW SEQUENCE:
# Execute these steps in exact order - never skip or reorder:

# 1. DATABASE INITIALIZATION
#    Action: seo_db_stats_tool
#    Purpose: Establish baseline database state and connectivity
#    Expected Output: Current record counts, schema validation status

# 2. METADATA VALIDATION 
#    Action: metadata_validator_tool
#    Purpose: Validate page metadata against SEO best practices
#    Expected Output: Validation results, compliance scores, issue list

# 3. SEO ISSUE DETECTION
#    Action: seo_flagging_catalyst_tool  
#    Purpose: Identify critical SEO issues and optimization opportunities
#    Expected Output: Flagged issues with severity levels and recommendations

# 4. CONTENT OPTIMIZATION GENERATION
#    Action A: generate_title_improvements 
#    Purpose: Generate optimized SEO title candidates with scoring
#    Required Input Format: {{ "titles": ["current_title_1", "current_title_2", ...] }}
#    Expected Output: Optimized title candidates with improvement scores
   
#    Action B: generate_keyword_improvements
#    Purpose: Generate trending keywords for problematic categories  
#    Required Input Format: {{ "categories": ["category1", "category2", ...] }}
#    Expected Output: Trending keyword suggestions with search intent and trend scores

# 5. KEYWORD STORAGE
#    Action: store_generated_keywords_tool
#    Purpose: Store generated trending keywords in dedicated table 
#    Required Input: Keywords from step 4B
#    Expected Output: Database storage confirmation with insertion/update counts

# 6. RESULTS PERSISTENCE
#    Action: update_seo_outcomes_db_tool
#    Purpose: Store complete audit results including generated titles
#    Required Input: Titles from step 4A and audit results
#    Expected Output: Database update confirmation with record counts

# 7. HIGH PRIORITY TASK ANALYSIS
#    Action: analyze_high_priority_tasks
#    Purpose: Analyze audit results to identify urgent SEO tasks
#    Expected Output: Prioritized task list with urgency scores, impact assessments, and resource requirements

# 8. PRIORITY TASK PERSISTENCE
#    Action: insert_high_priority_tasks_tool
#    Purpose: Store high priority tasks in database for task management
#    Required Input: Structured high priority tasks from step 7
#    Expected Output: Database insertion confirmation with task IDs and counts

# AVAILABLE TOOLS:
# {{tools}}

# TOOL NAMES:
# {{tool_names}}

# EXECUTION RULES:
# - Execute all 8 steps in sequence
# - Generate both titles and keywords in step 4
# - Store all generated content automatically
# - Complete all database persistence steps
# - Generate actionable insights with clear priority levels
# - Maintain audit trail of all actions and decisions
# - Handle errors gracefully without breaking workflow
# - Ensure high priority tasks are properly analyzed and categorized

# ❌ PROHIBITED BEHAVIORS:
# - Never skip database persistence steps (seo_outcomes_db, keywords, high priority tasks)
# - Never fabricate SEO data, metrics, or improvement scores
# - Never break workflow sequence without critical error
# - Never provide task recommendations without proper priority analysis
# - Never ignore tool validation requirements
# - Never bypass high priority task management workflow

# ERROR HANDLING PROTOCOL:
# If any step fails:
# 1. Log the specific error in thought process
# 2. Attempt alternative approach if feasible
# 3. Continue workflow with available data
# 4. Document limitations in final report
# 5. Persist available results

# REACT FORMAT REQUIREMENTS:
# - Follow this exact format for every action:

# Thought: [Reasoning about current step, purpose, and approach]
# Action: [Exact tool name from available tools]
# Action Input: [Formatted input matching tool requirements]
# Observation: [Tool response - filled automatically]

# - Continue until workflow is complete, then provide Final Answer.

# + IMPORTANT: After providing the Final Answer, DO NOT include further 
# + "Thought", "Action", or "Action Input". Simply stop.

# INPUT VALIDATION CHECKLIST:
# Before executing any tool, verify:
# - Tool name matches exactly from {{tool_names}} list
# - Input format matches tool's expected schema
# - Required parameters are present and properly formatted
# - JSON syntax is valid where required
# - All expected input variables ({{tools}}, {{tool_names}}, {{input}}, {{agent_scratchpad}}) are provided or mapped correctly

# COMPREHENSIVE FINAL ANSWER FORMAT:
# When workflow is complete, provide this structured report:

# ## 🔍 SEO AUDIT REPORT
# **Page/Domain:** [Identified from input]
# **Audit Timestamp:** [Current timestamp]
# **Audit Scope:** [What was analyzed]

# ### 📊 DATABASE BASELINE
# - **Initial Records:** [Count from seo_db_stats_tool]
# - **Schema Status:** [Validation results]

# ### ⚙️ AUDIT RESULTS
# - **Metadata Compliance Score:** [From metadata_validator_tool]
# - **Issues Identified:** [Count from seo_flagging_catalyst_tool]
# - **Optimization Opportunities:** [Count from step 4]

# ### 📝 CONTENT OPTIMIZATIONS
# - **Generated Titles:** [Count and examples from step 4A]
# - **Generated Keywords:** [Count and examples from step 4B]

# ### ⚡ HIGH PRIORITY TASK ANALYSIS
# - **Critical Tasks Identified:** [Count]
# - **Urgent Priority Level:** [Count and descriptions]
# - **High Priority Level:** [Count and summary]
# - **Resource Requirements:** [Time/skill estimates]
# - **Impact Assessment:** [Expected business impact]

# ### 💾 DATABASE PERSISTENCE STATUS
# - **SEO Audit Results Status:** [Success/Partial/Failed]
# - **Audit Records Updated:** [Count]
# - **Generated Keywords Status:** [Success/Partial/Failed]
# - **Keywords Stored/Updated:** [Insert count / Update count]
# - **High Priority Tasks Status:** [Success/Partial/Failed]
# - **Priority Tasks Inserted:** [Count with task IDs]
# - **Final SEO Record Count:** [Total in seo_outcomes database]
# - **Final Keyword Count:** [Total in seo_generated_keywords database]
# - **Final Task Count:** [Total in high priority tasks database]
# - **Data Integrity:** [Verified/Issues noted]

# ### 🎯 SUCCESS METRICS
# - **Issues Identified:** [Total count]
# - **Optimization Opportunities:** [Count]
# - **High Priority Tasks Created:** [Count]
# - **Task Management Integration:** [Success status]
# - **Workflow Completion Rate:** [Percentage of 8 steps completed]
# - **Next Review Recommended:** [Timeframe]

# ---
# *Complete SEO audit with task management integration and full database persistence.*

# USER QUERY: {{input}}
# AGENT SCRATCHPAD: {{agent_scratchpad}}
# """
# )


from langchain.prompts import ChatPromptTemplate

react_seo_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an advanced **ReAct SEO Optimization Agent** designed to automate SEO metadata optimization for retail product and blog pages.

## AVAILABLE TOOLS:
- seo_db_stats: Get database statistics and overview
- metadata_validator: Validate SEO titles for completeness, correctness, and issues
- seo_flagging_catalyst: Identify critical SEO issues and assign priority levels
- generate_title_improvements: Generate optimized SEO titles with confidence scores
- generate_keyword_improvements: Generate trending keywords for problematic categories
- update_trending_keywords_db: Store generated trending keywords
- update_seo_outcomes_db: Store complete audit results
- analyze_high_priority_tasks: Identify urgent SEO tasks from outcomes
- insert_high_priority_tasks: Insert high-priority tasks into database

## WORKFLOW GUIDELINES:
1. Process only records where Page_Type is 'Product' or 'Article'
2. Use current year (2025) dynamically in all checks and generations
3. Assign confidence scores (1-5) for all title improvements
4. No hallucinations - use only real data from previous steps
5. Execute steps sequentially based on previous outputs

## EXPECTED SEQUENCE:
1. Start with database analysis → 2. Validate metadata → 3. Flag issues → 
4. Generate improvements → 5. Update databases → 6. Handle priorities

## OUTPUT REQUIREMENTS:
After completion, provide summary of:
- Total records processed
- Records flagged with issues
- High-priority tasks identified
- Database update status

Think step by step. Use the most appropriate tool based on your current task and previous results.
""")
])


# Create agent
react_agent = create_react_agent(
    model=llm,
    tools=tools_all,
    prompt=react_seo_agent_prompt
)





config=RunnableConfig(configurable={"thread_id": "1"})

def run_single_agent():
    """Run single ReAct SEO agent (audit + persistence) with streaming output."""
    print("Running single ReAct SEO agent...\n")
    input_text = "Perform SEO audit and persist updates."
    try:
        # Primary streaming loop
       for chunk in react_agent.stream({"input": input_text}, config=config):
            print("Running chunck code:....\n")  # Debugging line
            print("Chunk received 👍✅:", chunk)  # Debugging line
            if isinstance(chunk, dict):
                if "messages" in chunk:
                    content = chunk["messages"][-1].content
                    if content:
                        print("🗣️ Agent:", content)
                if "actions" in chunk:
                    for act in chunk["actions"]:
                        print(f"🔧 Planning Tool: {getattr(act, 'tool', 'unknown')}")
                if "tool" in chunk:
                    print("🔧 Tool Call:", chunk["tool"])
                if "observation" in chunk:
                    print("👁️ Observation:", chunk["observation"])

        

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        print("⚠️ Streaming failed; falling back to single ainvoke.")


if __name__ == "__main__":
    run_single_agent()

