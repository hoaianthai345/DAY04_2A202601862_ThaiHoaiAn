import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #F2EFE9;
    }

    h1 {
        color: #3E3C38;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Clean chat messages */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1rem;
        background-color: #E8E4DB;
        border: 1px solid #D4CFC4;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    
    div[data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        border: 1px solid #C4BEB1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Style the expander */
    [data-testid="stExpander"] {
        border: 1px solid #D4CFC4 !important;
        border-radius: 8px !important;
        background-color: #F2EFE9 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stExpander"] summary {
        color: #5C5851 !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Research Agent</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Cấu hình Hệ thống")
    st.markdown("---")
    provider_name = st.selectbox("Provider", ["groq", "openrouter", "openai", "anthropic", "gemini"])
    version = st.text_input("Phiên bản (Version)", "v0")
    st.markdown("---")
    st.caption("Day 04 Lab v2 - Research Agent")

system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"

if not system_prompt_path.exists() or not tools_path.exists():
    st.error("Missing system_prompt.md or tools.yaml")
    st.stop()

system_prompt = system_prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_path)
openai_tools = to_openai_tools(tool_declarations)

try:
    provider = make_provider(provider_name)
    model = getattr(provider, "default_model", None)
except Exception as e:
    st.error(f"Error loading provider: {e}")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "rounds" in msg:
            with st.expander("System Trace"):
                for r in msg["rounds"]:
                    st.write(f"**Round {r.get('round', '?')}**")
                    if r.get("tool_calls"):
                        st.write("Tool Calls:")
                        st.json(r["tool_calls"])
                    if r.get("tool_results"):
                        st.write("Results:")
                        st.json(r["tool_results"])

user_text = st.chat_input("Bạn cần tìm thông tin gì?")
if user_text:
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    messages = [
        {"role": "system", "content": system_prompt},
    ]
    
    # Only keep last 5 turns of conversation context
    for msg in trim_history(st.session_state.history[:-1], 5):
        # We need to map history dicts back to standard message format expected by provider
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_text})

    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=4,
                )
                assistant_text = result.get("assistant_text", "")
                
                # Hiển thị text trả lời
                st.write(assistant_text)
                
                # Trực quan hóa trace tool
                if result.get("rounds"):
                    with st.expander("System Trace"):
                        for r in result["rounds"]:
                            st.write(f"**Round {r.get('round', '?')}**")
                            if r.get("tool_calls"):
                                st.write("Tool Calls:")
                                st.json(r["tool_calls"])
                            if r.get("tool_results"):
                                st.write("Results:")
                                st.json(r["tool_results"])
                
                # Lưu vào lịch sử phiên
                record = {
                    "role": "assistant", 
                    "content": assistant_text,
                    "rounds": result.get("rounds", [])
                }
                st.session_state.history.append(record)

            except Exception as e:
                st.error(f"Lỗi: {e}")
