"""
    预处理
"""

import re
import ner
import json
import pku_sparql_endpoint
from KB_query import question2sparql


question_str = "q"
triple_str = "select"
answer_list = ['<', '"']

q_t_a_list = []
seq_q_list = []
seq_tag_list = []

mention2ent = json.load(open("./input/mention2ent.txt", "r", encoding="utf8"))

if __name__ == '__main__':
    # 连接服务器
    pku = pku_sparql_endpoint.PkuBase()

    data_obj = {}


    with open("./data/task6ckbqa_train_2019.txt", 'r', encoding='utf-8') as f:
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

                if q_str in data_obj:
                    continue

                print(q_str, t_str, a_str)
                entities = ner.entities2(q_str.strip(question_str))
                print(entities)
                if entities:

                    data_obj[q_str] = {}

                    for entity in entities:
                        if '（' in entity:
                            entity = '_（'.join(entity.split('（'))
                        result = pku.get_attrs("select ?x ?y where { <%s> ?x ?y. }" % entity)
                        if not result:
                            print("知识库中找不到对应实体：", entity)
                            n_entity = entity.split('_（')[0]
                            if n_entity in mention2ent:
                                for xx in sorted(mention2ent[n_entity],key=lambda x: (x[1])):
                                    result = pku.get_attrs("select ?x ?y where { <%s> ?x ?y. }" % xx[0])
                                    if not result:
                                        print("知识库中再次找不到对应实体：", xx[0])
                                    else:
                                        print("找到实体:", xx[0])
                                        data_obj[q_str][xx[0]] = result
                                        break
                        else:
                            print("找到实体:", entity)
                            data_obj[q_str][entity] = result
                else:
                    print("error: 找不到实体")


    with open("./input/training_entity.txt", "w", encoding="utf8") as f:
        json.dump(data_obj, f, ensure_ascii=False)