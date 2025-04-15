import streamlit as st

def handle_wechat_callback():
    """处理微信登录回调"""
    # 获取URL参数
    params = st.experimental_get_query_params()
    
    # 获取code和state
    code = params.get('code', [None])[0]
    state = params.get('state', [None])[0]
    
    if code and state:
        # 存储code和state到session state
        st.session_state['wechat_code'] = code
        st.session_state['wechat_state'] = state
        
        # 显示成功信息
        st.success('授权成功！请返回登录页面点击"我已完成扫码"按钮完成登录。')
    else:
        st.error("授权失败，请重试。") 