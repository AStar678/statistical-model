import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_month_list(year, endYear, month2024_list):
    """
    根据年份生成对应的月份列表
    :param year: 当前年份
    :param endYear: 结束年份
    :param month2024_list: 2024年的月份列表
    :return: 月份列表
    """
    if year == endYear and endYear == 2024:
        return month2024_list
    return list(range(1, 13))


def format_month(month):
    """
    将月份格式化为两位字符串
    :param month: 月份
    :return: 格式化后的月份字符串
    """
    return str(month).zfill(2)


def get_html_content(url):
    """
    发送请求获取网页内容
    :param url: 请求的URL
    :return: 网页内容或None
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
    }
    try:
        response = requests.get(url, headers=header, stream=True, timeout=(20, 20))
        response.raise_for_status()  # 检查响应状态码
        return response.content
    except requests.RequestException as e:
        print(f"请求 {url} 失败: {e}")
        return None


def parse_html(bs):
    """
    解析HTML内容,提取数据
    :param bs: BeautifulSoup对象
    :return: 解析后的数据列表和列名列表
    """
    table = bs.find('table', class_='b')
    if table is None:
        return [], []
    columns_bs = table.find_all('b')
    td_bs = table.find_all('td')

    columns_list = [col.text for col in columns_bs]
    dayLength = len(td_bs[len(columns_bs):]) // len(columns_bs)

    t_list = []
    for i in range(dayLength):
        t_list_unit = []
        for x in range(len(columns_bs)):
            text = td_bs[len(columns_bs) + i * len(columns_bs) + x].text
            t_list_unit.append(text.replace('\r', '').replace('\n', '').replace(' ', ''))
        t_list.append(t_list_unit)
    return t_list, columns_list


def getData(city, startYear, endYear, month2024_list, df):
    """
    主函数，获取指定城市和时间范围内的数据
    :param city: 城市名称
    :param startYear: 开始年份
    :param endYear: 结束年份
    :param month2024_list: 2024年的月份列表
    :param df: 存储数据的DataFrame
    :return: 合并后的数据和失败列表
    """
    fail_list = []
    for year in tqdm(range(startYear, endYear), unit='年', desc='年'):
        month_list = get_month_list(year, endYear, month2024_list)
        for month in month_list:
            month_str = format_month(month)
            url = f'http://www.tianqihoubao.com/lishi/{city}/month/{year}{month_str}.html'

            html_content = get_html_content(url)
            if html_content is None:
                fail_list.append([city, year, month])
                continue

            bs = BeautifulSoup(html_content, 'lxml')
            t_list, columns_list = parse_html(bs)
            if not t_list or not columns_list:
                fail_list.append([city, year, month])
                continue

            t_df = pd.DataFrame(t_list, columns=columns_list)
            t_df['城市'] = city
            df = pd.concat([df, t_df], ignore_index=True)
    return df, fail_list


if __name__ == "__main__":
    #citys = ['','']
    startYear = 2019
    endYear = 2024
    month2024_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12]

    city = "changchun"
    # 爬取结果存取到df对象中
    df = pd.DataFrame()

    df, fail_list = getData(city, startYear, endYear, month2024_list, df)
    while len(fail_list) > 8:
        df, fail_list = getData(city, startYear, endYear, month2024_list, df)

    df = df.sort_values(by='日期').reset_index(drop=True)
    # 保存为csv文件
    df.to_csv(f'{city}/origin.csv', index=False)