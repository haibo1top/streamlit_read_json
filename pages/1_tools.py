# -*- coding:utf-8 -*-
import streamlit as st
import pandas as pd
import json
import datetime
import numpy as np


def clean_str_concent():
    if 'str_concent' in st.session_state:
        st.session_state['str_concent'] = ""
        st.text(st.session_state['str_concent'])


def show_tool_strlen():
    with st.expander('计算STRING字节长度', expanded=True):
        str_encode = st.selectbox("选择字符串编码", options=["utf-8", "gb2312", "gbk"], )
        str_concent = st.text_area("输入需要计算的STRING内容", key='str_concent')
        if str_concent:
            str_len_b = len(str_concent.encode(str_encode))
            st.write(f"字符串长度: {str_len_b} 字节")
            st.button("清空", on_click=clean_str_concent)


if __name__ == "__main__":
    st.set_page_config(page_title="小工具", page_icon="🤣")
    show_tool_strlen()