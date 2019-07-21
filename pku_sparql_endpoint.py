"""

    PKU BASE的在线查询终端

"""

import json
from collections import OrderedDict
import GStoreConnector

IP = "pkubase.gstore-pku.com"
Port = 80
username = "endpoint"
password = "123"

class PkuBase:
    def __init__(self):
        self.sparql_conn = GStoreConnector.GstoreConnector(IP, Port, username, password)

    def get_sparql_result(self, query):
        return json.loads(self.sparql_conn.query("pkubase", "json", query, "GET"))


    def get_attrs(self, query):
        result = self.get_sparql_result(query)
        query_head, query_result = self.parse_result(result)

        if not query_head or not query_result:
            return []
        else:
            res = []
            for qr in query_result:
                res.append([value for _, value in qr.items()])
            return res

    @staticmethod
    def parse_result(query_result):
        """
        解析返回的结果
        :param query_result:
        :return:
        """
        try:
            query_head = query_result['head']['vars']
            query_results = []
            for r in query_result['results']['bindings']:
                temp_dict = OrderedDict()
                for h in query_head:
                    temp_dict[h] = r[h]['value']
                query_results.append(temp_dict)
            return query_head, query_results
        except KeyError:
            return None, query_result

    def print_result_to_string(self, query_result):
        """
        直接打印结果，用于测试
        :param query_result:
        :return:
        """
        query_head, query_result = self.parse_result(query_result)

        if not query_head or not query_result:
            print('知识库中找不到对应实体。')
        else:
            # for h in query_head:
            #     print (h)
            print([value for qr in query_result for _, value in qr.items()])
            # for qr in query_result:
            #     for _, value in qr.items():
            #         print (value, ' ',)
            #     print()

    def get_sparql_result_value(self, query_result):
        """
        用列表存储结果的值
        :param query_result:
        :return:
        """
        query_head, query_result = self.parse_result(query_result)
        if query_head is None:
            return query_result
        else:
            values = list()
            for qr in query_result:
                for _, value in qr.iteritems():
                    values.append(value)
            return values

# TODO 用于测试
if __name__ == '__main__':
    endpoint = PkuBase()
    sparql = "select ?x ?y where \
                 { \
                    <北京大学> ?x ?y. \
                 }"
    result = endpoint.get_sparql_result(sparql)
    print(result)
    endpoint.print_result_to_string(result)