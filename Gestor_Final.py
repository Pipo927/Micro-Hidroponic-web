#===================================================== LIBS ================================
import json
import serial
import sys
import time
import io
import os
import re
import RPi.GPIO as GPIO
import datetime
import statistics
import pymysql
#=================================================== VARIAVEIS GLOBAIS ====================================
EC = 0
AUTOMATIC = 0
PH = 0
LIGHT = 0
ard_con = 2
STATE = 1
Read_LDR = 0
Read_EC = 0
Read_PH = 0
Read_Temp= 0
EC_Confirm = 0



#=============================================RESET VIA SERIAL AO ARDUINO=======================================
if os.path.exists('/dev/ttyACM0') == True:
    arduino = serial.Serial('/dev/ttyACM0',1200,timeout = 0.1)
    time.sleep(0.5)
    arduino.close()
    time.sleep(2)
if os.path.exists('/dev/ttyACM1') == True:
    arduino = serial.Serial('/dev/ttyACM1',1200,timeout = 0.1)
    time.sleep(0.5)
    arduino.close()
    time.sleep(2)
if os.path.exists('/dev/ttyACM2') == True:
    arduino = serial.Serial('/dev/ttyACM2',1200,timeout = 0.1)
    time.sleep(0.5)
    arduino.close()
    time.sleep(2)
time.sleep(8)
#FIM DO RESET

#=================================CONFIG PORTA SERIE====================================================
if os.path.exists('/dev/ttyACM0') == True:
        ard_con = 'ACM0'
        arduino = serial.Serial('/dev/ttyACM0',115200,timeout = 20)

if os.path.exists('/dev/ttyACM1') == True:
        ard_con = 'ACM1'
        arduino = serial.Serial('/dev/ttyACM1',115200,timeout = 20)

if os.path.exists('/dev/ttyACM2') == True:
        ard_con = 'ACM2'
        arduino = serial.Serial('/dev/ttyACM2',115200,timeout = 20)

time.sleep(0.5)
print ('Porta Usada:',ard_con)



#============================================FUNÇOES ========================================

def WaitSeed():
    global EC
    global PH
    global AUTOMATIC
    global LIGHT
    dbConn = pymysql.connect(host="localhost",user="root",passwd="*******",db="wordpress")
    cursor = dbConn.cursor()
    cursor.execute("SELECT * FROM OUTPUT ORDER BY id DESC LIMIT 1 ")
    row=cursor.fetchone()
    if row is not None:
        row_str = str(row)
        row_str_aux = row_str.replace("'","")
        row_str_final = row_str_aux.replace(")","")
        data_splited = row_str_final.split(",")
        data_aux = (data_splited[1] + data_splited[9] + data_splited[11] + data_splited [12] + data_splited [2])
        data_final =data_aux.ljust(30, ' ')
        EC = data_splited [9]
        AUTOMATIC = data_splited [12]
        PH = data_splited [10]
        LIGHT = data_splited [2]
        print("-------------DADOS DO UTILIZADOR-------------")
        print("Planta:",data_splited [1])
        print("EC:",EC)
        print("Dias de Crescimento:",data_splited [11])
        print("-------------DADOS MEDIDOS-------------------")
        return 2
    else:
        return 1

def ProgressBar (num, total, nextPercent, nextPoint):
    num = float (num)
    total = float (total) - 1
    if STATE == 5:
        time.sleep(0.08)
    if STATE == 7:
        time.sleep(0.04)
    if STATE == 8:
        time.sleep(1)
    if STATE == 4:
        time.sleep(1)
    if not nextPoint:
        nextPoint = 0.0
    if not nextPercent:
        nextPoint += 2.0
        sys.stdout.write ("[0%")
        nextPercent = 10
    elif num == total:
        sys.stdout.write ("100%]\n")
        nextPercent += 10
    elif not nextPoint:
        nextPoint = 0.0
    elif num / total * 100 >= nextPercent:
        sys.stdout.write (str(int (nextPercent)) + "%")
        nextPercent += 10
    elif num / total * 100 >= nextPoint:
        sys.stdout.write (":")
        nextPoint += 2
    return (nextPercent, nextPoint)



def FillRes():
    Rsize = 1
    FillResComplete = 1
    data = {"CMD": 1}
    data=json.dumps(data)
    size = len(data)
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print ("erro 1")
            print (e)
            pass
        time.sleep(1)
    while FillResComplete:
        try:
            incoming = arduino.readline()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                print ("ENCHER RESERVATORIO: OK")
                time.sleep(1)
                FillResComplete = 0
                return 3
            else:
                FillResComplete = 1
                print ("ENCHER RESERVATORIO: ...")
                time.sleep(1)
                return 2

        except Exception as e:
            print ("erro aqui")
            print (e)
            pass
            return 2


def CheckLDR():
    global Read_LDR
    Rsize = 1
    LDRComplete = 1
    Aut = int(AUTOMATIC)
    lig = int(LIGHT)
    now = datetime.datetime.now()
    if Aut:
        if now.hour >= 7 and now.hour <= 20:
            data = { "CMD": 2, "day": 1}
            print("Luminosidade em Modo Automatico e dentro de horas")
        else:
            data = { "CMD": 2, "day": 0}
            print("Luminosidade em Modo Automatico e fora de horas")
    else:
        if lig:
            data = { "CMD": 2, "light": 1}
            print("Luminosidade em Modo Manual: Liga Lampada")
        else:
            data = { "CMD": 2, "light": 0}
            print("Luminosidade em Modo Manual: Desliga Lampada")
    data=json.dumps(data)
    size = len(data)
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
        time.sleep(1)
    while LDRComplete:
        try:
            incoming = arduino.readline().decode()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                time.sleep(1)
                LDRComplete = 0
                if incoming_dict["light"] == 1:
                    print ("lampada ligada")
                else:
                    print ("lampada Desligada")
                temp = statistics.median(incoming_dict["LDR"])
                #temp = 1023 - temp
                Read_LDR = round((250/((temp)*0.0048828125))-50,2)
                #Read_LDR = int((1.25 * pow (10,7))*pow(temp,(-1.4059)))
                print ("LDR", Read_LDR)
                print ("Control Luminosidade: OK")
                return 4
            else:
                LDRComplete = 1
                print ("Control Luminosidade: ...")
                time.sleep(1)
                return 3

        except Exception as e:
            print (e)
            pass
            return 2

def ControlEC():
    global EC
    global Read_EC
    global Read_Temp
    global EC_Confirm
    Rsize = 1
    ECComplete = 1
    MultiEC = float(EC)*100
    MultiEC = int(MultiEC)
    tryy = int(EC_Confirm)
    data = { "CMD": 3, "EC": MultiEC, "TRY": tryy}
    data=json.dumps(data)
    size = len(data)
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
        time.sleep(1)
    while ECComplete:
        try:
            if EC_Confirm == 0:
                print ("A estabilizar agua para leitura")
                nextPercent, nextPoint = 0, 0
                total = 180
                for num in range (total):
                    nextPercent, nextPoint = ProgressBar (num, total, nextPercent, nextPoint)
            else:
                pass
            incoming = arduino.readline()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                time.sleep(1)
                ECComplete = 0
                REC = (statistics.median(incoming_dict["ReadEC"]))
                temp = statistics.median(incoming_dict["Water"])
                #Read_Temp = round((10 * temp * 2.8 / 1024),2)
                Read_Temp = temp
                Read_EC = round((REC / 500),2)
                #Read_EC = REC
                if Read_EC < float(EC):
                    print ("Control EC: Falta EC")
                    print ("Valor EC:", Read_EC)
                    EC_Confirm = 0
                    return 5
                else:
                    print ("Valor EC:", Read_EC)
                    if EC_Confirm < 5:
                        EC_Confirm += 1
                        print ("Confirmar Valor de EC: ", EC_Confirm, "/ 5")
                        time.sleep (5)
                        return 4
                    else:
                        EC_Confirm = 0
                        print ("Confirmar Valor de EC: OK")
                        return 6
            else:
                ECComplete = 1
                print ("READY 0")
                time.sleep(1)
                return 3
        except Exception as e:
            print ("erro 2 ")
            print (e)
            pass
            return 2

def AddEC():
    AddECComplete = 1
    Rsize = 1
    data = { "CMD": 4}
    data=json.dumps(data)
    size = len(data)
    dbConn = pymysql.connect(host="localhost",user="root",passwd="girafa",db="wordpress")
    cursor = dbConn.cursor()
    cursor.execute("SELECT * FROM LEVEL ORDER BY id DESC LIMIT 1 ")
    row=cursor.fetchone()
    row_str = str(row)
    row_str_aux = row_str.replace("'","")
    row_str_final = row_str_aux.replace(")","")
    data_splited = row_str_final.split(",")
    cursor.execute("SELECT * FROM LEVEL")
    cursor.execute("""INSERT INTO LEVEL (EC1,EC2,pH) VALUES (%s,%s,%s)""",((float(data_splited[1])-0.2),(float(data_splited[2])-0.2),float(data_splited[3])))
    dbConn.commit() #commit the insert
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
        time.sleep(1)
    while AddECComplete:
        try:
            nextPercent, nextPoint = 0, 0
            total = 150
            for num in range (total):
                nextPercent, nextPoint = ProgressBar (num, total, nextPercent, nextPoint)
            incoming = arduino.readline()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                AddECComplete = 0
                print ("Adiciona EC: Adicionado 4mL")
                print ("Check EC: ...")
                return 4
            else:
                AddECComplete = 1
                print ("Adiciona EC: ...")
                time.sleep(1)
                return 5
        except Exception as e:
            print (e)
            pass
            return 2

def ControlpH():
    global PH
    global Read_PH
    Rsize = 1
    pHComplete = 1
    MultipH = float(PH)*100
    MultipH = int(MultipH)
    data = { "CMD": 5, "pH": MultipH}
    try:
        data=json.dumps(data)
        size = len(data)
    except Exception as e:
            print (e)
            pass
            return 6
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
        time.sleep(1)
    while pHComplete:
        try:
            time.sleep(1)
            incoming = arduino.readline()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                time.sleep(1)
                pHComplete = 0
                Read_PH = (statistics.median(incoming_dict["ReadpH"])/1000)
                Read_PH = round(Read_PH,2)
                print("pH:",Read_PH)
                if Read_PH > float(PH):
                    print ("Control pH: pH > ", pH)
                    return 7
                else:
                    print ("Control pH: OK")
                    return 8
            else:
                ECComplete = 1
                print ("READY 0")
                time.sleep(1)
                return 3
        except Exception as e:
            print (e)
            pass
            return 2

def AddpH():
    AddpHComplete = 1
    Rsize = 1
    data = { "CMD": 6}
    data=json.dumps(data)
    size = len(data)
    dbConn = pymysql.connect(host="localhost",user="root",passwd="girafa",db="wordpress")
    cursor = dbConn.cursor()
    cursor.execute("SELECT * FROM LEVEL ORDER BY id DESC LIMIT 1 ")
    row=cursor.fetchone()
    row_str = str(row)
    row_str_aux = row_str.replace("'","")
    row_str_final = row_str_aux.replace(")","")
    data_splited = row_str_final.split(",")
    cursor.execute("SELECT * FROM LEVEL")
    cursor.execute("""INSERT INTO LEVEL (EC1,EC2,pH) VALUES (%s,%s,%s)""",(float(data_splited[1]),float(data_splited[2]),(float(data_splited[3])-0.2)))
    dbConn.commit() #commit the insert
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
    while AddpHComplete:
        try:
            nextPercent, nextPoint = 0, 0
            total = 100
            for num in range (total):
                nextPercent, nextPoint = ProgressBar (num, total, nextPercent, nextPoint)
            incoming = arduino.readline()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                AddpHComplete = 0
                print ("Adiciona pH: Adicionado 2mL")
                print ("Check pH: ...")
                return 6
            else:
                AddECComplete = 1
                print ("Adiciona pH: ...")
                time.sleep(1)
                return 7
        except Exception as e:
            print (e)
            pass
            return 2

def BombSolution():
    BSComplete = 1
    Rsize = 1
    data = { "CMD": 7}
    data=json.dumps(data)
    size = len(data)
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
        time.sleep(1)
    while BSComplete:
        try:
            print ("A Repor Solucao nas plantas ...")
            nextPercent, nextPoint = 0, 0
            total = 150
            for num in range (total):
                nextPercent, nextPoint = ProgressBar (num, total, nextPercent, nextPoint)
            incoming = arduino.readline()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                BSComplete = 0
                print ("Repor Solucao nas plantas: OK")
                return 9
            else:
                BSComplete = 1
                print ("Repor Solucao nas plantas: ...")
                time.sleep(1)
                return 8
        except Exception as e:
            print (e)
            pass
            return 2

def InsertBD():
    try:
        dbConn = pymysql.connect(host="localhost",user="root",passwd="girafa",db="wordpress")
        cursor = dbConn.cursor()
        cursor.execute("SELECT * FROM INPUT")
        cursor.execute("""INSERT INTO INPUT (EC,PH,LUMINOSIDADE,TEMPERATURA) VALUES (%s,%s,%s,%s)""",(Read_EC,Read_PH,Read_LDR,Read_Temp))
        dbConn.commit() #commit the insert
        print("Dados inseridos na BD: OK")
        return 10
    except Exception as e:
        print (e)
        print("Dados inseridos na BD: ERRO")
        print("Standby  até nova alteração (BD, Luminosidade, Tempo)")
        pass
        return 9

def WaitChange():

    #======================================CHECK LDR==================================
    Rsize = 1
    LDRComplete = 1
    data = { "CMD": 8}
    data=json.dumps(data)
    size = len(data)
    while Rsize != size:
        arduino.write(data.encode('ascii'))
        arduino.flush()
        try:
            incoming = arduino.readline().decode("utf-8").strip("\r").strip("\n").strip("'")
            Rsize = int(incoming)
        except Exception as e:
            print (e)
            pass
        time.sleep(1)
    while LDRComplete:
        try:
            incoming = arduino.readline().decode()
            incoming_dict = json.loads(incoming)
            if incoming_dict["Ready"] == 1:
                time.sleep(1)
                LDRComplete = 0
#                 temp = statistics.median(incoming_dict["LDR"])
#                 temp = 1023 - temp
#                 NowLDR = int((1.25 * pow (10,7))*pow(temp,(-1.4059)))
                temp = statistics.median(incoming_dict["LDR"])
                #temp = 1023 - temp
                NowLDR = round((250/((temp)*0.0048828125))-50,2)
                #Read_LDR = int((1.25 * pow (10,7))*pow(temp,(-1.4059)))
                dbConn = pymysql.connect(host="localhost",user="root",passwd="girafa",db="wordpress")
                cursor = dbConn.cursor()
                cursor.execute("SELECT * FROM INPUT ORDER BY id DESC LIMIT 1 ")
                row=cursor.fetchone()
                row_str = str(row)
                row_str_aux = row_str.replace("'","")
                row_str_final = row_str_aux.replace(")","")
                data_splited = row_str_final.split(",")
                LastLDR = float(data_splited [3])
                if LastLDR > 200 and NowLDR > 200:
                    pass
                elif LastLDR < 200 and NowLDR < 200:
                    pass
                elif LastLDR > 200 and NowLDR < 200:
                    print("----------------------LDR COM ALTERAÇAO-------------------------------")
                    print("BD LDR",LastLDR)
                    print("NOW LDR",NowLDR)
                    return 1
                elif LastLDR < 200 and NowLDR > 200:
                    print("----------------------LDR COM ALTERAÇAO-------------------------------")
                    print("BD LDR",LastLDR)
                    print("NOW LDR",NowLDR)
                    return 1
            else:
                LDRComplete = 1
                time.sleep(1)
                return 10

        except Exception as e:
            print (e)
            pass
            return 10
        #======================================CHECK BD==================================
    dbConn = pymysql.connect(host="localhost",user="root",passwd="girafa",db="wordpress")
    cursor = dbConn.cursor()
    cursor.execute("SELECT * FROM OUTPUT ORDER BY id DESC LIMIT 1 ")
    row=cursor.fetchone()
    if row is not None:
        row_str = str(row)
        row_str_aux = row_str.replace("'","")
        row_str_final = row_str_aux.replace(")","")
        data_splited = row_str_final.split(",")
        data_aux = (data_splited[1] + data_splited[9] + data_splited[11] + data_splited [12] + data_splited [2])
        data_final =data_aux.ljust(30, ' ')
        if data_splited[9] != EC or data_splited[12] != AUTOMATIC or data_splited[10] != PH or data_splited[2] != LIGHT:
            if data_splited[9] == ' R':
                dbConn = pymysql.connect(host="localhost",user="root",passwd="girafa",db="wordpress")
                cursor = dbConn.cursor()
                cursor.execute("set FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("TRUNCATE TABLE INPUT;")
                dbConn.commit()
                time.sleep(0.1)
                cursor.execute("set FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("TRUNCATE TABLE LEVEL;")
                dbConn.commit()
                time.sleep(0.1)
                cursor.execute('TRUNCATE TABLE OUTPUT ')
                time.sleep(0.1)
                dbConn.commit()
                cursor.close()
                print("RESET FEITO")
                a = 0
                return 1
            else:
                print("---------------------- BD COM ALTERAÇAO-------------------------------")
                return 1
        else:
                pass
    else:
        return 1
    #======================================TIME==================================
    now = datetime.datetime.now()
    if now.minute is 15 or now.minute is 45:
        print("Rotina recomeça", now.minute)
        return 1
    else:
        return 10

def StateMachine():
    global STATE
    if STATE is 1:
        STATE = WaitSeed()

    if STATE is 2:
        STATE = FillRes()

    if STATE is 3:
        STATE = CheckLDR()

    if STATE is 4:
        STATE = ControlEC()

    if STATE is 5:
        STATE = AddEC()

    if STATE is 6:
        STATE = ControlpH()

    if STATE is 7:
        STATE = AddpH()

    if STATE is 8:
        STATE = BombSolution()

    if STATE is 9:
        STATE = InsertBD()

    if STATE is 10:
        STATE = WaitChange()



while 1:

    StateMachine()
