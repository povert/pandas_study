from model.base import *

text = {
	"光伏值，$光伏，1-20；参考值，1-5":(CRangeVal,),
	"Tunnel隧道接入网元信息列表，$网元信息":(CSingleList, CDoubleList),
	"Tunnel隧道接入网元信息列表，$$告警;保护Tunnel隧道网元信息列表，":(CSingleList, CDoubleList)
}

df_list = []
for w, tC in text.items():
	for c in tC:
		o = c(w)
		df_list.append(o.output())
r = pd.concat(df_list)
# r.head()
r.to_excel("./deal.xlsx")
