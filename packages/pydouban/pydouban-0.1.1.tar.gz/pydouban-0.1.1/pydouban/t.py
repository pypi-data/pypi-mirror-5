#encoding:utf-8
from client import DoubanClient

c1 = DoubanClient('tianyu0915@126.com','ty283406767')
print c1.login()
print c1.say('测试发送中文')


#print 'x',client.reply_topic('http://www.douban.com/group/topic/39324575/','101001001011101010010')

#for m in client.get_doumails(unread=True):
#    print m
