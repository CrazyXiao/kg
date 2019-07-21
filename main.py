"""

    查询入口

"""
import pku_sparql_endpoint
from KB_query import question2sparql

if __name__ == '__main__':
    # 连接服务器
    pku = pku_sparql_endpoint.PkuBase()

    # 初始化自然语言到SPARQL查询的模块，参数是外部词典列表。
    q2s = question2sparql.Question2Sparql(['./KB_query/external_dict/movie_title.txt', './KB_query/external_dict/person_name.txt'])

    questions = ['周润发演了那些电影', '莫妮卡·贝鲁奇的代表作？', '被誉为万岛之国的是哪个国家？']
    for question in questions:
        my_query = q2s.get_sparql(question)
        if my_query is not None:
            result = pku.get_sparql_result(my_query)

            # print(result)
            value = pku.get_sparql_result_value(result)

            # TODO 判断结果是否是布尔值，是布尔值则提问类型是"ASK"，回答“是”或者“不知道”。
            if isinstance(value, bool):
                if value is True:
                    print('Yes')
                else:
                    print('I don\'t know. :(')
            else:
                # TODO 查询结果为空，根据OWA，回答“不知道”
                if len(value) == 0:
                    print('I don\'t know. :(')
                elif len(value) == 1:
                    print(value[0])
                else:
                    output = ''
                    for v in value:
                        output += v + u'、'
                    print(output[0:-1])

        else:
            # TODO 自然语言问题无法匹配到已有的正则模板上，回答“无法理解”
            print('I can\'t understand. :(')

        print('#' * 100)