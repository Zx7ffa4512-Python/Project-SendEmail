#coding=utf8
####################################################################################################
#版本号：v1.0
#用法：配置config.ini,双击SendEmail.py运行即可
####################################################################################################
import smtplib,codecs,re,sys,warnings,base64
from os.path                import exists
from ConfigParser           import ConfigParser
from threading              import Thread,Lock
from Queue                  import Queue
from time                   import strftime,sleep
from email.mime.text        import MIMEText
from email.header           import Header
from email.mime.multipart   import MIMEMultipart

#----------------------------------------------------------------------------------------------------
#全局变量
gConfigFileStr  ='config.ini'
gMutex          =None
gErrorLog       ="ErrorLog.log"
#----------------------------------------------------------------------------------------------------





class InitCls():
    def __init__(self):
        ErrorFile=open(gErrorLog,'a')
        ErrorFile.writelines("\n\n[%s] [%s]\n%s\n"%(strftime('%x'),strftime('%X'),"-"*80))
        sys.stderr   =ErrorFile
        warnings.filterwarnings("ignore")
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
            sys.exit()
        
    def CreateConfig(self, ):
        config=ConfigParser()
        config.add_section('SMTP')
        config.add_section('SEND')
        config.add_section('MAIL')
        config.set('SMTP','Server','smtp.163.com')
        config.set('SMTP','Port','25')
        config.set('SMTP','SSL','0')
        config.set('SEND','Thread','1')
        config.set('SEND','Per_Sender','4')
        config.set('SEND','per_email_sleep','10')
        config.set('SEND','Loop_Wait_Minutes','10')
        config.set('SEND','Sender','Sender.txt')
        config.set('SEND','Receiver','Receiver.txt')
        config.set('MAIL','PlainOrHtml','html')
        config.set('MAIL','Subject','测试{%emailname%}')
        config.set('MAIL','DisplayName','Rich Park{%MAILFROM%}')
        config.set('MAIL','ForgeSource','false')
        config.set('MAIL','Content','mail.html')
        config.set('MAIL','Attachment','None')
        
        
        config.write(open(gConfigFileStr,'w'))
        #config.write(codecs.open(gConfigFileStr,'w'))
        if not exists('Sender.txt'):open('Sender.txt','a')
        if not exists('Receiver.txt'):open('Receiver.txt','a')
        self.__init__()
        
        
        
        
    @staticmethod
    def transcode(EchoStr,charsetFrom=sys.getfilesystemencoding(),charsetTo=sys.getfilesystemencoding()):
        if isinstance(EchoStr,unicode): 
            return EchoStr.encode(charsetTo)
        else:
            return EchoStr.decode(charsetFrom).encode(charsetTo)
    
    
class SendEmail():
    def __init__(self,**ql):
        self.config=ConfigParser()
        self.config.readfp(codecs.open(gConfigFileStr, "r", "utf-8-sig"))
        #self.config.readfp(open(gConfigFileStr))
        self.SenderQueue    =ql['Sender']
        self.ReceiverQueue  =ql['Receiver']
        self.Fail           =Queue()
        self.Succed         =Queue()
    def DealArg(self,inString):
        opts=re.findall('\{\%.+?\%\}',inString)
        for opt in opts:
            if opt=="{%emailname%}":
                inString=(inString).replace("{%emailname%}",self.ToUserInfo[0])
            elif opt=="{%DATE%}":
                inString=(inString).replace("{%DATE%}",strftime("%x"))
            elif opt=="{%TIME%}":
                inString=(inString).replace("{%TIME%}",strftime("%X"))
            elif opt=="{%MAILFROM%}":
                if self.ForgeSource == 'false':
                    inString=(inString).replace("{%MAILFROM%}","<"+self.FromUserInfo[0]+">")
                elif self.ForgeSource == 'true':
                    inString=(inString).replace("{%MAILFROM%}","")
                    tmp=self.SMTPServer.split('.')[-2]+'.'+self.SMTPServer.split('.')[-1]
                    inString=inString + "<"+ inString.replace(" ","_") + "@" + tmp +">"
        return inString
        
    def GetUnchangedConfig(self,):
        self.RemoteServer       =None
        self.SMTPServer         =self.config.get("SMTP","server")
        self.SMTPPort           =self.config.getint("SMTP","port")
        self.SMTPSSL            =self.config.getint("SMTP","ssl")
        self.thread             =self.config.getint("SEND","thread")
        self.per_sender         =self.config.getint("SEND","per_sender")
        self.per_email_sleep    =self.config.getint("SEND","per_email_sleep")
        self.loop_wait_minutes  =self.config.getint("SEND","Loop_Wait_Minutes")
        self.sender             =self.config.get("SEND","sender")
        self.receiver           =self.config.get("SEND","receiver")
        self.ForgeSource        =self.config.get("MAIL","forgesource")
    def GetChangedConfig(self,):
        self.subject            =self.DealArg(self.config.get("MAIL","subject"))
        self.content            =self.DealArg(open(self.config.get("MAIL","content"),'r').read())
        self.plainorhtml        =self.config.get("MAIL","plainorhtml")
        self.DisplyName         =self.config.get("MAIL","displayname")
        self.attachment         =self.config.get("MAIL","attachment").split(';')
        self.msg                = MIMEMultipart('alternative')
        self.msg['Subject']   =Header(self.subject,'utf-8')
        self.msg['From']       =Header(self.DealArg(self.DisplyName),'utf-8')
        self.msg['To']          =Header(self.ToUserInfo[0])
             
        
    def ConnectServer(self,host,port,username,password):
        SMTPServer=smtplib.SMTP()
        #SMTPServer.set_debuglevel(1)#设置是否为调试模式。默认为False，即非调试模式，表示不输出任何调试信息。 
        SMTPServer.connect(host=host,port=port)
        if self.SMTPSSL==0:
            #SMTPServer.helo()
            #SMTPServer.send(base64.encodestring(username))
            #SMTPServer.send(base64.encodestring(password))
            SMTPServer.login(username,password)
        elif self.SMTPSSL==1:
            SMTPServer.ehlo()
            SMTPServer.starttls()
            SMTPServer.ehlo()
            #SMTPServer.send(base64.encodestring(username))
            #SMTPServer.send(base64.encodestring(password))
            SMTPServer.login(username, password)
        return SMTPServer

    def StartToSend(self,):
        self.GetUnchangedConfig()
        for line in open(self.sender):
            self.SenderQueue.put(line + ";0")
        for line in open(self.receiver):
            self.ReceiverQueue.put(line)
        #----------|开始主循环|----------#
        while not self.ReceiverQueue.empty():
            if not self.SenderQueue.empty():
                self.FromUserInfo=str(self.SenderQueue.get()).split(";") #0是帐号，1是密码，2是登录失败次数
                #----------|连接服务器|----------#
                if self.FromUserInfo[2]=='0':
                    self.RemoteServer=self.ConnectServer(self.SMTPServer,self.SMTPPort,self.FromUserInfo[0],self.FromUserInfo[1])
                elif self.FromUserInfo[2]!='0':
                    self.RemoteServer=self.ConnectServer(self.SMTPServer,self.SMTPPort,self.FromUserInfo[0],self.FromUserInfo[1])
                else:
                    pass
                if self.RemoteServer == None:
                    #----------|登录失败,失败次数小于3就添加|----------#
                    print self.FromUserInfo[0]+InitCls.transcode(" --> 登录失败","utf-8")
                    if int(self.FromUserInfo[2])<=3:self.Sender.put(str(self.FromUserInfo[0]+';'+self.FromUserInfo[1]+';'+str(int(self.FromUserInfo[2])+1)))
                else:
                    #----------|登录成功，开始发送邮件|----------#
                    print self.FromUserInfo[0]+InitCls.transcode(" --> 登录成功","utf-8")
                    for per in range(0,int(self.per_sender)):
                        #----------|初始化配置|----------#
                        if self.ReceiverQueue.empty():return 0
                        self.ToUserInfo  =str(self.ReceiverQueue.get()).split('\n')
                        self.GetChangedConfig()
                        #----------|每封信延时|----------#
                        for i in range(0,5):
                            sleep(int(self.per_email_sleep)/5)
                            print '.',
                        if self.attachment[0]=='None':       #无附件
                            try:
                                self.msg.attach(MIMEText(self.content, _subtype=self.plainorhtml, _charset='utf-8'))
                                self.RemoteServer.sendmail(self.FromUserInfo[0],self.ToUserInfo,self.msg.as_string())
                                print InitCls.transcode("--> 发送到:"+self.ToUserInfo[0] + "成功!","utf-8")
                                self.Succed.put(self.ToUserInfo[0])
                            except Exception,e:
                                self.ReceiverQueue.put(self.ToUserInfo[0])
                                self.Fail.put(self.ToUserInfo[0])
                                print InitCls.transcode("--> 发送到:"+self.ToUserInfo[0] + "失败:","utf-8")+str(e)
                        else:                           #有附件
                            try:
                                for att in self.attachment:
                                    a=MIMEText(open(att,'rb').read(), 'base64', 'utf-8')
                                    a["Content-Type"] = 'application/octet-stream'
                                    a["Content-Disposition"] = 'attachment; filename="' + att + '"'
                                    self.msg.attach(a)
                                self.msg.attach(MIMEText(self.content, _subtype=self.plainorhtml, _charset='utf-8'))
                                self.RemoteServer.sendmail(self.FromUserInfo[0],self.ToUserInfo,self.msg.as_string())
                                print InitCls.transcode("--> 发送到:"+self.ToUserInfo[0] + "成功!","utf-8")
                                self.Succed.put(self.ToUserInfo[0])
                            except Exception,e:
                                self.ReceiverQueue.put(self.ToUserInfo[0])
                                self.Fail.put(self.ToUserInfo[0])
                                print InitCls.transcode("--> 发送到:"+self.ToUserInfo[0] + "失败:","utf-8")+str(e)
                    self.RemoteServer.quit()
            else:
                print InitCls.transcode("\n发件箱已用尽。\n在{"+self.sender+"}文件中填写新的发件箱。\n按[Enter]继续,输入exit停止发送:","utf-8")
                tmp=raw_input()
                if tmp=='exit':return 1
                for line in open(self.sender):
                    self.SenderQueue.put(line + ";0")
            print InitCls.transcode('\n一次循环完成，等待'+self.loop_wait_minutes+'min后发送...','utf-8')
            sleep(int(self.loop_wait_minutes)*60)
        return 0




        

def main():
    start   =InitCls()
    send    =None
    ret     =0
    try:
        if start.ready:
            send=SendEmail(Sender=Queue(),Receiver=Queue())
            ret=send.StartToSend()
    finally:
            print InitCls.transcode("\n发送结果汇报:",'utf8')
            print InitCls.transcode("|发送成功|"+"-"*31+"|未发送成功|"+"-"*29,'utf8')
            while True:
                temp=''
                if not send.Succed.empty():
                    temp="|"+str(send.Succed.get()).ljust(40)+"|"
                else:
                    temp="|"+' '.ljust(40)+"|"
                if not send.Fail.empty():
                    temp=temp+str(send.Fail.get()).ljust(40)+"|"
                else:
                    temp=temp+' '.ljust(40)+"|"
                print temp
                if send.Succed.empty() and send.Fail.empty():break
            print "-"*82
    sys.exit()


if __name__ == '__main__':main()