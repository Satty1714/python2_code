# coding:utf-8
# python 2.7
import os, sys
import re
import time
import platform
from bs4 import BeautifulSoup
from time import sleep
reload(sys)
sys.setdefaultencoding('utf-8')

# comments数据位置，从html提取的位置
comments_path = r'/home/fanghao/workspace/write_excel/CaseComment.xls'
# 筛选符合条件的comments保存的位置；只还有cpp和c的comments的全部内容
screen_comments_path = r'/home/fanghao/workspace/write_excel/case1.txt'
# xmlpath
xml_path = "/home/fanghao/workspace/write_excel/xml"
exl_path = "data_excel.xls"

# 如果cpp或者c的开始字符包含在一下字符串则不写入xml
eliminate_char_list = ["-", "+", "*"]

def GetComments(comments_path):
    with open(comments_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        # print soup
        # print len(soup.find_all("tr"))
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
                comments_dict[case_number] = re.findall(relus_1, str(tr.find_all("td")[6]))[0] + "\n" + \
                                             re.findall(relus_1, str(tr.find_all("td")[7]))[0] + "\n" + \
                                             re.findall(relus_1, str(tr.find_all("td")[2]))[0]
            except:
                pass
    return comments_dict

#读取xml内容
def ReadxmlComments(path_):
    comments_list = []
    with open(path_, 'r') as f:
        lines = f.readlines()
        index_begin = 0
        temp_list = []
        for index in range(len(lines)):
            if index == 0:
                index_begin = index
            else:
                if "Case Number:".lower() in lines[index].lower():
                    temp_list = lines[index_begin:index]
                    comments_list.append(temp_list[:])
                    temp_list = []
                    index_begin = index
                if index == len(lines) - 1:
                    comments_list.append(lines[index_begin:])
    return comments_list

# 获得comments含有时间的 case
def GetNeedComments(comments_dict):
    need_comments_dict = {}
    for key, values in comments_dict.items():
        pattern1 = re.compile(r"\d{2}:\d{2}:\d{2}.\d{3}")
        m1 = pattern1.findall(values)
        if m1:
            need_comments_dict[key] = values
    print("all_case_number:{}".format(len(comments_dict)))
    print("all message numbers:{}".format(len(need_comments_dict)))
    return need_comments_dict

def WriteInfo(need_comments_dict):
    with open(screen_comments_path, "w") as f:
        for key, values in need_comments_dict.items():
            f.write("Case Number:{}\nComment:\n{}\n".format(key, values))
            f.write("{}\n".format("#" * 60))

def ProduceEXL(names, output_list, comments_list,related_crs,cases_owner,case_comments):
    produce_info_list = []
    name =[]
    name.append(names)
    name_str = ""
    output_str = ""
    comments_str = ""
    relate_str = ""
    owner_str = ""
    case_comments_str = ""
    for index in range(len(output_list)):
        output_list[index] = output_list[index].replace("\n", "")
    for out in output_list:

        # output 不输出条件
        # 1 字符串前两个为//不存储
        if "//" == out[0:2]: continue
        # 2 hi(不分大小写),转换小写比较
        if "hi" == out[0:2].lower(): continue
        # 3 使用dear Dear Customer
        if ("dear" == out[0:5].lower() and ('customer' not in out.lower())): continue
        # 4 只是空格的跳过
        # print("out:({})".format(len(out)))
        if not len(out):
            print("out:({})".format(out))
            continue
        output_str += out
    for index in range(len(comments_list)):
        if (index + 1) == len(comments_list):
            comments_str += "\t\t" + comments_list[index]
        else:
            comments_str += "\t\t" + comments_list[index] + "\n"
    for c in case_comments:
        for index in range(len(c)):
            case_comments_str += c[index]
    for n in name:
        name_str += n
    for crs in related_crs:
        relate_str += crs
    for owner in cases_owner:
        owner_str += owner
    produce_info_list.append(name_str)
    produce_info_list.append(output_str)
    produce_info_list.append(comments_str)
    produce_info_list.append(relate_str)
    produce_info_list.append(owner_str)
    produce_info_list.append(case_comments_str)
    return produce_info_list

# 生成xml
def ProduceXML(name, output_list, comments_list, mode="and"):
    produce_info_list = [
        '<State name="{}" mode="{}" output="{}">',
        '\n\t</Message>\n{}',
        '\n\t</Message>\n</State>'
    ]
    output_str = ""
    comments_str = ""
    for index in range(len(output_list)):
        output_list[index] = output_list[index].replace("\n", "")
    for out in output_list:

        # output 不输出条件
        # 1 字符串前两个为//不存储
        if "//" == out[0:2]: continue
        # 2 hi(不分大小写),转换小写比较
        if "hi" == out[0:2].lower(): continue
        # 3 使用dear Dear Customer
        if ("dear" == out[0:5].lower() and ('customer' not in out.lower())): continue
        # 4 只是空格的跳过
        # print("out:({})".format(len(out)))
        if not len(out):
            print("out:({})".format(out))
            continue
        output_str += out
    for index in range(len(comments_list)):

        if (index + 1) == len(comments_list):
            comments_str += "\t\t" + comments_list[index]
        else:
            comments_str += "\t\t" + comments_list[index] + "\n"
    produce_info_list[0] = produce_info_list[0].format(name, mode, output_str)
    produce_info_list[1] = produce_info_list[1].format(comments_str)
    return produce_info_list

def WriteEXL(produce_info_list2):
    import xlwt
    file = xlwt.Workbook(encoding='utf-8')
    table = file.add_sheet('data', cell_overwrite_ok=True)
    table_head = ['name', 'case_number', 'message','related_crs','case_owner','case_comments']
    for i in range(len(table_head)):
        table.write(0, i, table_head[i])
    for row in range(len(produce_info_list2)):
        for col in range(0, len(produce_info_list2[row])):
            table.write(row + 1, col, produce_info_list2[row][col])
    file.save(exl_path)

# 写xml文件
def WriteXML(xml_list, file_):
    # path_= r"C:\SUNYAN\20180821_xml\xml_test"
    if not os.path.isdir(xml_path):
        os.makedirs(xml_path)
    file_ = "{}/{}.xml".format(xml_path, file_)
    with open(file_, "w") as f:
        for xml in xml_list:
            f.write(xml)

# 获得当前系统时间到毫秒级
def GetTime():
    # 格式化成2016-03-20 11:45:39形式
    time_ = str(time.time())
    temp_list = time_.split(".")
    #:.2表示输出字符串的宽度为：2
    return "{}_{:.2}".format(time.strftime("%Y%m%d_%H%M%S", time.localtime()), temp_list[1])

#联合条件匹配规则
def contain(index,comm,line_list):
    sign = True
    pattern_4 = re.compile(r"^\s{4}.+\n")
    for index_x in range(index+1, len(comm)):
        line_t = pattern_4.findall(comm[index_x])
        if line_t:
            line_list.append(line_t[0])
            sign = False
        else:
            return sign,line_list

def GetNew_list(comm):
    line_list = []
    global begin
    begin = 0
    for index in range(begin, len(comm)):
        # 以时间戳开头且下一个字符是空格的，取整行
        pattern_1 = re.compile(r"^\d{2}:\d{2}:\d{2}.\d{3}.+\n")
        # 非日期开头但是有时间的，取时间以及以后的内容
        pattern_2 = re.compile(r" \d{2}:\d{2}:\d{2}.\d{3}.+\n")
        # 以日期开头且后面是时间戳的且后面不跟\t的，取整行
        pattern_3 = re.compile(r"^\d{4}\s\w+\s{1,2}\d{1,2}\s{2}\d{2}:\d{2}:\d{2}.\d{3}.+\n")
        # 以日期开头且后面是时间戳的且后面跟\t的，取该行以及后面的所有\t开头的 为一条信息
        sign = True
        line4 = pattern_3.findall(comm[index])
        if sign and line4:
            sign, temp_list = contain(index, comm, line4)
            if len(temp_list) != 1:
                line_list.append(temp_list)

        line3 = pattern_3.findall(comm[index])
        if sign and line3:
            line_list.append(line3)
            sign = False

        line5 = pattern_1.findall(comm[index])
        if sign and line5:
            sign, temp_list = contain(index, comm, line5)
            if len(temp_list) != 1:
                line_list.append(temp_list)

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
            line_list.append(line1)
            sign = False
    return line_list
#获取case_comments
def GetCase_comments(comm):
    case_comments = []
    case_comments.append(comm[:-1])
    return case_comments


#创建exl文件
def CreateExl(comments_list):
    produce_info_list2 = []
    for comm in comments_list:
        output_list = []
        # relateds_crs = []
        related_crs = (re.findall(r"(\d+)[\r\n|\n]", comm[2]))
        cases_owner = []
        case_owner = str(re.findall(r"(.+)", comm[3])[0])
        cases_owner.append(case_owner)
        sysstr = platform.system()
        if sysstr == "Linux":
            case_num = str(re.findall("Case Number:(.+?)[\r\n|\n]", comm[0])[0])
            output_list.append(case_num)
        else:
            case_num = str(re.findall("Case Number:(.+?)[\r\n|\n]", comm[0])[0])
            output_list.append(case_num)
        # 获得xml中message内容
        # cpp_c_list = GetCppC_list(comm[2:])
        new_list = GetNew_list(comm)
        case_comments = GetCase_comments(comm[4:])
        # xml相关标签
        xml_name = "MSG_{}_{}".format(output_list[0], GetTime())  # xml名称，唯一标识
        # mode = "and"  # xml模式
        # 如果message信息超过10条将不执行
        for lists in new_list:
            if ((len(lists) <= 10) and (len(lists) > 0)):
                produce_info_list = ProduceEXL(xml_name, output_list, lists, related_crs, cases_owner,case_comments)
                produce_info_list2.append(produce_info_list)
                WriteEXL(produce_info_list2)
                sleep(0.1)

def Main():
    # print sys.argv;
    # 命令行传递需要解析的生成xml的文件，必须满足固定的格式
    if len(sys.argv) > 1:
        #********************
        if ".xls" in sys.argv[1]:
            import xlrd
            data = xlrd.open_workbook(exl_path)
            table = data.sheets()[0]
            nrows = table.nrows
            with open("test.txt", "w") as f:
                for i in range(1, nrows):
                    rows_values = table.row_values(i)
                    for j in rows_values:
                        f.write("{}\n".format(j))
                    f.write("{}\n".format("*" *70))
        else:
            comments_list = ReadxmlComments(sys.argv[1])
            CreateExl(comments_list)

        exit()
    # 从html获得数据提取comments
    comments_dict = GetComments(comments_path)
    # 筛选comments
    need_comments_dict = GetNeedComments(comments_dict)
    # 将筛选结果存入文件
    WriteInfo(need_comments_dict)
    comments_list = ReadxmlComments("{}/case1.txt".format(os.path.split(os.path.realpath(__file__))[0]))
    CreateExl(comments_list)

if __name__ == "__main__":
    Main()

