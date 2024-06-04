# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import json
import datetime
import numpy as np
import sqlite3

# 按采集方案校验
# 事件列表
EVENT_PATH: str = r'mapfile/ht_event_list.csv'
# 公共属性
PROPERTIES_PATH: str = r'mapfile/ht_properties_list.csv'
# 关键属性
KEY_PROPERTIES_PATH: str = r'mapfile/ht_key_properties_list.csv'


@st.cache_data
def radio_map_data(event_path: str, properties_path: str, key_properties_path: str):
    """
    读取csv中的事件属性方案
    :param event_path: 事件表路径
    :param properties_path: 自定义属性和预知属性表路径
    :param key_properties_path: 关键属性表路径
    :return:
    """
    event_map = pd.read_csv(event_path, encoding="utf-8")
    properties_map = pd.read_csv(properties_path, encoding="utf-8")
    with open(key_properties_path, "r", encoding="utf-8") as f:
        key_properties_map = f.read().split("\n")
    return event_map, properties_map, key_properties_map


# 封装sqlite3 操作
class SqLiteDb(object):
    """
    sqlite连接对象
    """
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def execute(self, query, params=()):
        """
        插入sql语句并提交事务
        """
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetchall(self, query):
        """
        返回查询结果
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        """
        关闭链接
        """
        self.connection.close()


def is_json(data):
    """
    判断传入的是否是个json
    """
    try:
        json.loads(data)
        return True
    except:
        return False


def read_json(jon: str, data_map: tuple):
    """
    解读json数据
    :param data_map: 校验事件属性
    :param jon: json文本
    :return: 事件和用户ID, 事件名, 关键属性, 自定义属性, 预知属性, 格式化文案
    """
    event_map, propertie_map, key_properties = data_map
    json_text = jon.strip()
    json_data = json.loads(json_text)
    # 组装用户id和触发时间
    json_time = int(str(json_data['time'])[:10])
    event_time = str(datetime.datetime.fromtimestamp(json_time))
    time_and_id_dict = {"触发时间": [event_time], "用户id": [json_data['distinct_id']]}
    time_and_id = pd.DataFrame(time_and_id_dict)
    # 组装事件名
    event_cname = event_map.loc[event_map['事件名'] == json_data['event'], "事件显示名"]
    event_name = pd.DataFrame(event_cname)
    event_name['事件名'] = json_data['event']
    event_name = event_name.loc[:, ["事件名", "事件显示名"]]
    event_name.index = [0]
    # 比对采集方案和上报自定义属性，
    propertie_map_dict = propertie_map.to_dict("list")
    key_propertie_k = [k for k, v in json_data['properties'].items() if k in key_properties]
    key_propertie_c = [propertie_map_dict["属性中文名"][propertie_map_dict["属性名"].index(k)] for k in key_propertie_k]
    key_propertie_v = [str(v) for k, v in json_data['properties'].items() if k in key_properties]
    key_propertie = pd.DataFrame([key_propertie_k, key_propertie_c, key_propertie_v],
                                 ["属性名", "属性中文名", "上报内容"])
    propertie_k = [k for k, v in json_data['properties'].items() if "$" not in k]
    propertie_c = [propertie_map_dict["属性中文名"][propertie_map_dict["属性名"].index(k)] for k in propertie_k]
    propertie_v = [str(v) for k, v in json_data['properties'].items() if "$" not in k]
    propertie = pd.DataFrame([propertie_k, propertie_c, propertie_v], ["属性名", "属性中文名", "上报内容"])
    propertie_all_k = [k for k, v in json_data['properties'].items() if "$" in k]
    propertie_all_c = [propertie_map_dict["属性中文名"][propertie_map_dict["属性名"].index(k)] for k in propertie_all_k]
    propertie_all_v = [str(v) for k, v in json_data['properties'].items() if "$" in k]
    propertie_all = pd.DataFrame([propertie_all_k, propertie_all_c, propertie_all_v],
                                 ["属性名", "属性中文名", "上报内容"])
    # 组装复制
    propertie_mp = {k: v for k, v in json_data['properties'].items() if k in key_properties}
    propertie_vl = list()
    for k, v in propertie_mp.items():
        propertie_vl.append(k)
        propertie_vl.append(v)
    event_info = [str(json_text), json_data['event']]
    # 新规范埋点通过tack_sign定位，老埋点通过关键属性定位
    is_track_sign = propertie_mp.get("track_sign", False)
    if is_track_sign:
        event_code = "新规范埋点" + '\t' + '\t'.join(event_info) + '\t' + "track_sign" + '\t' + propertie_mp.get("track_sign", "")
    else:
        event_code = "老规范埋点" + '\t' + '\t'.join(event_info) + '\t' + '\t'.join(propertie_vl)
    # 链接数据库
    # read_json_log = SqLiteDb("read_json_log.db")
    # 创建表
    # read_json_log.execute("CREATE TABLE IF NOT EXISTS event_info (track_id INTEGER PRIMARY KEY AUTOINCREMENT, distinct_id TEXT NOT NULL, event TEXT NOT NULL, track_json TEXT NOT NULL, track_time TEXT NOT NULL, read_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    # 插入数据
    # read_json_log.execute("INSERT INTO event_info (distinct_id, event, track_json, track_time) VALUES (?,?,?,?)",(str(json_data['distinct_id']), str(json_data['event']), str(json_text), str(event_time)))
    # read_json_log.close()
    return time_and_id, event_name, key_propertie, propertie, propertie_all, event_code


def clean_test_json():
    """
    清空json文本框内容
    """
    if 'test_json' in st.session_state:
        st.session_state['test_json'] = ""


def show_json_data():
    """
    根据选择的加载工具，展示json解析的操作步骤和数据处理
    """
    st.title("json解读好帮手(匹配元数据中文名)")
    json_text = st.text_area("将复制的内容粘贴此处", height=40, key='test_json')

    # 在文本框有内容的情况下，现实清空按钮
    if json_text != "" and is_json(json_text):
        st.button("清空", on_click=clean_test_json)
        event_map, properties_map, key_properties_map = radio_map_data(EVENT_PATH, PROPERTIES_PATH, KEY_PROPERTIES_PATH)
        time_and_id, event_name, key_propertie, propertie, propertie_all, event_code = read_json(jon=json_text, data_map=(event_map, properties_map, key_properties_map))
        # st.markdown("###### 查询sql")
        # st.code(sql_connet,language='sql')

        # 展示是否是新规范埋点
        if "track_sign" in key_propertie.T["属性名"].values:
            st.info("新规范埋点")
        else:
            st.warning("老规范埋点")

        st.code(event_code)
        r1com1, r1com2 = st.columns(2)
        r1com2.markdown("###### 触发时间&用户ID")
        r1com2.dataframe(time_and_id, width=580)
        r1com1.markdown("###### 事件")
        r1com1.dataframe(event_name, width=580)
        st.markdown("###### 自定义属性(关键)")
        st.dataframe(key_propertie.T, width=800)
        r2com1, r2com2 = st.columns(2)
        r2com1.markdown("###### 自定义属性")
        r2com1.dataframe(propertie.T, width=800, height=600)
        r2com2.markdown("###### 预置属性")
        r2com2.dataframe(propertie_all.T, width=800, height=600)

        # st.markdown("###### 方案外属性")
        # st.dataframe(pop_map[1])
        st.markdown(" ")
        with st.expander('格式化json（展开/折叠）'):
            st.json(json_text)
    elif json_text != "":
        st.warning("注意：内容不可被解析，请传入json格式数据！")
    else:
        st.info("粘贴json")


if __name__ == "__main__":
    st.set_page_config(page_title="json解读好帮手", page_icon="🤣", layout="wide")
    show_json_data()
