#encoding=utf-8
'''
Created on 2012-11-7

@author: Steven
http://www.lifeba.org
基于BaseHTTPServer的http server实现，包括get，post方法，get参数接收，post参数接收。
'''
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import io,shutil  
import urllib,time
import os
import getopt,string
rootPath='j:\\a2z'
selectItemFile=open('j:\\a2z\\selectItem.txt','a')
class MyRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.process(2)

	def do_POST(self):
		self.process(1)
		
	def process(self,type):
		content=''
		if type==1:#post方法，接收post参数
			datas = self.rfile.read(int(self.headers['content-length']))
			datas = urllib.unquote(datas).decode("utf-8", 'ignore')#指定编码方式
			datas = transDicts(datas)#将参数转换为字典
			for key in datas.keys():
				content += key
				content += '\r\n'
		action=self.path
		if '?' in self.path:
			query = urllib.splitquery(self.path)
			action = query[0] 

			if query[1]:#接收get参数
				for qp in query[1].split('&'):
					kv = qp.split('=')
					content+= kv[0]+"\r\n"
		if content != '':
			selectItemFile.write(content)
			selectItemFile.flush()
		#指定返回编码
		mimeType='text/html'
		if self.path.endswith('jpeg') or self.path.endswith('jpg'):
			mimeType='image/jpeg'
		elif self.path.endswith('png'):
			mimeType='image/png'
		elif self.path.endswith('gif'):
			mimeType='image/gif'
		action=rootPath+action
		file=open(action,'rb')
		self.send_response(200)  
		self.send_header("Content-type", mimeType)
		self.send_header("Content-Length", str(os.path.getsize(action)))
		self.end_headers()  
		shutil.copyfileobj(file,self.wfile)
		file.close()
def transDicts(params):
	dicts={}
	if len(params)==0:
		return
	params = params.split('&')
	for param in params:
		dicts[param.split('=')[0]]=param.split('=')[1]
	return dicts
	   
if __name__=='__main__':
	
	try:
		server = HTTPServer(('', 8000), MyRequestHandler)
		print 'started httpserver...'
		server.serve_forever()

	except KeyboardInterrupt:
		server.socket.close()
	
	pass
