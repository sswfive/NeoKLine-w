import streamlit as st

def single_content_qa(content):
    img_path = content['img'][0]['value']
    with st.container(border=True):
        j1, j2, j3 = st.columns([2, 2, 2])
        j2.image('assets/deepseek.png')
        i1, i2 = st.columns([4, 1])
        extra_info = i1.text_area('请填写您对当前结果的问题或对场景的补充描述，让DeepSeek帮你分析！',
                                  value='分析一下这个图的走势，并对下一天进行分析，给出一个0到1之间的上涨概率')
        if i2.button('问答交流'):
            base_system = f"你现在是一名资深的股票分析师，请根据这张图以及用户的提问进行分析"
            single_img_one_round_qa_view(base_system, img_path, extra_info)

def single_img_one_round_qa_view(system, img_path, extra_info):
    from llm.siliconflow import get_stream_dsvl2_response
    from llm.siliconflow import image_to_base64

    img_base64 = image_to_base64(img_path)
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "text": system,
                    "type": "text"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "image_url": {
                        "detail": "auto",
                        "url": f"data:image/png;base64,{img_base64}"  # 使用 Base64 编码的shap图片
                    },
                    "type": "image_url"
                },
                {
                    "text": f"{extra_info}",
                    "type": "text"
                }
            ]
        }
    ]
    with st.expander('DeepSeek分析结果', expanded=True):
        st.write_stream(get_stream_dsvl2_response(messages))