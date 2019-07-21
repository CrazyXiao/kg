"""

    KBQA整体流程
    1、输入问句
    2、通过实体识别模型检测问句中的实体，得到mention
    3、通过检索模型在知识库中检索mention，得到候选集（K个候选实体的所有三元组）
    4、通过属性抽取模型在候选集中挑选最合适的属性，得到唯一三元组
    5、输出答案

"""
import re
import ner
import pku_sparql_endpoint
from KB_query import question2sparql


file = "./data/task6ckbqa_train_2019.txt"
question_str = "q"
triple_str = "select"
answer_list = ['<', '"']

q_t_a_list = []
seq_q_list = []
seq_tag_list = []



if __name__ == '__main__':
    # 连接服务器
    pku = pku_sparql_endpoint.PkuBase()

    with open(file, 'r', encoding='utf-8') as f:
        q_str = ""
        t_str = ""
        a_str = ""

        for line in f:
            if line.startswith(question_str):
                q_str = line.strip()
            elif line.startswith(triple_str):
                t_str = line.strip()
            elif line[0] in answer_list:
                a_str = line.strip()

            elif not line.strip():  # new question answer triple
                q_str = re.match("q\d+[:：](.*)", q_str).group(1)
                print(q_str, t_str, a_str)
                entities = ner.entities(q_str.strip(question_str))
                if entities:
                    print("找到实体:", entities)
                    sparql = "select ?x ?y where { <%s> ?x ?y. }" % entities[0]
                    result = pku.get_sparql_result(sparql)
                    pku.print_result_to_string(result)
