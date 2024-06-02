# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import datetime
import requests
import random
import json
import hashlib


def make_md5(s, encoding='utf-8'):
    # Generate salt and sign
    return hashlib.md5(s.encode(encoding)).hexdigest()


def app_key():
    # Set your own appid/appkey.
    appid = '20230404001627670'
    appkey = 'EoxT2XlBVtxxe92FKM94'
    return appid,appkey


def translate(test: str, from_lang: str = 'en', to_lang: str = 'zh'):
    # 翻译文本, pop _
    query = test.replace('_', ' ')

    # 初始化翻译语言
    from_lang = from_lang
    to_lang = to_lang

    # 构造请求地址
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    baidu_post_url = endpoint + path

    # 构造请求md5密钥
    salt = random.randint(32768, 65536)
    sign = make_md5(app_key()[0] + query + str(salt) + app_key()[1])

    # 构造请求内容字段
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': app_key()[0], 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    r = requests.post(url=baidu_post_url,params=payload,headers=headers)
    return r.json()['trans_result'][0]['dst']


def ShowTranslate():
    # 展示翻译组件
    selectbox_no = st.sidebar.selectbox(label='翻译方式',options=['英译汉','汉译英'])
    translate_type = ['en','zh'] if selectbox_no == '英译汉' else ['zh','en']
    json_text = st.sidebar.text_area("输入需要翻译的内容")
    if json_text != "":
        r = translate(test=json_text, from_lang=translate_type[0], to_lang=translate_type[1])
        st.sidebar.text_area(label='翻译结果',value=r)
    else:
        st.sidebar.info("输入翻译内容")


def IsJson(data):
    # 判断传入的是否是个json
    try:
        json.loads(data)
        return True
    except:
        return False


def ReadJson(jon: str):
    # 把文本框传入的文本首尾去空格后按json数据格式化事件名和属性信息
    json_text = jon.strip()
    json_data = json.loads(json_text)
    custom_properties_dict = dict()
    all_properties_dict = dict()
    json_time = int(str(json_data['time'])[:10])
    time_and_id_dict = {'time': str(datetime.datetime.fromtimestamp(json_time))}
    time_and_id_dict['distinct_id'] = str(json_data['distinct_id'])
    custom_properties_dict["event"] = json_data["event"]
    for i in json_data["properties"]:
        if "$" in i:
            all_properties_dict[i] = json_data["properties"][i]
        else:
            custom_properties_dict[i] = json_data["properties"][i]

    custom_propertise = pd.DataFrame(data=[custom_properties_dict], index=['上报内容'])
    all_propertise = pd.DataFrame(data=[all_properties_dict], index=['上报内容'])
    time_and_id = pd.DataFrame(data=[time_and_id_dict], index=['上报内容'])
    return custom_propertise, all_propertise, time_and_id, custom_properties_dict, json_text


def ShowJsonData():
    # 根据选择的加载工具，展示json解析的操作步骤和数据处理
    st.session_state['properties'] = 'None'
    st.title("json数据解析 全部属性")
    json_text = st.text_area("将复制的内容粘贴此处", height=300, key='test1')
    if json_text != "" and IsJson(json_text) is True:
        custom_propertise, all_propertise, time_and_id, custom_properties_dict, json_text = ReadJson(json_text)
        properties_list = list()
        for k, v in custom_properties_dict.items():
            if k == 'event':
                properties_list.append(v)
            else:
                properties_list.append(str(k))
                properties_list.append(str(v))
        properties_list.insert(0, json_text)
        st.session_state['properties'] = '\t'.join(properties_list)
        st.code(st.session_state['properties'])
        r2col1, r2col2, r2col3 = st.columns(3)
        with r2col1:
            st.markdown("###### 触发时间&用户ID")
            st.dataframe(time_and_id.T, width=400)
        with r2col2:
            st.markdown("###### 事件&自定义属性")
            st.dataframe(custom_propertise.T, height=600, width=400)
        with r2col3:
            st.markdown("###### 预置属性")
            st.dataframe(all_propertise.T, height=1000, width=400)
    elif json_text != "":
        st.warning("注意：内容不可被解析，请传入json格式数据！")
    else:
        st.info("粘贴json")


if __name__ == "__main__":
    st.set_page_config(page_title="属性重名报错解析工具", page_icon="🤣", layout="wide")
    ShowTranslate()
    ShowJsonData()