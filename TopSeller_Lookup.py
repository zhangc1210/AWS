class Product:
	def __init__(asin,title.url):
		self.asin=asin
		self.title=title
		self.url=url
		self.cnTitle=''
mapProduct={}
inPath=''
for line in open(inPath,'r'):
	res=api.browse_node_lookup(int(line),response_group='TopSellsers')
	for item in res.BrowseNodes.BrowseNode.TopItemSet.TopItem:
		if item.ASIN not in mapProduct:
			mapProduct[item.ASIN]=Product(item.ASIN,item.Title,item.DetailPageURL)
outPath=''
ouput=open(outPath,'w')
for asin in list(mapID.keys()):
	mapProduct[item.ASIN].cnTitle=BaiduTrans(mapProduct[asin].Title)
	ouput.write('%s\t%s\t%s\n\t\t%s\n' %(asin,mapID[asin].Title,mapID[asin].cnTitle,mapID[asin].DetailPageURL))
