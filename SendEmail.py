#coding=utf8
import smtplib
from sys                    import exit,getfilesystemencoding
from os.path                import exists
from ConfigParser           import ConfigParser
from threading              import Thread,Lock
from Queue                  import Queue
from time                   import strftime
from email.mime.text        import MIMEText
from email.header           import Header
from email.mime.multipart   import MIMEMultipart

#----------------------------------------------------------------------------------------------------
#全局变量
gConfigFileStr  ='config.ini'
gMutex          =None
#----------------------------------------------------------------------------------------------------





class InitCls():
    def __init__(self):
        self.ready=False
        if exists(gConfigFileStr):
            self.ViewConfig() #显示config.ini的内容
        else:
            self.CreateConfig() #创建config.ini

    def ViewConfig(self, ):
        print self.transcode(open(gConfigFileStr,'r').read(),"Utf-8")
        con=raw_input(self.transcode("配置信息如上,是否继续?[Y/n]",'utf-8'))
        if con.strip().upper()=="Y":
            self.ready = True
        else:
            exit()
        
    def CreateConfig(self, ):
        config=ConfigParser()
        config.add_section('SMTP')
        config.add_section('SEND')
        config.add_section('MAIL')
        config.set('SMTP','Server','smtp.163.com')
        config.set('SMTP','Port','25')
        config.set('SMTP','SSL','0')
        config.set('SEND','Thread','1')
        config.set('SEND','Sender','Sender.txt')
        config.set('SEND','Receiver','Receiver.txt')
        config.set('MAIL','PlainOrHtml','html')
        config.set('MAIL','Subject','测试')
        config.set('MAIL','Content','mail.html')
        config.set('MAIL','Attachment','app.rar')
        config.write(open(gConfigFileStr,'w'))
        self.__init__()
        
        
        
        
    @staticmethod
    def transcode(EchoStr,charsetFrom=getfilesystemencoding(),charsetTo=getfilesystemencoding()):
        if isinstance(EchoStr,unicode): 
            return EchoStr.encode(charsetTo)
        else:
            return EchoStr.decode(charsetFrom).encode(charsetTo)
    
    
class SendEmail():
    def __init__(self,**ql):
        self.config=ConfigParser()
        self.config.readfp(open(gConfigFileStr))
        self.Sender=ql['Sender']
        self.Receiver=ql['Receiver']
        for line in open(self.config.get("SEND","sender")):
            self.Sender.append(line)
        for line in open(self.config.get("SEND","receiver")):
            self.Receiver.put(line)
            
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = Header(self.config.get("MAIL","subject"),'utf-8')
        self.msg['From']    = Header(self.config.get("MAIL","DisplyName"),'utf-8')
        
    def fnSendEmail(self,):
        pass
        mutex.acquire()#关键代码开始
        pass
        mutex.release()#关键代码结束
        self.x=a+b
    def GetVal(ValName):
        #----------------------------------------------------------------------------------------------------
        #name,email,url,random
        #----------------------------------------------------------------------------------------------------
        pass


class MyThread(Thread):
        def __init__(self, func, args, name=""):
            Thread.__init__(self)
            self.name = name
            self.func = func
            self.args = args
        
        def run(self):  #重写Thread类中的run
            apply(self.func,self.args)


        

def main():
    start   =InitCls()
    send    =None
    t       =None
    if start.ready:
        send=SendEmail(Sender=[],Receiver=Queue())
        gMutex = Lock()
        t = MyThread(send.fnSendEmail,())
        t.start()
    #----------------------------------------------------------------------------------------------------
    #显示效果
    #----------------------------------------------------------------------------------------------------
    print send.x
    
    t.join()


if __name__ == '__main__':main()