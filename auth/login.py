import os
import random
import requests
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime
from .wechat_login import WeChatLogin

# 云片API配置
YUNPIAN_API = {
    'SINGLE_SEND': 'https://sms.yunpian.com/v2/sms/single_send.json',
    'TPL_SEND': 'https://sms.yunpian.com/v2/sms/tpl_single_send.json',
    'TPL_BATCH_SEND': 'https://sms.yunpian.com/v2/sms/tpl_batch_send.json'
}

# 加载配置
def load_config():
    return st.secrets

# 生成验证码
def generate_verification_code():
    return str(random.randint(100000, 999999))

# 发送验证码
def send_verification_code(phone_number):
    try:
        config = load_config()
        code = generate_verification_code()
        
        st.session_state['verification_code'] = code
        st.session_state['verification_time'] = datetime.now()
        
        # 根据配置决定是否使用模拟发送
        if config['yunpian']['use_mock']:  # 默认使用模拟发送
            # 模拟发送验证码，实际上只是显示在界面上（仅用于测试）
            st.info(f"模拟发送验证码到 {phone_number}，验证码为：{code}（此消息仅用于测试）")
            return True, "验证码已发送"
        else:
            # 使用真实短信服务发送
            headers = {
                'Content-type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'apikey': config['yunpian']['api_key'],
                'mobile': phone_number,
                'text': f'【NeoKline系统】您的验证码是{code}，请在5分钟内完成验证。如非本人操作，请忽略本短信。'
            }
            
            response = requests.post(
                YUNPIAN_API['SINGLE_SEND'],
                data=data,
                headers=headers,
                timeout=5  # 设置5秒超时
            )
            
            if response.status_code != 200:
                return False, f"请求失败: HTTP {response.status_code}"
                
            result = response.json()
            if result.get('code') == 0:
                return True, "验证码已发送"
            return False, f"发送失败: {result.get('msg', '未知错误')}"
            
    except requests.exceptions.Timeout:
        return False, "请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        return False, f"网络请求错误: {str(e)}"
    except Exception as e:
        return False, f"发送失败: {str(e)}"


def verify_code(input_code):
    stored_code = st.session_state.get('verification_code')
    stored_time = st.session_state.get('verification_time')
    
    if not stored_code:
        return False, "请先获取验证码"
    
    # 验证码5分钟有效期
    current_time = datetime.now()
    if (current_time - stored_time).total_seconds() > 300:
        return False, "验证码已过期，请重新获取"
    
    if input_code != stored_code:
        return False, "验证码错误"
    
    return True, "验证成功"


def login_page():
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div class="title-container">
                    <h1>📈 NeoKline系统</h1>
                </div>
            """, unsafe_allow_html=True)

    with st.container():
        config = load_config()
        
        # 创建一个普通字典来存储凭证信息
        credentials = {
            "usernames": {}
        }
        for username, user_data in config["credentials"]["usernames"].items():
            credentials["usernames"][username] = {
                "email": user_data["email"],
                "name": user_data["name"],
                "password": user_data["password"]
            }
        
        cookie_config = {
            "expiry_days": config["cookie"]["expiry_days"],
            "key": config["cookie"]["key"],
            "name": config["cookie"]["name"]
        }
        
        authenticator = stauth.Authenticate(
            credentials,
            cookie_config["name"],
            cookie_config["key"],
            cookie_config["expiry_days"]
        )

        if 'login_status' not in st.session_state:
            st.session_state['login_status'] = False
        
        if not st.session_state['login_status']:

            login_method = st.radio(
                "选择登录方式",
                ["手机验证码登录", "微信扫码登录"],
                horizontal=True,
                key="login_method"
            )
            
            if login_method == "手机验证码登录":
                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input(
                        "用户名",
                        placeholder="请输入用户名",
                        key="username_input"
                    )
                    
                    password = st.text_input(
                        "密码",
                        type="password",
                        placeholder="请输入密码",
                        key="password_input"
                    )
                    
                    phone = st.text_input(
                        "手机号码",
                        max_chars=11,
                        placeholder="请输入11位手机号",
                        key="phone_input"
                    )
                    
                    left_col, center_col, right_col = st.columns([1, 3, 1])
                    with center_col:
                        code_col, btn_col = st.columns([7, 3])
                        with code_col:
                            verification_code = st.text_input(
                                "验证码",
                                max_chars=6,
                                placeholder="请输入6位验证码",
                                key="verification_code_input"
                            )
                        with btn_col:
                            st.write("")
                            st.write("")
                            verify_button = st.form_submit_button(
                                "获取验证码",
                                type="secondary",
                                use_container_width=True
                            )
                    
                    left_space, btn_col, right_space = st.columns([1, 2, 1])
                    with btn_col:
                        login_button = st.form_submit_button(
                            "登 录",
                            type="primary",
                            use_container_width=True
                        )
                    
                    # 处理验证码发送
                    if verify_button:
                        if not phone or len(phone) != 11:
                            st.error("请输入正确的手机号码")
                        elif not phone.isdigit():
                            st.error("手机号码只能包含数字")
                        else:
                            success, message = send_verification_code(phone)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                    
                    # 处理登录
                    if login_button:
                        if not all([username, password, phone, verification_code]):
                            st.error("请填写所有必填项")
                        elif len(phone) != 11 or not phone.isdigit():
                            st.error("请输入正确的手机号码")
                        elif len(verification_code) != 6 or not verification_code.isdigit():
                            st.error("请输入正确的验证码格式")
                        else:
                            try:
                                if username in config['credentials']['usernames']:
                                    # 测试账号使用明文密码，其他账号使用哈希密码
                                    is_test_account = username == 'admin' and password == 'admin123'
                                    is_valid_password = (
                                        is_test_account or 
                                        stauth.Hasher([password]).verify(
                                            config['credentials']['usernames'][username]['password']
                                        )[0]
                                    )
                                    
                                    if is_valid_password:
                                        code_valid, code_msg = verify_code(verification_code)
                                        if code_valid:
                                            st.session_state['login_status'] = True
                                            st.session_state['username'] = username
                                            st.success("登录成功！")
                                            st.rerun()
                                        else:
                                            st.error(code_msg)
                                    else:
                                        st.error("密码错误")
                                else:
                                    st.error("用户名不存在")
                            except Exception as e:
                                st.error(f"登录失败: {str(e)}")
                
                # st.markdown("""
                #     <div class="login-info" style="text-align: center;">
                #         首次使用？请使用默认账号：admin / admin123
                #     </div>
                # """, unsafe_allow_html=True)
            
            else:  # 微信扫码登录
                wechat_login = WeChatLogin()
                
                # 生成并显示二维码
                qr_code = wechat_login.get_qr_code()
                
                # 居中显示二维码
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(qr_code, caption="微信扫码登录", width=250)
                    st.markdown("""
                        <div class="qr-info">
                            请使用微信扫描二维码登录
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 添加轮询检查状态的按钮
                    if st.button("我已完成扫码", type="primary", use_container_width=True):
                        try:
                            if 'wechat_code' in st.session_state and 'wechat_state' in st.session_state:
                                user_info = wechat_login.handle_callback(
                                    st.session_state['wechat_code'],
                                    st.session_state['wechat_state']
                                )
                                
                                st.session_state['login_status'] = True
                                st.session_state['username'] = user_info['nickname']
                                st.success("登录成功！")
                                st.rerun()
                            else:
                                st.error("请先扫描二维码")
                        except Exception as e:
                            st.error(f"登录失败: {str(e)}")
        
    return st.session_state['login_status']

# 登出功能
def logout():
    st.session_state['login_status'] = False
    st.session_state['username'] = None
    st.rerun()

if __name__ == "__main__":
    login_page() 