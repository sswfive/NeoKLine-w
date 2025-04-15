import os
import json
import time
import uuid
import requests
import qrcode
import streamlit as st
from io import BytesIO
from urllib.parse import quote

class WeChatLogin:
    def __init__(self):
        self.config = st.secrets
        self.app_id = self.config['wechat']['app_id']
        self.app_secret = self.config['wechat']['app_secret']
        self.redirect_uri = self.config['wechat']['redirect_uri']
        
    def generate_state(self):
        """生成随机state用于防止CSRF攻击"""
        return str(uuid.uuid4())
    
    def get_qr_code(self):
        """生成微信登录二维码"""
        state = self.generate_state()
        st.session_state['wechat_state'] = state
        
        # URL编码redirect_uri
        encoded_redirect_uri = quote(self.redirect_uri, safe='')
        
        # 构建微信授权URL
        auth_url = (
            f"https://open.weixin.qq.com/connect/qrconnect"
            f"?appid={self.app_id}"
            f"&redirect_uri={encoded_redirect_uri}"
            f"&response_type=code"
            f"&scope=snsapi_login"
            f"&state={state}#wechat_redirect"
        )
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(auth_url)
        qr.make(fit=True)
        
        # 将二维码转换为图片
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = img_buffer.getvalue()
        
        return img_str
    
    def get_access_token(self, code):
        """通过code获取access_token"""
        url = (
            f"https://api.weixin.qq.com/sns/oauth2/access_token"
            f"?appid={self.app_id}"
            f"&secret={self.app_secret}"
            f"&code={code}"
            f"&grant_type=authorization_code"
        )
        
        response = requests.get(url)
        result = response.json()
        
        if 'errcode' in result:
            raise Exception(f"获取access_token失败：{result['errmsg']}")
            
        return result
    
    def get_user_info(self, access_token, openid):
        """获取用户信息"""
        url = (
            f"https://api.weixin.qq.com/sns/userinfo"
            f"?access_token={access_token}"
            f"&openid={openid}"
        )
        
        response = requests.get(url)
        result = response.json()
        
        if 'errcode' in result:
            raise Exception(f"获取用户信息失败：{result['errmsg']}")
            
        return result
    
    def handle_callback(self, code, state):
        """处理微信回调"""
        # 验证state
        if state != st.session_state.get('wechat_state'):
            raise Exception("Invalid state")
            
        # 获取access_token
        token_info = self.get_access_token(code)
        
        # 获取用户信息
        user_info = self.get_user_info(
            token_info['access_token'],
            token_info['openid']
        )
        
        return user_info 