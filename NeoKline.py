import streamlit as st
from auth.login import login_page

# 页面配置
st.set_page_config(
    page_title="股票分析系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/neokline',
        'Report a bug': "https://github.com/yourusername/neokline/issues",
        'About': "# 股票分析系统\n这是一个基于Streamlit的股票分析系统。"
    }
)

# 自定义样式
st.markdown("""
<style>
    /* 重置背景色 */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    /* 输入框样式 */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 0.5rem 1rem !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus {
        border-color: #00a8e8 !important;
        box-shadow: 0 0 0 1px #00a8e8 !important;
    }
    
    /* 按钮样式 */
    .stButton button {
        background: linear-gradient(45deg, #00a8e8, #00e1d9) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 168, 232, 0.3) !important;
    }
    
    /* 标题样式 */
    h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* 表单容器样式 */
    .stForm {
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* 警告消息样式 */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* 成功/错误消息样式 */
    .element-container .stAlert {
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-radius: 8px !important;
    }
    
    .element-container .stSuccess {
        background-color: rgba(40, 167, 69, 0.2) !important;
        border-color: rgba(40, 167, 69, 0.3) !important;
    }
    
    .element-container .stError {
        background-color: rgba(220, 53, 69, 0.2) !important;
        border-color: rgba(220, 53, 69, 0.3) !important;
    }
    
    /* 标签样式 */
    .stTextInput label, .stSelectbox label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 帮助文本样式 */
    .stTextInput .help {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.875rem !important;
        margin-top: 0.25rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 主程序
def main():
    if not login_page():
        st.stop()
    else:
        st.sidebar.success(f"欢迎回来，{st.session_state['username']}！")
        if st.sidebar.button("退出登录"):
            st.session_state['login_status'] = False
            st.rerun()

if __name__ == "__main__":
    main()
