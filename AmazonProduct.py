from amazonproduct import *
import BaiduTrans
import urllib
import sys
import types
import os
reload(sys)
sys.setdefaultencoding("utf8")
class BrowseNode:
	def __init__(self,id,name,deep):
		self.NodeID=id
		self.Name=name
		self.chName=''
		self.deep=deep
		self.Children=[]
		self.Ancestors=[]
	def __repr__(self):
		str='Deep:%d\tID:%d \tName:%s,Chinese:%s \n' % (self.deep,self.NodeID,self.Name,self.chName)
		if self.Children:
			str+= '\tChildren:['
			for child in self.Children:
				str+='%d,'%(child)
			str=str[:-1]
			str+=']\n'
		if self.Ancestors:
			str+='\tAncestors:['
			for ancestor in self.Ancestors:
				str+='%d,'% (ancestor)
			str=str[:-1]
			str+=']\n'
		return str
class Product:
	def __init__(self,asin,title,url):
		self.asin=asin
		self.title=title
		self.url=url
		self.cnTitle=''
		self.imagePath=''
		self.imageLocalPath=''
		self.brand=''
mapID={}
mapProduct={}
setBrand=set()
maxDeep=0
locale='us'
api=API(locale=locale,trycount=20)
def Init():
		global api
		api=API(locale=locale,trycount=20)
def BrowseNodeLookup(nodeID,deep):
	if maxDeep > 0 and deep >= maxDeep:
		return
	try:
		res=api.browse_node_lookup(nodeID)
	except:
		return
	sleep(0.1)
	if nodeID not in mapID:
		mapID[nodeID]=BrowseNode(nodeID,res.BrowseNodes.BrowseNode.Name.text,deep)
	else:
		mapID[nodeID].Name=res.BrowseNodes.BrowseNode.Name.text
	if deep == 0 and 'Ancestors' in dir(res.BrowseNodes.BrowseNode) :
		idRootParent=int(res.BrowseNodes.BrowseNode.Ancestors.BrowseNode.BrowseNodeId)
		mapID[nodeID].Ancestors.append(idRootParent)
		mapID[idRootParent]=BrowseNode(idRootParent,res.BrowseNodes.BrowseNode.Ancestors.BrowseNode.Name.text,-1)
	if 'Children' in dir(res.BrowseNodes.BrowseNode) :
		for child in res.BrowseNodes.BrowseNode.Children.BrowseNode:
			idChild=int(child.BrowseNodeId)
			mapID[nodeID].Children.append(idChild)
			if idChild in mapID:
				mapID[idChild].Ancestors.append(nodeID)
			else:
				mapID[idChild]=BrowseNode(idChild,child.Name.text,deep+1)
				mapID[idChild].Ancestors.append(nodeID)
				BrowseNodeLookup(idChild,deep+1)
def BrowseNodeFileTopSellersLookup(inPath):
	for line in open(inPath,'r'):
		id=int(line.split('\t')[0])
		print id
		try:
			res=api.browse_node_lookup(id,response_group='TopSellers')
			for item in res.BrowseNodes.BrowseNode.TopItemSet.TopItem:
				print item.ASIN
				if item.ASIN not in mapProduct:
					mapProduct[item.ASIN.text]=Product(str(item.ASIN.text),str(item.Title.text),str(item.DetailPageURL.text))
		except:
			continue
def BrowseNodeTopSellersLookup():
	ks=list(mapID.keys())
	for id in ks:
		try:
			res=api.browse_node_lookup(id,response_group='TopSellers')
			for item in res.BrowseNodes.BrowseNode.TopItemSet.TopItem:
				if item.ASIN not in mapProduct:
					mapProduct[item.ASIN.text]=Product(str(item.ASIN.text),str(item.Title.text),str(item.DetailPageURL.text))
		except:
			continue
def PrintAll():
	ks=list(mapID.keys())
	for key in ks:
		print mapID[key]
def SortAll():
	ks=list(mapID.keys())
	for key in ks:
		mapID[key].Ancestors.sort()
		mapID[key].Children.sort()
def GetCHName():
	ks=list(mapID.keys())
	for key in ks:
		mapID[key].chName=BaiduTrans.BaiduTrans(mapID[key].Name,fromLang=locale)
def SaveData(path):
	output=file(path,'w')
	output.write('Node Count:%d\n' %len(mapID))
	ks=list(mapID.keys())
	ks.sort()
	for key in ks:
		output.write(mapID[key].__repr__())
def GetProductInfo(strImageRootPath):
	for asin in list(mapProduct.keys()):
		try:
			res=api.item_lookup(asin,ResponseGroup='Images,ItemAttributes')
		except:
			continue
		if 'Item' in dir(res.Items) :
			if 'DetailPageURL' in dir(res.Items.Item):
				mapProduct[asin].url=str(res.Items.Item.DetailPageURL)
			if 'ItemAttributes' in dir(res.Items.Item) and 'Title' in dir(res.Items.Item.ItemAttributes):
				mapProduct[asin].title=str(res.Items.Item.ItemAttributes.Title)
			if 'LargeImage' in dir(res.Items.Item):
				mapProduct[asin].imagePath=str(res.Items.Item.LargeImage.URL)
			elif 'MediumImage' in dir(res.Items.Item):
				mapProduct[asin].imagePath=str(res.Items.Item.MediumImage.URL)
			elif 'SmallImage' in dir(res.Items.Item):
				mapProduct[asin].imagePath=str(res.Items.Item.SmallImage.URL)
			if 'ItemAttributes' in dir(res.Items.Item) and 'Brand' in dir(res.Items.Item.ItemAttributes):
				mapProduct[asin].brand=str(res.Items.Item.ItemAttributes.Brand)
				if str(res.Items.Item.ItemAttributes.Brand) not in setBrand:
					setBrand.add(str(res.Items.Item.ItemAttributes.Brand)) 
		if mapProduct[asin].imagePath != '':
			surfix=mapProduct[asin].imagePath.split('.')[-1]
			localPath=strImageRootPath+asin+'.'+surfix
			for tryc in range(20):
				try:
					if urllib.urlretrieve(mapProduct[asin].imagePath,localPath) :
						break
				except:
					continue
			mapProduct[asin].imageLocalPath=localPath
def OutputProduct(outPath):
	ouput=open(outPath,'w')
	for asin in list(mapProduct.keys()):
		if mapProduct[asin].cnTitle == '':
			mapProduct[asin].cnTitle=BaiduTrans.BaiduTrans(mapProduct[asin].title,fromLang=locale)
			if type(mapProduct[asin].cnTitle) is types.NoneType:
				ouput.write('%s\t|\t|%s\t|%s\n\t\t%s\n' %(asin,mapProduct[asin].title,mapProduct[asin].brand,mapProduct[asin].url))
			else:
				ouput.write('%s\t|%s\t|%s\t|%s\n\t\t%s\n' %(asin,mapProduct[asin].title,mapProduct[asin].cnTitle,mapProduct[asin].brand,mapProduct[asin].url))
def OutputBrand(outPath):
	ouput=open(outPath,'w')
	for brand in setBrand: 
		ouput.write('%s\n' % brand)
def OutputProductByHtml(outPath):
	output=open(outPath,'w')
	output.write('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
	<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>Product</title>
	</head><body>
	<form>
	<input type="submit" value="select" method="post"/>
	<table border="1">
	''')
	for asin in list(mapProduct.keys()):
		row='''
		<tr>
		'''
		row+='\t<td><input type="checkbox" name="'+asin+'" />'
		row+='</td>\n'
		if mapProduct[asin].cnTitle == '':
			mapProduct[asin].cnTitle=BaiduTrans.BaiduTrans(mapProduct[asin].title,fromLang=locale)
		row+='\t<td>'
		strImagePath=mapProduct[asin].imageLocalPath
		strImagePath=strImagePath[strImagePath.find('image'):]
		strImagePath=strImagePath.replace('\\','/')
		row+='<a href="'+mapProduct[asin].url+'" target="_blank"><img src="'+strImagePath+'" width="75" height="75" alt="'+asin+'"/></a>'
		row+='</td>\n'
		row+='\t<td>'
		row+=asin
		row+='</td>\n'
		row+='\t<td>'
		row+=mapProduct[asin].brand
		row+='</td>\n'
		row+='\t<td>'
		row+=mapProduct[asin].title
		row+='</td>\n'
		row+='\t<td>'
		if type(mapProduct[asin].cnTitle) is types.NoneType:
			row+=' '
		else:
			row+=mapProduct[asin].cnTitle
		row+='</td>\n'
		row+='''
		</tr>\n'''
		output.write(row)
	output.write('''
	</table>
	<input type="submit" value="select" />
	</form>
	</body>''')
def FilterNodeID(pathInput,pathOutput):
	output=open(pathOut,'w')
	for line in open(pathInput,'r'):
		if line.startswith('Deep'):
			str='ID:'
			inx=line.find(str)
			inx+=len(str)
			line=line[inx:]
			columns=line.split('\t')
			id=int(columns[0])
			comment=''.join(columns[1:])
			output.write('%d \t#%s' % (id,comment))
def ProcessProduct(pathOut,strNumSuffix):
	strImageRootPath='/image/'
	GetProductInfo(pathOut+strImageRootPath)
	OutputProduct(pathOut+'/product'+strNumSuffix+'.txt')
	OutputProductByHtml(pathOut+'/product'+strNumSuffix+'.html')
if __name__ == '__main__' :
	maxDeep=0
	#pathList='D:\\document\\a2z\\nodeid_us1.txt'
	#pathOut='D:\\document\\a2z\\TopSellers_us.html'
	'''
	pathList=sys.argv[1]
	pathOut=sys.argv[2]
	if len(sys.argv) > 3:
		locale=sys.argv[3]
	Init()
	input=file(pathList,'r')
	nLineIndex=0
	'''
	#try:
		#for line in input.readlines():
			#print line
	#	listLine=line.split('\t')
	#	nLineIndex+=1
	#	if listLine[0].isdigit():
	#		mapID.clear()
	#		num=int(listLine[0])
	#		setID.add(num)
	#		BrowseNodeLookup(num,0)
	#finally:
	#	SortAll()
	#	GetCHName()
	#	SaveData(pathOut)
	#FilterNodeID(pathList,pathOut)
	#BrowseNodeFileTopSellersLookup(pathList)
	#BrowseNodeTopSellersLookup()
	#print len(setID)
	#input=file(pathOut,'r')
	'''
	nFileIndex=82
	nLineCountPerFile=1000
	nStartLine=nFileIndex*nLineCountPerFile
	for line in input.readlines():
		if nLineIndex < nStartLine:
			nLineIndex+=1
			continue
		line=line[:-1]
		mapProduct[line]=Product('','','')
		if nLineIndex % nLineCountPerFile == nLineCountPerFile-1:
			strNumSuffix='%03d' %nFileIndex
			print strNumSuffix
			ProcessProduct(pathOut,strNumSuffix)
			nFileIndex+=1
			mapProduct.clear()
		nLineIndex+=1
	if len(mapProduct.keys()):
		strNumSuffix='%03d' %nFileIndex
		print strNumSuffix
		ProcessProduct(pathOut,strNumSuffix)
	OutputBrand(pathOut+'/brand.txt')
	'''
	#pathDir=sys.argv[1]
	'''
	pathDir='J:\\a2z'
	for filePath in os.listdir(pathDir):
		if filePath.startswith('product') and filePath.endswith('.html'):
			strSub=filePath.replace('product','')
			strSub=strSub.replace('.html','')
			if not strSub.isdigit():
				continue
			file=open(pathDir+'\\'+filePath,'r')
			fileNew=open(pathDir+'\\'+filePath+'.new','w')
			index=int(strSub)
			fileData=file.read()
			strHead=''
			strTail=''
			if index == 0:
				strHead='<body>\n<a href="product%03d.html">NextPage</a>' %(index+1)
				strTail='<a href="product%03d.html">NextPage</a>\n</body>' %(index+1)
			else :
				strHead='<body>\n<a href="product%03d.html">PreviousPage</a>\n<a href="product%03d.html">NextPage</a>' %(index-1,index+1)
				strTail='<a href="product%03d.html">PreviousPage</a>\n<a href="product%03d.html">NextPage</a>\n</body>' %(index-1,index+1)
			fileData=fileData.replace('<body>',strHead)
			fileData=fileData.replace('</body>',strTail)
			fileNew.write(fileData)
			fileNew.close()
	'''
