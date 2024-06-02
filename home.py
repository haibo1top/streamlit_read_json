import streamlit as st
import requests


# 高德天气api借口和get参数
TEMPERATURE_API = "https://restapi.amap.com/v3/weather/weatherInfo?parameters"
CITY_ALL_DAY_DATA = {"key": "0b3674733074da5dd83616bc58728fdc", "city": "310000", "extensions": "all"}


def get_4day_weather(request):
    """
    取出高德天气api反馈的近4日的所需数据
    """
    today_content = request.json()["forecasts"][0]
    day1_weather, day2_weather, day3_weather, day4_weather = today_content["casts"]
    info_list = ["date", "week", "dayweather", "daytemp"]
    day1_weather = [v for k, v in day1_weather.items() if k in info_list]
    day2_weather = [v for k, v in day2_weather.items() if k in info_list]
    day3_weather = [v for k, v in day3_weather.items() if k in info_list]
    day4_weather = [v for k, v in day4_weather.items() if k in info_list]
    return day1_weather, day2_weather, day3_weather, day4_weather


def show_weekday(string):
    """
    返回状态代表的周几中文字符
    :return: 星期一,星期二,星期三...
    """
    weekday_dict = {"1": "周一", "2": "周二", "3": "周三", "4": "周四", "5": "周五", "6": "周六", "7": "周日"}
    return weekday_dict[string]


def show_work_link():
    """
    相关sa环境连接
    """
    with st.expander('嘉略环境', expanded=True):
        c11, c12, c13, c14 = st.columns(4)
        c11.markdown("[嘉略官网](http://www.jialve.cn/#/login)")
        c12.markdown("[开发环境](http://develop.jialve.cn:8079/#/login)")
        c13.markdown("[hnyh环境](http://hnyh.demo.jialve.cn/#/loginn)")
    with st.expander('sa环境', expanded=True):
        c21, c22, c23, c24 = st.columns(4)
        c21.markdown("[券商APP](http://sa.jialve.cn:8107/login/index.html?project=demoTest1)")
        c22.markdown("[手机银行/券商app](http://sa.jialve.cn:8107/login/index.html?project=demoTest2)")
        c23.markdown("[麦当劳](http://sa.jialve.cn:8107/login/index.html?project=GFapp)")
        c24.markdown("[mocha](http://sa.jialve.cn:8107/login/index.html?project=demoTest7)")
        c21.markdown("[强校验测试项目](http://sa.jialve.cn:8107/login/index.html?project=demoTest12)")
        c22.markdown("[某阅读APP测试](http://sa.jialve.cn:8107/login/index.html?project=seven_cat_test)")
        c23.markdown("[某阅读APP生产](http://sa.jialve.cn:8107/login/index.html?project=seven_cat_productio)")
        c24.markdown("[测试项目6](http://sa.jialve.cn:8107/login/index.html?project=demoTest6)")
        c21.markdown("[人保APP独有](http://sa.jialve.cn:8107/login/index.html?project=demoTest10)")
        c22.markdown("[手机银行](http://sa.jialve.cn:8107/login/index.html?project=demoTest4)")
        c23.markdown("[湖南银行测试](http://sa.jialve.cn:8107/login/index.html?project=demoTest9)")
        c24.markdown("[demoTest5](http://sa.jialve.cn:8107/login/index.html?project=demoTest5)")
        c21.markdown("[正式项目](http://sa.jialve.cn:8107/login/index.html?project=production)")
        c22.markdown("[保险行业demo](http://sa.jialve.cn:8107/login/index.html?project=insurance)")
        c23.markdown("[测试项目](http://sa.jialve.cn:8107/login/index.html?project=default)")
        c24.markdown("[demoTest5](http://sa.jialve.cn:8107/login/index.html?project=demoTest5)")


def show_wd():
    """
    百度查询借口
    """
    with st.expander('百度搜索', expanded=True):
        contcent = st.text_input("输入搜索内容")
        if contcent:
            st.link_button("搜索",f"https://www.baidu.com/s?wd={contcent}")


if __name__ == '__main__':
    st.set_page_config(page_title="哇哈哈首页", page_icon="😄")
    st.title("首页")
    # 展示近4天的天气
    today_city = "上海市"
    weather_content = requests.get(TEMPERATURE_API, params=CITY_ALL_DAY_DATA)
    day1_weather, day2_weather, day3_weather, day4_weather = get_4day_weather(weather_content)
    st.success(f"{today_city} 近4日的天气和气温")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f'{show_weekday(day1_weather[1])} {day1_weather[0][-5:]} ({day1_weather[2]})', f'{day1_weather[3]} °c')
    col2.metric(f'{show_weekday(day2_weather[1])} {day2_weather[0][-5:]} ({day2_weather[2]})', f'{day2_weather[3]} °c', f'{float(day2_weather[3])-float(day1_weather[3]):0.1f} °c')
    col3.metric(f'{show_weekday(day3_weather[1])} {day3_weather[0][-5:]} ({day3_weather[2]})', f'{day3_weather[3]} °c', f'{float(day3_weather[3])-float(day2_weather[3]):0.1f} °c')
    col4.metric(f'{show_weekday(day4_weather[1])} {day4_weather[0][-5:]} ({day4_weather[2]})', f'{day4_weather[3]} °c', f'{float(day4_weather[3])-float(day3_weather[3]):0.1f} °c')
    show_wd()
    show_work_link()
