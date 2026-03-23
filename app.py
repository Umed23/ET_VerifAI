import streamlit as st
import time
import json
from main import app as agent_graph
from utils.processor import extract_text_from_upload 

# --- PAGE CONFIG ---
st.set_page_config(page_title="VerifAI", page_icon="🛡️", layout="wide")

# --- CSS INJECTION ---
st.markdown("""
<style>
    /* Global Background Pattern */
    .stApp {
        background-color: #0d1117;
        background-image: radial-gradient(circle at 50% top, #161b22 0%, #0d1117 100%);
        color: #c9d1d9;
    }
    
    /* Glowing Title */
    .glow-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #bd56ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(88, 166, 255, 0.3);
    }
    
    .glow-subtitle {
        text-align: center;
        color: #8b949e;
        margin-top: 5px;
        margin-bottom: 40px;
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    /* Glassmorphism Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(48, 54, 61, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    
    /* Pulsing Status Dot */
    .pulse-dot {
        height: 12px;
        width: 12px;
        background-color: #3fb950;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7);
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(63, 185, 80, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(63, 185, 80, 0); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="glow-title">🛡️ VerifAI</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="glow-subtitle">FLAGSHIP MULTI-AGENT ORCHESTRATOR</h3>', unsafe_allow_html=True)

# --- SIDEBAR STATS ---
st.sidebar.markdown('<h2><span class="pulse-dot"></span> Live System Health</h2>', unsafe_allow_html=True)
stats_placeholder = st.sidebar.empty()

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader(
    "Upload Invoice, HR Document, or Meeting Transcript",
    type=["pdf", "docx", "txt"],
    help="Files up to 5MB (Optimized for Sentinel AI)"
)

if uploaded_file:
    with st.spinner("🔄 Sentinel Orchestrator executing 6-agent pipeline..."):
        try:
            # 1. Extraction & Validation
            raw_text = extract_text_from_upload(uploaded_file)
            if not raw_text or len(raw_text.strip()) < 10:
                st.error("⚠️ Could not extract readable text. Please upload a clearer document.")
                st.stop()
                
            start_timestamp = time.time()
            
            # 2. Initialize State
            initial_state = {
                "task_id": f"VERIFAI-{int(start_timestamp)}",
                "start_time": start_timestamp,
                "raw_input": raw_text,
                "workflow_type": None,
                "extracted_data": {},
                "audit_log": [],
                "errors": [],
                "retry_count": 0,
                "correction_flag": False,
                "status": "initiated",
                "next_step": "coordinator"
            }
            
            # 3. Invoke Graph
            final_state = agent_graph.invoke(initial_state)
            
        except Exception as e:
            st.error(f"❌ System Crash: {str(e)}")
            st.stop()
    
    # --- METRIC RECOVERY ---
    audit_log = final_state.get('audit_log', [])
    last_entry = audit_log[-1] if audit_log else {}
    metrics = last_entry.get('metrics', {})
    
    # Fix 3: Fallback warning if monitor failed
    if not metrics and final_state.get('status') == 'completed':
        st.warning("⚠️ Monitoring agent did not return performance metrics.")

    autonomy_score = metrics.get('autonomy_score', 0)
    savings_per_tx = metrics.get('net_savings_usd', 0.0)
    processing_time = metrics.get('processing_time_sec', 0.0)
    
    # Fix 1: Independent ROI Logic
    manual_cost = 25.00
    ai_cost = 0.15
    improvement = ((manual_cost - ai_cost) / manual_cost) * 100 # Constant business value

    # --- TOP LEVEL STATUS & BADGE ---
    st.divider()
    w_type = final_state.get('workflow_type', 'UNKNOWN').upper()
    st.caption(f"🛡️ WORKFLOW CLASSIFICATION: **{w_type}**")
    
    status = final_state.get('status', 'failed').upper()
    if status == 'COMPLETED':
        # Fix 4: Cleaner Success Message
        st.success(f"✅ WORKFLOW COMPLETED SUCCESSFULLY")
    elif status in ['ESCALATED', 'WAITING_FOR_USER']:
        st.warning(f"✋ HUMAN-IN-THE-LOOP: Clarification Gate Triggered")
        if final_state.get("errors"):
            for err in final_state["errors"]:
                st.caption(f"Reason: ⚠️ {err}")
    else:
        st.error(f"❌ WORKFLOW {status}")

    # --- KEY METRICS ---
    col1, col2, col3, col4, col5 = st.columns(5) # Added 5th column for Confidence
    
    with col1:
        delta_msg = "Self-Healed" if final_state.get('correction_flag') else "Verified"
        st.metric("Autonomy Score", f"{autonomy_score}%", delta=delta_msg)
    
    with col2:
        st.metric("Cost Savings", f"${round(savings_per_tx, 2)}", delta=f"{round(processing_time, 2)}s")
    
    with col3:
        st.metric("Annual Impact", f"${savings_per_tx * 1000:,.0f}", delta="per 1,000 TX")
    
    with col4:
        # Fix 2: Accurate Unique Agent Progress
        unique_agents = len(set(e.get("agent", "Unknown") for e in audit_log))
        st.write(f"**Agents Executed: {unique_agents}/6**")
        st.progress(min(unique_agents / 6, 1.0))

    with col5:
        # Fix 5: Confidence Score Wow Factor
        conf = final_state.get("confidence_score", None)
        if conf is not None:
            st.metric("AI Confidence", f"{conf*100:.1f}%", delta="Extraction Quality")
        else:
            st.metric("AI Confidence", "N/A")

    # --- DATA TABS ---
    tab1, tab2, tab3 = st.tabs(["📋 Extracted JSON", "🏥 Self-Healing Log", "📑 Full Audit Trail"])
    
    with tab1:
        st.json(final_state.get('extracted_data', {}))
        if final_state.get("errors"):
            st.error("⚠️ System Violations/Errors:")
            for err in final_state["errors"]:
                st.caption(f"- {err}")
        
    with tab2:
        healing_actions = [e for e in audit_log if e.get('correction_flag') or e.get('recovery_used')]
        if healing_actions:
            st.info(f"✅ {len(healing_actions)} Autonomous corrections applied via Semantic Vector Matching.")
            for action in healing_actions:
                st.write(f"**{action.get('agent')}**: {action.get('details')}")
        else:
            st.write("Data verified against registry - no corrections needed.")

    with tab3:
        st.markdown("### 🚦 Execution Timeline")
        timeline_html = ""
        for i, entry in enumerate(audit_log, 1):
            agent = entry.get('agent', 'System')
            event = entry.get('event', 'Action')
            details = entry.get('details', 'No details.')
            t_stamp = time.ctime(entry['timestamp']) if entry.get("timestamp") else "Just now"
            
            icon = "🤖"
            if "Clarification" in agent or "Failed" in event:
                icon = "⚠️"
                border_color = "#f85149"
            elif "Matching" in agent:
                icon = "🏥"
                border_color = "#58a6ff"
            else:
                border_color = "#58a6ff"
                
            timeline_html += f"""
            <div style="border-left: 2px solid {border_color}; margin-bottom: 20px; position: relative; background: rgba(22, 27, 34, 0.4); padding: 15px 15px 15px 25px; border-radius: 0 8px 8px 0; border: 1px solid rgba(48, 54, 61, 0.5);">
                <div style="position: absolute; width: 14px; height: 14px; background: {border_color}; border-radius: 50%; left: -8px; top: 20px; box-shadow: 0 0 8px {border_color};"></div>
                <h4 style="margin:0; color:#c9d1d9; font-size: 1.1rem;">{icon} Step {i}: {agent} <span style="font-size: 0.8rem; color: #8b949e; float: right; font-weight: normal;">⏱️ {t_stamp}</span></h4>
                <p style="margin:5px 0; color:{border_color}; font-weight:bold;">{event}</p>
                <p style="margin:0; color:#8b949e;">{details}</p>
            </div>
            """
        st.markdown(timeline_html, unsafe_allow_html=True)

    # --- SIDEBAR REFRESH ---
    with stats_placeholder.container():
        st.metric("Status", status)
        st.metric("ROI Improvement", f"{round(improvement, 1)}%")

else:
    st.info("👆 Upload a document to activate the VerifAI 6-Agent pipeline.")