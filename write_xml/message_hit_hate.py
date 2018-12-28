# -*- coding:utf-8 -*-
# python 2.7

import os, sys
import re
import time
import codecs
import platform
import xlwt
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
    # txt_name = filename + ".txt"
    xml_name = filename + "_hit"
    # data_file_path = "{}/{}".format(path_,txt_name)
    xml_path = "{}/{}".format(path_,xml_name)
    # return data_file_path,xml_path,path_
    return filename,xml_path,path_


def GetCommentsInfo(relus,tr,index,sign):
    try:
        if sign: return "{}\n".format(re.findall(relus, str(tr.find_all("td")[index]))[0])
        else: return "{}".format(re.findall(relus, str(tr.find_all("td")[index]))[0])
    except:
        return "None\n"

def GetComments(comments_path):
    with open(comments_path, 'rb') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        comments_list= []
        for tr in soup.find_all("tr"):
            relus = '<td style="vnd.ms-excel.numberformat:@">(.*)</td>'
            relus_1 = '<td style="vnd.ms-excel.numberformat:@">([\s\S]*)</td>'
            # relus,str(tr.find_all("td")[0]))[0]
            # relus 规则
            # tr.find_all("td")[0]新的匹配节点的第一个数据
            # str() type是一个类所以需要字符串化
            # re.findall(...)[0]获得的结果第一个就是需要的数据
            comments_dict = {}
            try:
                case_number = re.findall(relus, str(tr.find_all("td")[0]))[0]
                index_list=[5,2]
                comm_str,comm_sign = "",True
                for i in range(len(index_list)):
                    if index_list[i] == index_list[-1]:comm_sign = False
                    comm_str += GetCommentsInfo(relus_1,tr,index_list[i],comm_sign)
                    comm_str = comm_str.replace('\r\n', '\n')
                    comments_dict[case_number] = comm_str
            except:
                pass
            comments_list.append(comments_dict)
    return comments_list


def GetNeedComments(comments_list):
    need_comments_list = []
    for sing_dict in comments_list:
        for key,values in sing_dict.items():
            values_list = values.split(line_sign)
            values_list.insert(0,"Case Number:{}".format(key))
            values_list.insert(1,"Comment:")
            need_comments_list.append(values_list)

    return need_comments_list

def GetCppC_list(comm,case_id):
    line_list = []
    global begin
    begin = 0
    for index in range(begin,len(comm)):
        # if (".cpp " in comm[index]) or (".c " in comm[index]):
        if ("Dear customer" in comm[index]) or ("Dear Customer" in comm[index]):
            comments = comm[3:]
            comments.insert(0,case_id)
            line_list.extend(comments)
            break
    return line_list

#获取case_comments
def GetCase_comments(comm):
    case_comments = []
    case_comments.append(comm[:])
    return case_comments


def get_new_list(need_comments_list):
    file_name, xml_path, path_ = split_path(comments_path)
    if not os.path.isdir(xml_path):
        os.makedirs(xml_path)
    path_ = "{}/{}".format(xml_path, file_name + '_all_caseid.txt')
    txt_path = "{}/{}".format(xml_path, file_name + '_finally_caseid.txt')
    list_ = []
    for comm in need_comments_list:
        line_list = []
        case_id = str(re.findall(r"(.+)", comm[2])[0])
        for index in range(0, len(comm)):
            comments = comm[3:]
            comments.insert(0, case_id)
            line_list.extend(comments)
            break
        list_.append(line_list)

    pattern = re.compile(r"\d{8}\s+\d{2}:\d{2}:\d{2}\.\d{3}")
    pattern_1 = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}, Summary")
    pattern_2 = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}, Comment")
    pattern_3 = re.compile(r"\\Checkpoint")

    with open(path_, 'a') as f:
        for single_list in list_:
            sign = True
            for single_index in range(len(single_list)):
                single_message = single_list[single_index].lstrip()
                line = pattern.search(single_message)
                if not line:
                    line = pattern_1.search(single_message)
                    if not line:
                        line = pattern_2.search(single_message)
                        if not line:
                            line = pattern_3.search(single_message)

                if line:
                    # hit_list.append("{}-{}-{}".format(single_list[1:],single_list[0],'1'))
                    f.write("{};{}\n".format(single_list[0], '1'))
                    # f.write("{}\n".format('1'))
                    # hit_count += 1
                    # hit_list.append(single_list[:])
                    # hit_caseid_list.append(single_list[0])
                    sign = False
                    break

            if sign:
                f.write("{};{}\n".format(single_list[0],'0'))
                # f.write("{}\n".format('0'))
                # unhit_list.append(single_list[1:])

    if os.path.exists(path_):
        with open(path_,'r') as f :
            lists = f.readlines()
        caseid_list = []
        for caseid in lists:
            caseid = caseid.replace('\n','')
            if ";1" in caseid:
                caseid_list.append(caseid)
        caseid_set = list(set(caseid_list))
        for temp_caseid in caseid_set:
            temp = temp_caseid.split(';')
            with open(txt_path,'a') as f:
                f.write("{}\n".format(temp[0]))


    # return hit_count, hit_list, hit_caseid_list, unhit_list


#统计符合条件的comments 数量
def count_ratio(case_comments,hit_count,hit_list,hit_caseid_list,unhit_list):

    # pattern = re.compile(r"\d{6}\s+\d{2}:\d{2}:\d{2}\.\d{3}")
    pattern = re.compile(r"\d{8}\s+\d{2}:\d{2}:\d{2}\.\d{3}")
    pattern_1 = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}, Summary")
    pattern_2 = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}, Comment")
    pattern_3 = re.compile(r"\\Checkpoint")

    for single_list in case_comments:
        sign = True
        for single_index in range(len(single_list)):
            single_message = single_list[single_index].lstrip()
            line = pattern.search(single_message)
            if not line:
                line = pattern_1.search(single_message)
                if not line:
                    line = pattern_2.search(single_message)
                    if not line:
                        line = pattern_3.search(single_message)

            if line:
                hit_count += 1
                hit_list.append(single_list[:])
                hit_caseid_list.append(single_list[0])
                sign = False
                break
        if sign:
            unhit_list.append(single_list[1:])

    return hit_count, hit_list, hit_caseid_list,unhit_list


#命中的comments
def write_hit_comments(hit_list):
    file_name, xml_path, path_ = split_path(comments_path)
    if not os.path.isdir(xml_path):
        os.makedirs(xml_path)
    path_ = "{}/{}".format(xml_path,file_name + '_hit_comments.txt')
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
    file_name, xml_path, path_ = split_path(comments_path)
    if os.path.exists(xml_path):
        path_ = "{}/{}".format(xml_path,file_name + '_unhit_comments.txt')
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
    file_name, xml_path, path_ = split_path(comments_path)
    if os.path.exists(xml_path):
        path_ = "{}/{}".format(xml_path,file_name + '_hit_caseid_list.txt')
    if "(v2." in sys.version:
        with open(path_, "w", ) as f:
            for hit_caseid in hit_caseid_list:
                f.write("{}\n".format(hit_caseid))
    elif ("(v3." in sys.version or ("3." in sys.version and "|Anaconda" in sys.version)):
        f = codecs.open(path_, "w", "utf-8")
        for hit_caseid in hit_caseid_list:
            f.write("{}\n".format(hit_caseid))


#创建exl文件
def Write_txt(comments_list):
    hit_count = 0
    hit_list = []
    unhit_list = []
    hit_caseid_list = []
    list_ = []
    for comm in comments_list:
        #得到case id
        case_id = str(re.findall(r"(.+)", comm[2])[0])
        #得到case_comments
        # case_comments = GetCase_comments(comm[3:]) #二维列表[[]]
        cpp_c_list = GetCppC_list(comm,case_id)
        if len(cpp_c_list):
            list_.append(cpp_c_list)

    hit_count, hit_list, hit_caseid_list, unhit_list = count_ratio(list_, hit_count, hit_list,
                                                                     hit_caseid_list,unhit_list)

    write_hit_comments(hit_list)
    write_unhit_comments(unhit_list)
    write_hit_caseid(hit_caseid_list)
    print('total count is:{}'.format(len(comments_list)))
    print("the hit comments is:{}".format(hit_count))


def Main():
    # 命令行传递需要解析的生成xml的文件，必须满足固定的格
    if ".xls" in sys.argv[1]:
        # 从html获得数据提取comments
        # comments_dict = GetComments(comments_path)
        comments_list = GetComments(comments_path)
        # 筛选comments
        need_comments_list = GetNeedComments(comments_list)
        # Write_txt(need_comments_list)
        get_new_list(need_comments_list)


if __name__ == "__main__":
    Main()

