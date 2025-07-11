"""LangGraph Agents with Built-in Tools and Human-in-the-Loop Fallback"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

class AgentState(TypedDict):
    messages: List[BaseMessage]
    context: Dict[str, Any]
    agent_type: str

# Built-in Tools
@tool
def analyze_canvas(query: str, canvas_items: int = 0) -> str:
    """Analyze canvas content and provide visual insights"""
    if canvas_items > 0:
        return f"I can see {canvas_items} elements on your canvas related to: {query}"
    return "The canvas is empty. Start drawing and I'll help analyze your content!"

@tool
def tutor_help(query: str, context: str = "") -> str:
    """Provide educational assistance and explanations"""
    return f"Let me help explain: {query}. This is an important concept."

@tool
def drawing_tips(query: str, canvas_items: int = 0) -> str:
    """Suggest drawing improvements and artistic guidance"""
    if canvas_items > 5:
        return f"Great work! For '{query}', try organizing elements with better spacing and colors."
    elif canvas_items > 0:
        return f"Nice start! For '{query}', consider adding more details and colors."
    return f"For '{query}', start with main concepts, then add supporting details."

@tool
def process_docs(query: str, context: str = "") -> str:
    """Process and analyze document content"""
    return f"📄 For '{query}': organize key points visually with diagrams and summaries."

class AgentSystem:
    def __init__(self, canvas=None, api_key=None):
        self.canvas = canvas
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')
        self.llm = ChatGoogleGenerativeAI(google_api_key=self.api_key, model="gemini-1.5-flash", temperature=0.7) if self.api_key else None
        self.tools = {"analyze_canvas": analyze_canvas, "tutor_help": tutor_help, "drawing_tips": drawing_tips, "process_docs": process_docs}
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("router", self._router)
        workflow.add_node("agent", self._unified_agent)
        workflow.set_entry_point("router")
        workflow.add_edge("router", "agent")
        workflow.add_edge("agent", END)
        return workflow.compile()
    
    def _router(self, state: AgentState):
        query = state["messages"][-1].content.lower()
        if any(word in query for word in ['see', 'look', 'analyze', 'canvas', 'visual']):
            agent_type = "vision"
        elif any(word in query for word in ['draw', 'improve', 'suggest', 'art', 'sketch']):
            agent_type = "drawing"
        elif any(word in query for word in ['document', 'pdf', 'file', 'text']):
            agent_type = "document"
        else:
            agent_type = "tutor"
        return {"agent_type": agent_type}
    
    async def _get_ai_response(self, query: str, context: str = "", memory: list = None):
        if self.llm:
            try:
                # Build prompt with memory
                prompt_parts = []
                if memory:
                    for msg in memory[-2:]:  # Last 2 exchanges only
                        if msg["role"] == "user":
                            prompt_parts.append(f"Previous User: {msg['content']}")
                        else:
                            prompt_parts.append(f"Previous AI: {msg['content']}")
                
                # Simple single message approach
                full_prompt = "\n".join(prompt_parts) + f"\nContext: {context}\nCurrent Query: {query}\nResponse:"
                
                response = await self.llm.ainvoke([HumanMessage(content=full_prompt)])
                return response.content
            except Exception as e:
                print(f"API call failed: {e}")
                return None
        return None
    
    def _add_human_fallback(self, result: str) -> str:
        if len(result) < 30 or "I don't know" in result.lower():
            return f"{result}\n\n Human assistance may be needed."
        return result
    
    async def _unified_agent(self, state: AgentState):
        query = state["messages"][-1].content
        agent_type = state["agent_type"]
        canvas_items = state["context"].get("canvas_items", 0)
        
        # Try API first
        context_map = {
            "vision": f"Canvas has {canvas_items} visual elements",
            "drawing": f"Drawing context with {canvas_items} elements", 
            "document": "Document processing context",
            "tutor": f"Educational context with {canvas_items} canvas elements"
        }
        
        memory = state["context"].get("memory", [])
        ai_response = await self._get_ai_response(query, context_map.get(agent_type, ""), memory)
        
        if ai_response:
            icons = {"vision": "👁️", "tutor": "🎓", "drawing": "🎨", "document": "📄"}
            result = f"{icons.get(agent_type, '🤖')} AI: {ai_response}"
        else:
            # Fallback to built-in tools
            tool_map = {
                "vision": lambda: analyze_canvas.invoke({"query": query, "canvas_items": canvas_items}),
                "tutor": lambda: tutor_help.invoke({"query": query, "context": f"{canvas_items} elements"}),
                "drawing": lambda: drawing_tips.invoke({"query": query, "canvas_items": canvas_items}),
                "document": lambda: process_docs.invoke({"query": query, "context": ""})
            }
            result = tool_map.get(agent_type, tool_map["tutor"])()
        
        # Human fallback if need be
        result = self._add_human_fallback(result)
        return {"messages": [AIMessage(content=result)]}
    
    async def process_query(self, query: str, context: Dict = None):
        try:
            canvas_context = {"canvas_items": len(self.canvas.find_all()) if self.canvas else 0}
            canvas_context.update(context or {})
            
            state = {
                "messages": [HumanMessage(content=query)],
                "context": canvas_context,
                "agent_type": ""
            }
            
            result = await self.graph.ainvoke(state)
            return result["messages"][-1].content
            
        except Exception as e:
            return f"❌ Error: {str(e)}\n\n Human fallback: Please try rephrasing your question."