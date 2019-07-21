"""
    实体链接

"""

import json
import requests
from lxml import etree
url_pre = "http://shuyantech.com/api/entitylinking/cutsegment?q=%s"

def request(sent):
    r = requests.get(url_pre % (sent))
    return r.json()


def entities(sent):
    """
        获取实体链接
    """
    data = request(sent)
    res = []
    if not data['entities']:
        return res
    for xx in data['entities']:
        res.append(xx[1])
    return res


def entities2(sent):
    """
        获取实体链接
    """
    r = requests.post("http://shuyantech.com/api/entitylinking/", data={"p": sent})
    html = etree.HTML(r.text)
    xxx = html.xpath("//span[@class='dyn']/a/@href")
    return [x.strip('http://shuyantech.com/cndbpedia/search?entity=') for x in xxx]
