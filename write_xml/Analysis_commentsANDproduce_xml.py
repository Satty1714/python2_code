#coding:utf-8
#python 2.7

import os,sys
from bs4 import BeautifulSoup
import re
import time
from time import sleep
#comments数据位置，从html提取的位置
comments_path = r'C:\workspace\write_excel\CaseComment.xls'
#筛选符合条件的comments保存的位置；只还有cpp和c的comments的全部内容
screen_comments_path=r"C:\workspace\write_excel\screen_comments.txt"
#xmlpath
xml_path= r"C:\workspace\write_excel\xml"

#如果cpp或者c的开始字符包含在一下字符串则不写入xml
eliminate_char_list=["-","+","*"]


def GetComments(comments_path):
    with open(comments_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        # print soup
        #print len(soup.find_all("tr"))
        comments_dict = {}
        for tr in soup.find_all("tr"):
            try:
                relus = '<td style="vnd.ms-excel.numberformat:@">(.*)</td>'
                relus_1 = '<td style="vnd.ms-excel.numberformat:@">([\s\S]*)</td>'
                #relus,str(tr.find_all("td")[0]))[0]
                #relus 规则
                #tr.find_all("td")[0]新的匹配节点的第一个数据
                #str() type是一个类所以需要字符串化
                #re.findall(...)[0]获得的结果第一个就是需要的数据
                case_number = re.findall(relus,str(tr.find_all("td")[0]))[0]
                comments_dict[case_number]=re.findall(relus_1,str(tr.find_all("td")[2]))[0]
            except:pass
    return comments_dict

#
def ReadxmlComments(path_):
    comments_list=[]
    with open(path_, 'r') as f:
        lines=f.readlines();
        index_begin=0;
        temp_list=[]
        for index in range(len(lines)):
            if index==0: index_begin=index;
            else:
                if "Case Number:".lower() in lines[index].lower():
                    temp_list=lines[index_begin:index]
                    comments_list.append(temp_list[:])#从第三行开始取到最后
                    temp_list=[]
                    index_begin=index
                if index==len(lines)-1:
                    comments_list.append(lines[index_begin:])
    # print(comments_list)
    return comments_list

#获得comments含有cpp或者c case
def GetNeedComments(comments_dict):
    need_comments_dict={}
    for key,values in comments_dict.items():
        # print key,values
        if (".cpp " in values) or (".c " in values):
            need_comments_dict[key]=values
    print("all_case_number:{}".format(len(comments_dict)))
    print("all message numbers:{}".format(len(need_comments_dict)))
    return need_comments_dict
    
def WriteInfo(need_comments_dict):
    with open(screen_comments_path,"w") as f:
        for key,values in need_comments_dict.items():
            f.write("Case Number:{}\nComment:\n{}\n".format(key,values))
            f.write("{}\n".format("#"*60))

#生成xml
def ProduceXML(name,output_list,comments_list,mode="and"):
    produce_info_list=[
        '<State name="{}" mode="{}" output="{}">',
        '\n\t</Message>\n{}',
        '\n\t</Message>\n</State>'
    ]
    output_str="";
    comments_str="";
    for index in range(len(output_list)):
        output_list[index]=output_list[index].replace("\n","")
    for out in output_list:
        
        #output 不输出条件
        #1 字符串前两个为//不存储
        if "//"==out[0:2]:continue
        #2 hi(不分大小写),转换小写比较
        if "hi"==out[0:2].lower():continue
        #3 使用dear Dear Customer
        if ("dear"==out[0:5].lower() and (customer not in out.lower)):continue
        #4 只是空格的跳过
        # print("out:({})".format(len(out)))
        if not len(out):
            print("out:({})".format(out))
            continue
        output_str+=out
    for index in range(len(comments_list)):
        
        if (index+1)==len(comments_list):
            comments_str+="\t\t"+comments_list[index]
        else:
            comments_str+="\t\t"+comments_list[index]+"\n"
    produce_info_list[0]=produce_info_list[0].format(name,mode,output_str)
    produce_info_list[1]=produce_info_list[1].format(comments_str)
    # for pro in produce_info_list:
        # print(pro);
    return produce_info_list
    
#写xml文件
def WriteXML(xml_list,file_):
    # path_= r"C:\SUNYAN\20180821_xml\xml_test"
    if not os.path.isdir(xml_path):os.makedirs(xml_path) 
    file_="{}/{}.xml".format(xml_path,file_)
    with open(file_,"w") as f:
        for xml in xml_list:
            f.write(xml)

#获得当前系统时间到毫秒级
def GetTime():
    # 格式化成2016-03-20 11:45:39形式
    time_=str(time.time())
    temp_list=time_.split(".")
    #:.2表示输出字符串的宽度为：2
    return "{}_{:.2}".format(time.strftime("%Y%m%d_%H%M%S", time.localtime()),temp_list[1])

#从所有给定的comments中提取含有cpp或者c的行
def GetCppC_list(comments_list):
    index_begin=0
    cpp_c_list=[]
    for index in range(len(comments_list)):
        if (".cpp " in comments_list[index]) or (".c " in comments_list[index]):
            #开始字符含有标记的剔除字符的跳过
            if comments_list[index][0] in eliminate_char_list: continue
            #记录第一次
            if not index_begin: index_begin=index
            cpp_c_list.append(comments_list[index])
    return cpp_c_list
    
#生成xml文件
def CreateXML(comments_list,case_id):
    # 获得caseNumber，暂时也是xml中output的输出
    output_list=[]
    output_list.append(case_id)
    #获得xml中message内容
    cpp_c_list=GetCppC_list(comments_list);
    #xml相关标签
    xml_name="MSG_{}_{}".format(output_list[0],GetTime())#xml名称，唯一标识
    mode="and"#xml模式
    #如果message信息超过10条将不执行
    if ((len(cpp_c_list)<=10) and (len(cpp_c_list)>0)):
        produce_info_list=ProduceXML(xml_name,output_list,cpp_c_list,mode)
        WriteXML(produce_info_list,xml_name);
        sleep(0.1)
#
def Main():
    # print sys.argv;
    #命令行传递需要解析的生成xml的文件，必须满足固定的格式
    if len(sys.argv)>1:
        comments_list=ReadxmlComments(sys.argv[1]);
        for comm in comments_list:
            CreateXML(comm[2:],str(re.findall("Case Number:(.+?)\n",comm[0])[0]))
        exit()
    #从html获得数据提取comments
    comments_dict = GetComments(comments_path)
    #筛选comments
    need_comments_dict = GetNeedComments(comments_dict)
    for key,values in need_comments_dict.items():
        #获得所有cpp和c
        CreateXML(values.split("\n"),key)
    #将筛选结果存入文件
    WriteInfo(need_comments_dict)
#
if __name__=="__main__":
    Main()

