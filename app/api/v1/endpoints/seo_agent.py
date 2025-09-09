from typing import Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
# from app.agents.graph import workflow
from app.core.settings import get_settings
from app.services.runner import run_agent
from app.agents.agent import run_single_agent

router = APIRouter()

class AgentRequest(BaseModel):
    query: str = None



@router.post("/seo/graph")
def run_seo_graph_endpoint(req: AgentRequest):
    """Run the LangGraph with agent_1 and agent_2"""
    try:
        result=run_single_agent(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "SEO graph executed successfully", "result": result}


@router.post("/seo/form", response_class=HTMLResponse)
def run_seo_form(query: str = Form(...)):
                """Accepts a simple HTML form post and returns an HTML page with plain content."""
                try:
                                content: str = run_single_agent(query) or ""
                except Exception as e:
                                return HTMLResponse(
                                                content=f"""
                                                                <!doctype html>
                                                                <html>
                                                                <head><meta charset='utf-8'><title>SEO Analyzer - Error</title>
                                                                <link rel='stylesheet' href='/css/styles.css'>
                                                                </head>
                                                                <body>
                                                                                <main class='container'>
                                                                                        <h1>SEO Analyzer</h1>
                                                                                        <div class='panel error'>Error: {str(e)}</div>
                                                                                        <p><a class='btn' href='/'>Back</a></p>
                                                                                </main>
                                        </body></html>""",
                                                status_code=500,
                                )

                html = f"""
                <!doctype html>
                <html lang='en'>
                        <head>
                                <meta charset='utf-8' />
                                <meta name='viewport' content='width=device-width, initial-scale=1' />
                                <title>SEO Analyzer - Result</title>
                                <link rel='stylesheet' href='/css/styles.css' />
                        </head>
                        <body>
                                <main class='container'>
                                        <h1>SEO Analyzer</h1>
                                        <section class='panel'>
                                                <h2>Query</h2>
                                                <p>{query}</p>
                                        </section>
                                        <section class='panel'>
                                                <h2>Result</h2>
                                                <pre class='result'>{content}</pre>
                                        </section>
                                        <p><a class='btn' href='/'>Back</a></p>
                                </main>
                        </body>
                        </html>
                """
                return HTMLResponse(content=html)

