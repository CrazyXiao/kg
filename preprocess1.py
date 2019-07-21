import json
res = {}
with open("./data/pkubase-mention2ent.txt", "r", encoding="utf8") as f:
    for line in f:
        line = line.strip()
        try:
            mention, entity, value = line.split('\t')
            # print(mention, entity)
            if mention not in res:
                res[mention] = [(entity,value)]
            else:
                res[mention].append((entity, value))
        except Exception as ex:
            continue


with open("./input/mention2ent.txt", "w", encoding="utf8") as f:
    json.dump(res, f, ensure_ascii=False)