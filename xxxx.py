




xx = [ ['goodnight_（梅艳芳歌曲）', '10000'], ['香港的女儿', '10'], ['MINI猫', '10000'], ['梅艳芳', '0'],]

b = sorted(xx,key=lambda x: (x[1]))
print(b)


# with open("./data/pkubase-full.txt", "r", encoding="utf8") as f:
#     for line in f:
#         line = line.strip()
#         entry, attr, xxx = line.split("\t")
#         print(entry, attr, xxx.strip().strip("."))