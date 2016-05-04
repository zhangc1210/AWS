#coding=utf8
import sys
reload(sys)
sys.setdefaultencoding("utf8")

import httplib
import hashlib
import urllib
import random
import json

appid = '20160313000015392'
secretKey = 'MCmBwJkXJRqswDFwv2I5'
urlPrefix = '/api/trans/vip/translate'

def BaiduTrans(input,fromLang='en',toLang='zh'):
	httpClient = None
	salt = random.randint(1, 655360000)
	try:
		sign = appid+input+str(salt)+secretKey
		sign = hashlib.new('md5',sign).hexdigest()
		myurl = urlPrefix+'?appid='+appid+'&q='+urllib.quote(input)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

		httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
		httpClient.request('GET', myurl)

		#response是HTTPResponse对象
		response = httpClient.getresponse()
		decodeStr=json.loads(response.read())
		return decodeStr['trans_result'][0]['dst']
	except Exception, e:
		print e
	finally:
		if httpClient:
			httpClient.close()
if __name__ == '__main__':
	BaiduTrans('amazon')