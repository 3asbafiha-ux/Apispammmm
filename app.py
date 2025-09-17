#user_id2:password2
#user_id3:password3

import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, xKEys, base64, datetime, re, socket, threading
from protobuf_decoder.protobuf_decoder import Parser
from black9 import *
from black9 import xSendTeamMsg
from black9 import Auth_Chat
from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from flask import Flask, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

# قاموس لتخزين جميع العملاء المتصلين
connected_clients = {}
connected_clients_lock = threading.Lock()

# قاموس لتخزين أهداف السبام النشطة
active_spam_targets = {}
active_spam_lock = threading.Lock()

# إنشاء تطبيق Flask
app = Flask(__name__)

def AuTo_ResTartinG():
    time.sleep(6 * 60 * 60)
    print('\n - AuTo ResTartinG The BoT ... ! ')
    p = psutil.Process(os.getpid())
    for handler in p.open_files():
        try:
            os.close(handler.fd)
        except Exception as e:
            print(f" - Error CLose Files : {e}")
    for conn in p.connections():
        try:
            if hasattr(conn, 'fd'):
                os.close(conn.fd)
        except Exception as e:
            print(f" - Error CLose Connection : {e}")
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)
       
def ResTarT_BoT():
    print('\n - ResTartinG The BoT ... ! ')
    p = psutil.Process(os.getpid())
    open_files = p.open_files()
    connections = p.connections()
    for handler in open_files:
        try:
            os.close(handler.fd)
        except Exception:
            pass           
    for conn in connections:
        try:
            conn.close()
        except Exception:
            pass
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)

def GeT_Time(timestamp):
    last_login = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = now - last_login   
    d = diff.days
    h , rem = divmod(diff.seconds, 3600)
    m , s = divmod(rem, 60)    
    return d, h, m, s

def Time_En_Ar(t): 
    return ' '.join(t.replace("Day","يوم").replace("Hour","ساعة").replace("Min","دقيقة").replace("Sec","ثانية").split(" - "))
    
Thread(target = AuTo_ResTartinG , daemon = True).start()

# قراءة الحسابات من ملف accs.txt
ACCOUNTS = []

def load_accounts_from_file(filename="accs.txt"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):  # تجاهل الأسطر الفارغة والتعليقات
                    # افتراض أن التنسيق هو token:user_id أو user_id:token
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            # افتراض أن الجزء الأول هو user_id والثاني هو token/password
                            account_id = parts[0].strip()
                            password = parts[1].strip()
                            accounts.append({'id': account_id, 'password': password})
                    else:
                        # إذا لم يكن هناك :، افتراض أن السطر كله هو user_id فقط
                        accounts.append({'id': line.strip(), 'password': ''})
        print(f"تم تحميل {len(accounts)} حساب من {filename}")
    except FileNotFoundError:
        print(f"ملف {filename} غير موجود!")
    except Exception as e:
        print(f"حدث خطأ أثناء قراءة الملف: {e}")
    
    return accounts

# تحميل الحسابات من الملف
ACCOUNTS = load_accounts_from_file()

def infinite_spam_worker(target_id):
    """دالة العمل لإرسال سبام لا نهائي إلى هدف معين"""
    print(f"🚀 بدء السبام اللانهائي على الهدف: {target_id}")
    
    while True:
        with active_spam_lock:
            if target_id not in active_spam_targets:
                print(f"⏹️ توقف السبام على الهدف: {target_id}")
                break
                
        try:
            send_spam_from_all_accounts(target_id)
            time.sleep(0.1)  # وقت انتظار قصير بين كل دورة سبام
        except Exception as e:
            print(f"❌ خطأ في السبام اللانهائي على {target_id}: {e}")
            time.sleep(1)

def send_spam_from_all_accounts(target_id):
    """إرسال سبام من جميع الحسابات المتصلة"""
    with connected_clients_lock:
        for account_id, client in connected_clients.items():
            try:
                # التحقق من أن العميل لديه اتصال نشط
                if (hasattr(client, 'CliEnts2') and client.CliEnts2 and 
                    hasattr(client, 'key') and client.key and 
                    hasattr(client, 'iv') and client.iv):
                    
                    # إرسال السبام من الحساب
                    for i in range(10):  # تقليل عدد المحاولات لتجنب الأخطاء
                        try:
                            client.CliEnts2.send(SPamSq(target_id, client.key, client.iv))
                        except (BrokenPipeError, ConnectionResetError, OSError) as e:
                            print(f"🔌 خطأ اتصال للحساب {account_id}: {e}")
                            break
                        except Exception as e:
                            print(f"⚠️ خطأ في الإرسال من الحساب {account_id}: {e}")
                            break
                    # print(f"✅ تم إرسال السبام إلى {target_id} من الحساب {account_id}")
                else:
                    print(f"🔴 اتصال الحساب {account_id} غير نشط")
            except Exception as e:
                print(f"❌ خطأ في إرسال السبام من الحساب {account_id}: {e}")
            
class FF_CLient():

    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.Get_FiNal_ToKen_0115()     
            
    def Connect_SerVer_OnLine(self , Token , tok , host , port , key , iv , host2 , port2):
            global CliEnts2 , DaTa2 , AutH
            try:
                self.AutH_ToKen_0115 = tok    
                self.CliEnts2 = socket.create_connection((host2 , int(port2)))
                self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))                  
            except:pass        
            while True:
                try:
                    self.DaTa2 = self.CliEnts2.recv(99999)
                    if '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:	         	    	    
                            self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                            self.AutH = self.packet['5']['data']['7']['data']
                    
                except:pass    	
                                                            
    def Connect_SerVer(self , Token , tok , host , port , key , iv , host2 , port2):
            global CliEnts       
            self.AutH_ToKen_0115 = tok    
            self.CliEnts = socket.create_connection((host , int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))  
            self.DaTa = self.CliEnts.recv(1024)          	        
            threading.Thread(target=self.Connect_SerVer_OnLine, args=(Token , tok , host , port , key , iv , host2 , port2)).start()
            self.Exemple = xMsGFixinG('12345678')
            
            # تخزين المفتاح و IV للاستخدام لاحقاً
            self.key = key
            self.iv = iv
            
            # تسجيل العميل في القائمة العالمية
            with connected_clients_lock:
                connected_clients[self.id] = self
                print(f"✅ تم تسجيل الحساب {self.id} في القائمة العالمية، عدد الحسابات الآن: {len(connected_clients)}")
            
            while True:      
                try:
                    self.DaTa = self.CliEnts.recv(1024)   
                    if len(self.DaTa) == 0 or (hasattr(self, 'DaTa2') and len(self.DaTa2) == 0):	            		
                        try:            		    
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'):
                                self.CliEnts2.close()
                            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)                    		                    
                        except:
                            try:
                                self.CliEnts.close()
                                if hasattr(self, 'CliEnts2'):
                                    self.CliEnts2.close()
                                self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                            except:
                                self.CliEnts.close()
                                if hasattr(self, 'CliEnts2'):
                                    self.CliEnts2.close()
                                ResTarT_BoT()	            
                                      
                    if '1200' in self.DaTa.hex()[0:4] and 900 > len(self.DaTa.hex()) > 100:
                        if b"***" in self.DaTa:self.DaTa = self.DaTa.replace(b"***",b"106")         
                        try:
                           self.BesTo_data = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))	       
                           self.input_msg = 'besto_love' if '8' in self.BesTo_data["5"]["data"] else self.BesTo_data["5"]["data"]["4"]["data"]
                        except: self.input_msg = None	   	 
                        self.DeCode_CliEnt_Uid = self.BesTo_data["5"]["data"]["1"]["data"]
                        self.CliEnt_Uid = EnC_Uid(self.DeCode_CliEnt_Uid , Tp = 'Uid')
                               
                    if 'besto_love' in self.input_msg[:10]:
                        self.CliEnts.send(xSEndMsg(f'''[C][B][FF0000]مرحبٱ بك في بوت [C][B][FF0089]╔══════════════════════════╗
[EF9AFF] مرحباً بك في بوت متطور جداً البوت من صنع و تطوير [FF00A9]ZIX OFFICIAL
[00ff00]لمعرفة الأوامر الموجودة ابعث امر /َhelp و سيتم إضافة ميزات اخرى قريباً إن شاء الّله
[FF0089]╠══════════════════════ ═══╣
[FFFF9F]هل أنت مهتم بشراء البوت
[FF00FF]تواصل مع المطور:
[FFD700]تيليجرام : [FF0007]@XiZYELFI
[FFF000] انستغرام : [FF0007]@t_q_i_h
[FF0089]╚══════════════════════════╝''', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))
                        time.sleep(0.3)
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'):
                            self.CliEnts2.close()
                        self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)	                    	 	 
                                                               
  		             

                    if '/pp/' in self.input_msg[:4]:
                        self.target_id = self.input_msg[4:]	 
                        self.Zx = ChEck_Commande(self.target_id)
                        if True == self.Zx:	            		     
                            # إرسال السبام من جميع الحسابات
                            threading.Thread(target=send_spam_from_all_accounts, args=(self.target_id,)).start()
                            time.sleep(2.5)    			         
                            self.CliEnts.send(xSEndMsg(f'\n[b][c][{ArA_CoLor()}] SuccEss Spam To {xMsGFixinG(self.target_id)} From All Accounts\n', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))
                            time.sleep(1.3)
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'):
                                self.CliEnts2.close()
                            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)	            		      	
                        elif False == self.Zx: 
                            self.CliEnts.send(xSEndMsg(f'\n[b][c][{ArA_CoLor()}] - PLease Use /pp/<id>\n - Ex : /pp/{self.Exemple}\n', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))	
                            time.sleep(1.1)
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'):
                                self.CliEnts2.close()
                            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)	            		

   		      	            			      	
                except Exception as e:
                    print(f"Error in Connect_SerVer: {e}")
                    try:
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'):
                            self.CliEnts2.close()
                    except:
                        pass
                    self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                                    
    def GeT_Key_Iv(self , serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp , key , iv = my_message.field21 , my_message.field22 , my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp , key , iv    

    def Guest_GeneRaTe(self , uid , password):
        self.url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        self.headers = {"Host": "100067.connect.garena.com","User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)","Content-Type": "application/x-www-form-urlencoded","Accept-Encoding": "gzip, deflate, br","Connection": "close",}
        self.dataa = {"uid": f"{uid}","password": f"{password}","response_type": "token","client_type": "2","client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_id": "100067",}
        try:
            self.response = requests.post(self.url, headers=self.headers, data=self.dataa).json()
            self.Access_ToKen , self.Access_Uid = self.response['access_token'] , self.response['open_id']
            time.sleep(0.2)
            print(' - Starting ZIX OFFICIAL Freind BoT !')
            print(f' - Uid : {uid}\n - Password : {password}')
            print(f' - Access Token : {self.Access_ToKen}\n - Access Id : {self.Access_Uid}')
            return self.ToKen_GeneRaTe(self.Access_ToKen , self.Access_Uid)
        except Exception: 
            print("Error in Guest_GeneRaTe, restarting...")
            ResTarT_BoT()    
                                        
    def GeT_LoGin_PorTs(self , JwT_ToKen , PayLoad):
        self.UrL = 'https://clientbp.common.ggbluefox.com/GetLoginData'
        self.HeadErs = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB50',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': 'clientbp.common.ggbluefox.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',}       
        try:
                self.Res = requests.post(self.UrL , headers=self.HeadErs , data=PayLoad , verify=False)
                self.BesTo_data = json.loads(DeCode_PackEt(self.Res.content.hex()))  
                address , address2 = self.BesTo_data['32']['data'] , self.BesTo_data['14']['data'] 
                ip , ip2 = address[:len(address) - 6] , address2[:len(address) - 6]
                port , port2 = address[len(address) - 5:] , address2[len(address2) - 5:]             
                return ip , port , ip2 , port2          
        except requests.RequestException as e:
                print(f" - Bad Requests !")
        print(" - Failed To GeT PorTs !")
        return None, None   
        
    def ToKen_GeneRaTe(self , Access_ToKen , Access_Uid):
        self.UrL = "https://loginbp.common.ggbluefox.com/MajorLogin"
        self.HeadErs = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB50',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Content-Length': '928',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.common.ggbluefox.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'}   
        self.dT = bytes.fromhex('1a13323032352d30372d33302031343a31313a3230220966726565206669726528013a07322e3131342e324234416e64726f6964204f53203133202f204150492d33332028545031412e3232303632342e3031342f3235303531355631393737294a0848616e6468656c6452094f72616e676520544e5a0457494649609c1368b80872033438307a1d41524d3634204650204153494d4420414553207c2032300030207c20388001973c8a010c4d616c692d473532204d433292013e4f70656e474c20455320332e322076312e72333270312d3031656163302e32613839336330346361303032366332653638303264626537643761663563359a012b476f6f676c657c61326365613833342d353732362d346235622d383666322d373130356364386666353530a2010e3139362e3138372e3132382e3334aa0102656eb201203965373166616266343364383863303662373966353438313034633766636237ba010134c2010848616e6468656c64ca0115494e46494e495820496e66696e6978205836383336ea014063363231663264363231343330646163316137383261306461623634653663383061393734613662633732386366326536623132323464313836633962376166f00101ca02094f72616e676520544ed2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003dc810ee803daa106f003ef068004e7a5068804dc810e9004e7a5069804dc810ec80403d2045b2f646174612f6170702f7e7e73444e524632526357313830465a4d66624d5a636b773d3d2f636f6d2e6474732e66726565666972656d61782d4a534d4f476d33464e59454271535376587767495a413d3d2f6c69622f61726d3634e00402ea047b61393862306265333734326162303061313966393737633637633031633266617c2f646174612f6170702f7e7e73444e524632526357313830465a4d66624d5a636b773d3d2f636f6د2e6474732e66726565666972656d61782d4a534d4f476m33464e59454271535376587767495a413d3d2f626173652e61706bf00402f804028a050236349a050a32303139313135363537a80503b205094f70656e474c455333b805ff7fc00504d20506526164c3a873da05023133e005b9f601ea050b616e64726f69645d6d6178f2055c4b71734854346230414a3777466c617231594d4b693653517a6732726b3665764f38334f306f59306763635a626457467a785633483564454f586a47704e3967476956774b7533547a312b716a36326546673074627537664350553d8206147b226375755f72617465223a5b36302c39305d7d8806019006019a060134a2060134b20600')
        self.dT = self.dT.replace(b'2025-07-30 14:11:20' , str(datetime.now())[:-7].encode())        
        self.dT = self.dT.replace(b'c621f2d621430dac1a782a0dab64e6c80a974a6bc728cf2e6b1224d186c9b7af' , Access_ToKen.encode())
        self.dT = self.dT.replace(b'9e71fabf43d88c06b79f548104c7fcb7' , Access_Uid.encode())
        self.PaYload = bytes.fromhex(EnC_AEs(self.dT.hex()))  
        self.ResPonse = requests.post(self.UrL, headers = self.HeadErs ,  data = self.PaYload , verify=False)        
        if self.ResPonse.status_code == 200 and len(self.ResPonse.text) > 10:
            self.BesTo_data = json.loads(DeCode_PackEt(self.ResPonse.content.hex()))
            self.JwT_ToKen = self.BesTo_data['8']['data']           
            self.combined_timestamp , self.key , self.iv = self.GeT_Key_Iv(self.ResPonse.content)
            ip , port , ip2 , port2 = self.GeT_LoGin_PorTs(self.JwT_ToKen , self.PaYload)            
            return self.JwT_ToKen , self.key , self.iv, self.combined_timestamp , ip , port , ip2 , port2
        else:
            print("Error in ToKen_GeneRaTe, restarting...")
            sys.exit()
      
    def Get_FiNal_ToKen_0115(self):
        try:
            token , key , iv , Timestamp , ip , port , ip2 , port2 = self.Guest_GeneRaTe(self.id , self.password)
            self.JwT_ToKen = token        
            try:
                self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
                self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
                self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
                self.HeX_VaLue = DecodE_HeX(Timestamp)
                self.TimE_HEx = self.HeX_VaLue
                self.JwT_ToKen_ = token.encode().hex()
                print(f' - ProxCed Uid : {self.AccounT_Uid}')
            except Exception as e:
                print(f" - Error In ToKen : {e}")
                return
            try:
                self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
                length = len(self.EncoDed_AccounT)
                self.__ = '00000000'
                if length == 9: self.__ = '0000000'
                elif length == 8: self.__ = '00000000  '
                elif length == 10: self.__ = '000000'
                elif length == 7: self.__ = '000000000'
                else:
                    print('Unexpected length encountered')                
                self.Header = f'0115{self.__}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
                self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_ , key , iv)
            except Exception as e:
                print(f" - Erorr In Final Token : {e}")
            self.AutH_ToKen = self.FiNal_ToKen_0115
            self.Connect_SerVer(self.JwT_ToKen , self.AutH_ToKen , ip , port , key , iv , ip2 , port2)        
            return self.AutH_ToKen , key , iv
        except Exception as e:
            print(f"Error in Get_FiNal_ToKen_0115: {e}")
            ResTarT_BoT()

def start_account(account):
    """دالة لبدء تشغيل حساب واحد"""
    try:
        print(f"Starting account: {account['id']}")
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        print(f"Error starting account {account['id']}: {e}")

# تعريف واجهات API
@app.route('/spam', methods=['POST'])
def spam_api():
    """واجهة API لإرسال سبام إلى حساب معين"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'يجب إدخال user_id في الجسم'}), 400
        
        target_id = data['user_id']
        
        # التحقق من صحة user_id
        if not ChEck_Commande(target_id):
            return jsonify({'error': 'user_id غير صالح'}), 400
        
        # بدء السبام اللانهائي في ثريد منفصل
        with active_spam_lock:
            if target_id not in active_spam_targets:
                active_spam_targets[target_id] = True
                threading.Thread(target=infinite_spam_worker, args=(target_id,), daemon=True).start()
                message = f'تم بدء السبام اللانهائي على {target_id}'
            else:
                message = f'السبام اللانهائي على {target_id} يعمل بالفعل'
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@app.route('/spam/stop', methods=['POST'])
def stop_spam_api():
    """واجهة API لإيقاف السبام اللانهائي"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'يجب إدخال user_id في الجسم'}), 400
        
        target_id = data['user_id']
        
        # إيقاف السبام
        with active_spam_lock:
            if target_id in active_spam_targets:
                del active_spam_targets[target_id]
                message = f'تم إيقاف السبام اللانهائي على {target_id}'
            else:
                message = f'لا يوجد سبام نشط على {target_id}'
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@app.route('/spam/status', methods=['GET'])
def spam_status_api():
    """واجهة API للتحقق من حالة السبام النشط"""
    try:
        with active_spam_lock:
            active_targets = list(active_spam_targets.keys())
        
        return jsonify({
            'active_spam_targets': active_targets,
            'count': len(active_targets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@app.route('/status', methods=['GET'])
def status_api():
    """واجهة API للتحقق من حالة البوت والحسابات المتصلة"""
    try:
        with connected_clients_lock:
            accounts_count = len(connected_clients)
            accounts_list = list(connected_clients.keys())
        
        return jsonify({
            'status': 'running',
            'connected_accounts': accounts_count,
            'accounts': accounts_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_api():
    """واجهة API للتحقق من صحة البوت"""
    return jsonify({'status': 'healthy'}), 200

def run_flask_app():
    """تشغيل تطبيق Flask"""
    app.run(host='0.0.0.0', port=port, debug=False)

def StarT_SerVer():
    """الدالة الرئيسية لبدء تشغيل جميع الحسابات وخادم API"""
    # بدء تشغيل خادم Flask في خيط منفصل
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    threads = []
    
    for account in ACCOUNTS:
        thread = threading.Thread(target=start_account, args=(account,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(2)  # تأخير بسيط بين بدء كل حساب
    
    # انتظار انتهاء جميع الثreads (لن يحدث ذلك لأنها تعمل بشكل مستمر)
    for thread in threads:
        thread.join()
  
StarT_SerVer()
