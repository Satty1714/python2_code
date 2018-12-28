# -*- coding:utf-8 -*-
# python 2.7

import os, sys
import re
import time
import codecs
import platform
from bs4 import BeautifulSoup
from time import sleep

# comments数据位置，从html提取的位置
comments_path = ""
if os.path.isfile(sys.argv[1]):
    comments_path = "{}/{}".format(os.path.split(os.path.realpath(__file__))[0], sys.argv[1])
if os.path.isabs(sys.argv[1]):
    comments_path = sys.argv[1]
# txt文件存放路径
data_file_path = ""
# xmlpath
xml_path = ""
new_xml_path = ""

line_sign= "\n"
if platform.system() == "Linux":line_sign="\r\n"
#最后message行数
line_num = 10

#切分和拼接路径
def split_path(comments_path):
    global data_file_path
    global xml_path
    path_,file_ = os.path.split(comments_path)
    filename = os.path.splitext(file_)[0]
    txt_name = filename + ".txt"
    xml_name = filename + "_xml"
    data_file_path = "{}/{}".format(path_,txt_name)
    xml_path = "{}/{}".format(path_,xml_name)
    return data_file_path,xml_path,path_,filename

def GetCommentsInfo(relus,tr,index,sign):
    try:
        if sign: return "{}\n".format(re.findall(relus, str(tr.find_all("td")[index]))[0])
        else: return "{}".format(re.findall(relus, str(tr.find_all("td")[index]))[0])
    except:
        return "None\n"

def GetComments(comments_path):
    with open(comments_path, 'rb') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        comments_dict = {}
        for tr in soup.find_all("tr"):
            try:
                relus = '<td style="vnd.ms-excel.numberformat:@">(.*)</td>'
                relus_1 = '<td style="vnd.ms-excel.numberformat:@">([\s\S]*)</td>'
                # relus,str(tr.find_all("td")[0]))[0]
                # relus 规则
                # tr.find_all("td")[0]新的匹配节点的第一个数据
                # str() type是一个类所以需要字符串化
                # re.findall(...)[0]获得的结果第一个就是需要的数据
                case_number = re.findall(relus, str(tr.find_all("td")[0]))[0]
                index_list=[5,7,8,2]
                comm_str,comm_sign = "",True
                for i in range(len(index_list)):
                    if index_list[i] == index_list[-1]:comm_sign = False
                    comm_str += GetCommentsInfo(relus_1,tr,index_list[i],comm_sign)
                if platform.system() == "Linux":
                    comments_dict[case_number] = comm_str
                else:
                    comm_str = comm_str.replace('\r\n', '\n')
                    comments_dict[case_number] = comm_str
            except:
                pass
    return comments_dict

# 获得comments含有时间的 case
def GetNeedComments(comments_dict):
    need_comments_dict = {}
    for key, values in comments_dict.items():
        pattern = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}")
        m1 = pattern.findall(values)
        if m1:
            values_list = values.split(line_sign)
            values_list.insert(0,"Case Number:{}".format(key))
            values_list.insert(1, "Comment:")
            need_comments_dict[key] = values_list
    print("all_case_number:{}".format(len(comments_dict)))
    print("all message numbers:{}".format(len(need_comments_dict)))
    return need_comments_dict


def ProduceTXT(case_number, comments_list,case_id,case_owner,case_owner_alias,case_comments,Accept='Yes'):
    case_number = case_number.replace('\n', "")
    cnumber_str = "__CASE NUMBER__: " + case_number
    case_id_str = "__CASE ID__: " + case_id
    owner_str = "__OWNER__: " + case_owner
    owner_alias_str = "__MAIL__: " + case_owner_alias
    # output_str = "__OUTPUT__: "
    accept_str = "__ACCEPT__: " + Accept
    case_comments_str = "__COMMENTS__:" + '\n'
    for case in case_comments:
        for index in range(len(case)):
            case_comments_str += "{}{}".format(case[index],line_sign)
    produce_info_dict = {}

    for message in comments_list:
        comments_str = "__MESSAGE__:" + '\n'
        produce_info_list = []
        name_str = "__NAME__: " + "MSG_{}_{}".format(case_number, GetTime())
        time.sleep(0.01)
        if "//" == message[0][:2]:
            output_str = "__OUTPUT__: " + message[0]
        else:
            output_str = "__OUTPUT__: "
        if output_str != "__OUTPUT__: ":
            message=message[1:]
        for index_x in range(len(message)):
            if (index_x + 1) == len(message):
                comments_str += '\t\t' + message[index_x]
            else:
                comments_str += '\t\t' + message[index_x] + '\n'
        produce_info_list.append(name_str)
        produce_info_list.append(cnumber_str)
        produce_info_list.append(comments_str)
        produce_info_list.append(case_id_str)
        produce_info_list.append(owner_str)
        produce_info_list.append(owner_alias_str)
        produce_info_list.append(output_str)
        produce_info_list.append(accept_str)
        produce_info_list.append(case_comments_str)
        produce_info_dict[name_str] = produce_info_list
    return produce_info_dict

def WriteTxt(produce_info_list2):
    data_file_path, xml_path,path_,filename = split_path(comments_path)
    with open(data_file_path,'w') as f:
        for single_produce in produce_info_list2:
            for data in single_produce:
                f.write("{}\n".format(data))
            f.write("{}\n".format("*" *60))

def ReadTxt(data_file_path):
    #二维列表，每个一维列表都是一组完整的数据
    all_list = []
    # 从data.txt文件中读出所有内容放到xml_list中
    xml_list = []
    name_list = []
    number_list = []
    message_list = []
    caseid_list = []
    owner_list = []
    owner_alias_list = []
    output_list = []
    accept_list = []
    comments_list = []
    with open(data_file_path, 'rb') as f:
        for line in f.readlines():
            line = line.replace('\r\n', '').replace('\n', '')
            xml_list.append(line)

    begin = 0
    for index in range(begin, len(xml_list)):
        if "*" * 60 == xml_list[index]:
            all_list.append(xml_list[begin:index + 1])
            begin = index + 1

    for single_list in all_list:
        for single_index in range(len(single_list)):
            if "__NAME__: " in single_list[single_index]:
                name = str(single_list[single_index].split(":")[1]).lstrip()
                name_list.append(name)
            if "__CASE NUMBER__: " in single_list[single_index]:
                number = str(single_list[single_index].split(':')[1]).lstrip()
                number_list.append(number)
            if "__MESSAGE__:" in single_list[single_index]:
                for message_index in range(single_index, len(single_list)):
                    if "__CASE ID__: " in single_list[message_index]:
                        message_list.append(single_list[single_index + 1:message_index])
            if "__CASE ID__: " in single_list[single_index]:
                case_id = str(single_list[single_index].split(":")[1]).lstrip()
                caseid_list.append(case_id)
            if "__OWNER__: " in single_list[single_index]:
                owner = str(single_list[single_index].split(":")[1]).lstrip()
                owner_list.append(owner)
            if "__MAIL__: " in single_list[single_index]:
                owner_alias = str(single_list[single_index].split(":")[1]).lstrip()
                owner_alias_list.append(owner_alias)
            if "__OUTPUT__: " in single_list[single_index]:
                out = str(single_list[single_index].split(":")[1])
                output_list.append(out)
            if "__COMMENTS__:" in single_list[single_index]:
                for index_s in range(single_index, len(single_list)):
                    if "*" * 60 in single_list[index_s]:
                        comments_list.append(single_list[single_index + 1:index_s - 1])
            if "__ACCEPT__: " in single_list[single_index]:
                accept = str(single_list[single_index].split(":")[1]).lstrip()
                accept_list.append(accept)

    for atr in accept_list:
        if atr == "Yes":
            new_xml_list = ProduceXML(name_list, number_list, message_list, caseid_list, owner_list, owner_alias_list, output_list,comments_list)
            for name_index in range(len(new_xml_list)):
                WriteXML(new_xml_list[name_index],owner_list[name_index], name_list[name_index])

# 生成xml
def ProduceXML(name_list,number_list,message_list,caseid_list,owner_list,owner_alias_list,output_list,com_list):
    new_xml_list = []
    for index in range(len(name_list)):
        produce_info_list = [
            '<State name="{}" number="{}" case_id="{}" owner="{}" owner_alias="{}" output="{}">',
            '\n\t<Message>\n{}',
            '\n\t</Message>',
            '\n\t<Comments>\n{}',
            '\n\t</Comments>\n<State>'
        ]
        name_str = name_list[index]
        num_str = number_list[index]
        case_id_str = caseid_list[index]
        owner_str = owner_list[index]
        owner_alias_str = owner_alias_list[index]
        output_str = output_list[index]
        mess_str = ""
        comments_str = "\t"
        for index_x in range(len(message_list[index])):
            if (index_x + 1) == len(message_list[index]):
                mess_str += message_list[index][index_x]
            else:
                mess_str += message_list[index][index_x] + "\n"
        for index_y in range(len(com_list[index])):
            if (index_y + 1) == len(com_list[index]):
                comments_str += com_list[index][index_y]
            else:
                comments_str += com_list[index][index_y] + '\n'
        produce_info_list[0] = produce_info_list[0].format(name_str, num_str, case_id_str, owner_str, owner_alias_str, output_str)
        produce_info_list[1] = produce_info_list[1].format(mess_str)
        produce_info_list[3] = produce_info_list[3].format(comments_str)
        new_xml_list.append(produce_info_list)
    return new_xml_list

# 写xml文件
def WriteXML(xml_list,case_owner, file_):
    data_file_path, xml_path, path_,filename = split_path(comments_path)
    global new_xml_path
    new_xml_path = "{}/{}".format(xml_path, case_owner)
    if not os.path.isdir(new_xml_path):
        os.makedirs(new_xml_path)
    file_ = "{}/{}.xml".format(new_xml_path, file_)
    with open(file_, "w") as f:
        for xml in xml_list:
            f.write(xml)
    # print ("owner is {},xml is {}".format(case_owner, new_xml_path))

# 获得当前系统时间到毫秒级
def GetTime():
    # 格式化成2016-03-20 11:45:39形式
    time_ = str(time.time())
    temp_list = time_.split(".")
    #:.2表示输出字符串的宽度为：2
    return "{}_{:.2}".format(time.strftime("%Y%m%d_%H%M%S", time.localtime()), temp_list[1])


#联合条件匹配规则
def contain(index,comm,line_list,rules_):
    sign = True
    pattern_4 = re.compile(rules_)
    for index_x in range(index+1, len(comm)):
        line_t = pattern_4.findall(comm[index_x])
        if line_t:
            line_list.append(line_t[0])
            sign = False
        else:
            if len(line_list) == 0:
                return sign,[comm[index]]
            return sign,line_list

#获取含有c和cpp的
def GetCppC_list(comm):
    line_list = []
    #按照时间戳分组之后的二维列表
    new_line_list = []
    finall_list = []
    dict_ = {}
    global begin
    begin = 0
    pattern_1 = re.compile(r"^//.+")
    pattern = re.compile(r"(\d{2}:\d{2}:\d{2})")
    for index in range(begin, len(comm)):
        if (".cpp " in comm[index]) or (".c " in comm[index]):
            line_list.append([index,comm[index]])

    for mess in line_list:
        line = pattern.search(mess[1])
        lines = line.group(1)
        if lines in dict_:
            dict_[lines].append(mess[1])
        else:
            dict_.setdefault(lines, [mess[1]])
            dict_[lines].append(mess[0])
    for key, val in dict_.items():
        new_line_list.append(val)
    # print("new_line_list:({})".format(new_line_list)) new_line_list = [[message,number(行号),message],[message,num]]

    for line_list_t in new_line_list:
        temp=comm[:int(line_list_t[1])]
        temp_list = temp[::-1]
        sign = True
        for tl in temp_list:
            line = pattern_1.findall(tl)
            if line:
                line_list_t.insert(0,line[0])
                finall_list.append(line_list_t[:2]+line_list_t[3:])
                sign = False
                break
            else:
                pass
        if sign:
            finall_list.append(line_list_t[:1]+line_list_t[2:])
    return finall_list

def GetNew_list(comm):
    line_list = []
    global begin
    begin = 0
    for index in range(begin, len(comm)):
        # 以时间戳开头且下一个字符是空格的，取整行
        pattern_1 = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}.+")
        # 非日期开头但是有时间的，取时间以及以后的内容
        pattern_2 = re.compile(r"\s+\d{2}:\d{2}:\d{2}\.\d{3}.+")
        # 以日期开头且后面是时间戳的且后面不跟\t的，取整行
        pattern_3 = re.compile(r"^\d{4}\s\w+\s{1,2}\d{1,2}\s{2}\d{2}:\d{2}:\d{2}\.\d{3}.+")
        pattern_6 = re.compile(r"^\d+\s\d+\s\d{4}\s\w+\s{1,2}\d{1,2}\s{2}\d{2}:\d{2}:\d{2}\.\d{3}.+")
        # 以日期开头且后面是时间戳的且后面跟\t的，取该行以及后面的所有\t开头的 为一条信息
        sign = True
        line4 = pattern_3.findall(comm[index])
        if sign and line4:
            sign, temp_list = contain(index, comm, line4, r"^\s{4}.+")
            if len(temp_list) != 1:
                line_list.append(temp_list)

        line3 = pattern_3.findall(comm[index])
        if sign and line3:
            start = index + 1
            list_s = []
            for index_3 in range(start, len(comm)):
                if "" == comm[index_3]:
                    list_s.extend(comm[start:index_3])
                    break

            list_s.insert(0, line3[0])
            comb_str = list_s[0] + '\n'
            for index_comb in range(1, len(list_s)):
                if (index_comb + 1) == len(list_s):
                    comb_str += "{}{}".format("\t" * 2, list_s[index_comb])
                else:
                    comb_str += "{}{}".format("\t" * 2, list_s[index_comb]) + "\n"
            line_list.append([comb_str])
            sign = False

        line5 = pattern_1.findall(comm[index])
        if sign and line5:
            try:
                sign, temp_list = contain(index, comm, line5, r"^\s{4}.+")
            except:
                sign = False
                temp_list = line5
            if len(temp_list) != 1:
                line_list.append(temp_list)

        line6 = pattern_6.findall(comm[index].strip())
        if sign and line6:
            line6 = line6[0].split(" ")
            num = line6[1]
            try:
                sign, temp_list = contain(index, comm, line5, r"{}(.+)".format(num))
                if len(temp_list):
                    line2 = pattern_2.findall(comm[index])
                    for line in line2:
                        line = line.lstrip()
                        temp_list.insert(0,line)
            except:
                sign = False
                temp_list = []
            temp_str = temp_list[0] + "\n"
            for str_index in range(1,len(temp_list)):
                if (str_index + 1) == len(temp_list):
                    temp_str += "{}{}".format("\t" * 3, temp_list[str_index].strip())
                else:
                    temp_str += "{}{}".format("\t" * 3,temp_list[str_index].strip()) + '\n'
            if "Message Direction = To UE" not in temp_str:
                line_list.append([temp_str])

        line2 = pattern_2.findall(comm[index])
        lines_2 = []
        for line in line2:
            line = line.lstrip()
            lines_2.append(line)
        if sign and lines_2:
            line_list.append(lines_2)
            sign = False

        line1 = pattern_1.findall(comm[index])
        if sign and line1:
            try:
                if "[0x" not in line1[0]:
                    line_list.append(line1)
                    sign = False
            except:
                pass
    return line_list

#获取case_comments
def GetCase_comments(comm):
    case_comments = []
    case_comments.append(comm[:])
    return case_comments


#统计符合条件的comments 数量
def count_ratio(case_comments,hit_count,hit_list,hit_caseid_list,case_id):
    sign=False
    pattern = re.compile(r"\d{8}\s+\d{2}:\d{2}:\d{2}\.\d{3}")
    pattern_1 = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}, Summary")
    pattern_2 = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}, Comment")
    for single_message in case_comments[0]:
        single_message = single_message.lstrip()
        line = pattern.search(single_message)
        if not line:
            line = pattern_1.search(single_message)
            if not line:
                line = pattern_2.search(single_message)
        if line:
            line = line.group()
            hit_count += 1
            hit_list.append(case_comments[0])
            hit_caseid_list.append(case_id)
            sign = True
            break
    return hit_count,hit_list,hit_caseid_list,sign

#命中的comments
def write_hit_comments(hit_list):
    file_name, xml_path, path_,filename = split_path(comments_path)
    path_ = "{}/{}".format(path_,filename + '_hit_comments.txt')
    if "(v2." in sys.version:
        with open(path_, "w",) as f:
            for single_hit_list in hit_list:
                for sing_hit in single_hit_list:
                    f.write("{}\n".format(sing_hit))
                f.write("{}\n".format("*" * 60))
    elif ("(v3." in sys.version or ("3." in sys.version and "|Anaconda" in sys.version)):
        f = codecs.open(path_, "w", "utf-8")
        for single_hit_list in hit_list:
            for sing_hit in single_hit_list:
                f.write("{}\n".format(sing_hit))
            f.write("{}\n".format("*" * 60))

#未命中的comments
def write_unhit_comments(unhit_list):
    file_name, xml_path, path_,filename = split_path(comments_path)
    path_ = "{}/{}".format(path_, filename + '_unhit_comments.txt')
    if "(v2." in sys.version:
        with open(path_, "w",) as f:
            for single_hit_list in unhit_list:
                for sing_hit in single_hit_list:
                    f.write("{}\n".format(sing_hit))
                f.write("{}\n".format("*" * 60))
    elif ("(v3." in sys.version or ("3." in sys.version and "|Anaconda" in sys.version)):
        f = codecs.open(path_, "w", "utf-8")
        for single_hit_list in unhit_list:
            for sing_hit in single_hit_list:
                f.write("{}\n".format(sing_hit))
            f.write("{}\n".format("*" * 60))


#命中的case_id
def write_hit_caseid(hit_caseid_list,):
    file_name, xml_path, path_,filename = split_path(comments_path)
    path_ = "{}/{}".format(path_, filename + '_hit_caseid_list.txt')
    if "(v2." in sys.version:
        with open(path_, "w", ) as f:
            for hit_caseid in hit_caseid_list:
                f.write("{}\n".format(hit_caseid))
    elif ("(v3." in sys.version or ("3." in sys.version and "|Anaconda" in sys.version)):
        f = codecs.open(path_, "w", "utf-8")
        for hit_caseid in hit_caseid_list:
            f.write("{}\n".format(hit_caseid))


#创建exl文件
def CreateXml(comments_list):
    produce_info_list2 = []
    all_write_data = 0
    hit_count = 0
    hit_list,unhit_list,hit_caseid_list = [],[],[]
    for comm in comments_list:
        #得到case id
        case_id = re.findall(r"(.+)", comm[2])[0]
        #得到owner
        case_owner = re.findall(r"(.+)", comm[3])[0]
        # 得到case_owner别名
        case_owner_alias = re.findall(r"(.+)", comm[4])[0]
        #case number
        case_num = re.findall("Case Number:(\d+)", comm[0])[0]
        # 获得case_comments
        case_comments = GetCase_comments(comm[5:])
        Accept = 'Yes'
        # xml相关标签
        # xml_name = "MSG_{}_{}".format(case_num, GetTime())  # xml名称，唯一标识
        #取出所有符合条件的message组成一个二维列表
        new_list = GetNew_list(comm)
        cpp_c_list = GetCppC_list(comm)
        #统计命中率
        hit_count, hit_list, hit_caseid_list, hit_sign = count_ratio(case_comments, hit_count, hit_list,
                                                                     hit_caseid_list, case_id)
        if not hit_sign:
            unhit_list.append(case_comments[0])
        write_hit_comments(hit_list)
        write_unhit_comments(unhit_list)
        write_hit_caseid(hit_caseid_list)
        #降为一维列表
        # lists = []
        # for single in new_list:
        #     lists += single

        # 如果message信息超过10条将不执行
        # if ((len(lists) <= line_num) and (len(lists) > 0)):
        if ((len(cpp_c_list) <= line_num) and (len(cpp_c_list) > 0)):
            all_write_data += 1
            produce_info_dict = ProduceTXT(case_num, cpp_c_list, case_id, case_owner,case_owner_alias,case_comments,Accept)
            for key,produce_info_list in produce_info_dict.items():
                produce_info_list2.append(produce_info_list)
                WriteTxt(produce_info_list2)
                sleep(0.01)

    print("writen in total comments is:{}".format(all_write_data))
    print("the hit comments is:{}".format(hit_count))


def Main():
    # 命令行传递需要解析的生成xml的文件，必须满足固定的格式
    if ".txt" in sys.argv[1]:
        data_file_path, xml_path,path_,filename = split_path(comments_path)
        ReadTxt(data_file_path)
        exit()
    elif ".xls" in sys.argv[1]:
        # 从html获得数据提取comments
        comments_dict = GetComments(comments_path)
        # 筛选comments
        need_comments_dict = GetNeedComments(comments_dict)
        # 将筛选结果存入列表
        comms_list=[]
        for key,vals in need_comments_dict.items():
            comms_list.append(vals)
        CreateXml(comms_list)


if __name__ == "__main__":
    Main()

