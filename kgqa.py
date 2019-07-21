from harvesttext.harvesttext import HarvestText
from rdflib import URIRef,Graph,Namespace,Literal
from pyxdameraulevenshtein import damerau_levenshtein_distance as edit_dis
import numpy as np

class NaiveKGQA:
    def __init__(self, SVOs=None, entity_mention_dict=None, entity_type_dict=None):
        self.ht_SVO = HarvestText()
        self.default_namespace = "https://github.com/blmoistawinde/"
        if SVOs:
            self.KG = self.build_KG(SVOs, self.ht_SVO)
        self.ht_e_type = HarvestText()
        self.ht_e_type.add_entities(entity_mention_dict, entity_type_dict)
        self.q_type2templates = {():["default0"],
                                 ("#实体#",):["defaultE"],
                                 ("#谓词#",):["defaultV"],
                                 ("#实体#", "#谓词#"): ["defaultEV"],
                                 ("#实体#", "#实体#"): ["defaultEE"],
                                 ("#谓词#", "#实体#"): ["defaultVE"],}

        self.q_type2search = {():lambda *args: "",
                             ("#实体#",):lambda x: self.get_sparql(x=x),
                             ("#谓词#",):lambda y: self.get_sparql(y=y),
                             ("#实体#", "#谓词#"): lambda x,y: self.get_sparql(x=x, y=y),
                             ("#实体#", "#实体#"): lambda x,z: self.get_sparql(x=x, z=z),
                             ("#谓词#", "#实体#"): lambda y,z: self.get_sparql(y=y, z=z),}
        self.q_template2answer = {"default0":lambda *args: self.get_default_answer(),
                                  "defaultE":lambda entities, answers: self.get_default_answers(entities, answers),
                                  "defaultV": lambda entities, answers: self.get_default_answers(entities, answers),
                                  "defaultEV": lambda entities, answers: self.get_default_answers(entities, answers),
                                  "defaultEE": lambda entities, answers: self.get_default_answers(entities, answers),
                                  "defaultVE": lambda entities, answers: self.get_default_answers(entities, answers),}
    def get_sparql(self,x=None,y=None,z=None,limit=None):
        quest_placeholders = ["", "", "", "", "", ""]
        for i, word in enumerate([x,y,z]):
            if word:
                quest_placeholders[i] = ""
                quest_placeholders[i + 3] = "ns1:"+word
            else:
                quest_placeholders[i] = "?x"+str(i)
                quest_placeholders[i + 3] = "?x"+str(i)

        query0 = """
            PREFIX ns1: <%s>
            select %s %s %s
            where {
            %s %s %s.
            }
            """ % (self.default_namespace, quest_placeholders[0], quest_placeholders[1], quest_placeholders[2],
                   quest_placeholders[3], quest_placeholders[4], quest_placeholders[5])
        if limit:
            query0 += "LIMIT %d" % limit
        return query0
    def get_default_answer(self,x="",y="",z=""):
        if len(x+y+z) > 0:
            return x+y+z
        else:
            return "你好"
    def get_default_answers(self,entities, answers):
        if len(answers) > 0:
            return "、".join("".join(x) for x in answers)
        else:
            return "你好"
    def build_KG(self, SVOs, ht_SVO):
        namespace0 = Namespace(self.default_namespace)
        g = Graph()
        type_word_dict = {"实体":set(),"谓词":set()}
        for (s,v,o) in SVOs:
            type_word_dict["实体"].add(s)
            type_word_dict["实体"].add(o)
            type_word_dict["谓词"].add(v)
            g.add((namespace0[s], namespace0[v], namespace0[o]))
        ht_SVO.add_typed_words(type_word_dict)
        return g
    def parse_question_SVO(self,question,pinyin_recheck=False,char_recheck=False):
        entities_info = self.ht_SVO.entity_linking(question,pinyin_recheck,char_recheck)
        entities, SVO_types = [], []
        for span,(x,type0) in entities_info:
            entities.append(x)
            SVO_types.append(type0)
        entities = entities[:2]
        SVO_types = tuple(SVO_types[:2])
        return entities, SVO_types
    def extract_question_e_types(self,question,pinyin_recheck=False,char_recheck=False):
        entities_info = self.ht_e_type.entity_linking(question,pinyin_recheck,char_recheck)
        question2 = self.ht_e_type.decoref(question,entities_info)
        return question2
    def match_template(self,question,templates):
        arr = ((edit_dis(question, template0), template0) for template0 in templates)
        dis, temp = min(arr)
        return temp
    def search_answers(self, search0):
        records = self.KG.query(search0)
        answers = [[str(x)[len(self.default_namespace):] for x in record0] for record0 in records]
        return answers
    def add_template(self, q_type, q_template, answer_function):
        self.q_type2templates[q_type].append(q_template)
        self.q_template2answer[q_template] = answer_function
    def answer(self,question,pinyin_recheck=False,char_recheck=False):
        entities, SVO_types = self.parse_question_SVO(question,pinyin_recheck,char_recheck)
        print(entities, SVO_types)
        search0 = self.q_type2search[SVO_types](*entities)
        print(search0)
        if len(search0) > 0:
            answers = self.search_answers(search0)
            templates = self.q_type2templates[SVO_types]
            question2 = self.extract_question_e_types(question,pinyin_recheck,char_recheck)
            template0 = self.match_template(question2, templates)
            answer0 = self.q_template2answer[template0](entities,answers)
        else:
            answer0 = self.get_default_answer()
        return answer0


if __name__ == "__main__":
    SVOs = [['这风云变幻八十年', '是', '中国近代半殖民地半封建社会前半段'],
     ['英国', '发动', '鸦片战争'],
     ['中国工人阶级', '开始', '形成'],
     ['太平军', '定', '南京'],
     ['英法联军', '发动', '侵略中国'],
     ['清政府', '签订', '天津条约'],
     ['清政府', '签订', '北京条约'],
     ['慈禧太后', '掌握', '清王朝政权'],
     ['这是中国半殖民地半封建社会', '形成', '中国资本主义产生时期'],
     ['清政府', '兴办', '洋务'],
     ['史', '称', '洋务运动'],
     ['俄国', '出兵', '侵占中国伊犁地区'],
     ['日本', '出兵', '侵犯中国台湾南部地区'],
     ['法国', '发动', '侵略越南'],
     ['清政府', '决定', '台湾建省'],
     ['英国', '发动', '侵略中国西藏战争'],
     ['日本', '发动', '侵略朝鲜'],
     ['台湾军民', '开展', '反割台斗争'],
     ['列强', '加紧', '强占租'],
     ['中国', '出现', '瓜分危机'],
     ['戊戌变法', '实行', '百日维新'],
     ['慈禧太后', '发动', '戊戌政变'],
     ['英', '组织', '八国联军'],
     ['清政府', '推行', '新政'],
     ['英国', '发动', '侵略中国西藏战争'],
     ['清政府', '宣布', '预备立宪'],
     ['四川', '发生', '保路运动'],
     ['这是北洋军阀统治时期', '是', '中国旧民主主义革命终结时期'],
     ['孙中山', '就任', '临时大总统'],
     ['孙中山', '让', '位于袁世凯'],
     ['国民党人', '发动', '二次革命'],
     ['日本', '进行', '战争'],
     ['日本', '提出', '企图灭亡中国二十一条要求'],
     ['袁世凯', '复辟', '帝制'],
     ['青年杂志', '改称', '新青年'],
     ['孙中山', '发动', '护法运动'],
     ['同年11月7日', '发生', '十月社会主义革命']]

    entity_type_dict = {
        '中国': '地名',
        '鸦片战争': '其他专名',
        '五四运动': '其他专名',
        '英国': '地名',
        '南京': '地名',
        '望厦': '其他专名',
        '黄埔': '地名',
        '不平等条约': '其他专名',
        '洪秀全': '人名',
        '金田': '地名',
        '太平军': '其他专名',
        '京事变': '人名',
        '第二次鸦片战争': '其他专名',
        '清政府': '机构名',
        '法四国': '地名',
        '天津': '地名',
        '北京': '地名',
        '恭亲王': '其他专名',
        '清王朝': '其他专名',
        '史称': '其他专名',
        '俄国': '地名',
        '伊犁': '地名',
        '日本': '地名',
        '台湾': '地名',
        '法国': '地名',
        '越南': '地名',
        '新疆': '地名',
        '西藏': '地名',
        '兴中会': '人名', '朝鲜': '地名', '甲午战争': '其他专名', '马关条约': '其他专名', '势力范围': '其他专名', '戊戌变法': '其他专名', '日俄': '其他专名', '东北': '地名', '东京': '地名', '孙中山': '人名', '立宪': '其他专名', '广州': '地名', '黄花岗': '地名', '四川': '地名', '保路': '人名', '武昌起义': '其他专名', '辛亥革命': '其他专名', '临时政府': '机构名', '清帝': '人名', '袁世凯': '人名', '袁': '其他专名', '德国': '地名', '山东': '地名', '新青年': '其他专名', '张勋': '人名', '废帝': '其他专名', '社会主义革命': '其他专名'
    }

    QA = NaiveKGQA(SVOs)
    questions = ["你好","孙中山干了什么事？","谁发动了什么？","清政府签订了哪些条约？",
                 "英国与鸦片战争的关系是什么？","谁复辟了帝制？"]
    # questions = ["英国与鸦片战争的关系是什么？"]
    for question0 in questions:
        print("问："+question0)
        print("答："+QA.answer(question0))
