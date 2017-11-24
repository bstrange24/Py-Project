import logging
import time
import urllib.request
import re
from bs4 import BeautifulSoup, Comment
import string

# Call time clock for performance statistics
time.clock()

# set up logging properties
fmt = '%(asctime)s %(levelname)s %(lineno)s %(message)s'
logging.basicConfig(level='INFO', format=fmt, filename=r'C:\Users\hduser\PycharmProjects\Project\Project.log', datefmt='%m-%d-%Y %I:%M:%S %p')
logger = logging.getLogger('Project')

# Initialize list and maps
pitching_table = []
fan_graph_mapping = {}
temp_dict = {}
b_ref_data = []
b_ref_mapping = {}

baseball_reference_header = 'Name,Age,Tm,Lg,W,L,WL_Perct,ERA,G,GS,GF,CG,SHO,SV,IP,H,R,ER,HR,BB,IBB,SO,HBP,BK,WP,BF,ERA_Plus,FIP,WHIP,H9,HR9,BB9,SO9,SO_W,'
fan_graph_header = 'FB_Perct,FB_Vel,SL_Perct,SL_Vel,CT_Perct,CT_Vel,CB_Perct,CB_Vel,CH_Perct,CH_Vel,SF_Perct,SF_Vel,KN_Perct,KN_Vel,XX_Perct'
columns = baseball_reference_header + fan_graph_header

pages = list(range(1, 11))
years = list(range(2000, 2018))

# Make any empty fields zero '0'
def zero_out_empty_fields(field):
    if field.isspace():
        field = '0'
        return field
    else:
        return field

# Make any empty fields zero '0'
def add_space(field):
    filtered = field.replace(u'\xa0', ' ')
    return filtered

logger.info("*** Starting Project ***")
for year in years:
    base_url = 'http://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=30&type=4&season=' + str(year) + '&month=0&season1=' + str(year) + '&ind=0&team=0&rost=0&age=17,58&filter=&players=0&page='
    logger.info("Base URL :: " + str(base_url))
    bball_reference_file = r'C:\Users\hduser\Desktop\project\baseball_ref\\' + str(year) + '_baseball_reference.csv'
    consolidated_file = r'C:\Users\hduser\Desktop\project\consolidated\\' + str(year) + '_consolidated.csv'

    try:
        for page in pages:
            url = base_url + str(page) + "_50"
            logger.debug("URL :: " + str(url))
            soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

            for division in soup.findAll("tr", {"class": "rgRow"})[0:]:
                for conf in division.findAll("td", {"class": "grid_line_regular"}):
                    if conf.find("a") is not None:
                        pitching_table.append(conf.find("a").contents[0])
                    else:
                        pitching_table.append(conf.contents[0])

                pitcher_name = pitching_table[1].replace('\'', ' ')
                pitcher_name = str(pitcher_name.replace('.', ' '))
                fan_graph_mapping[pitcher_name] = pitching_table[3:]
                pitching_table.clear()

            for division in soup.findAll("tr", {"class": "rgAltRow"})[0:]:
                for conf in division.findAll("td", {"class": "grid_line_regular"}):
                    if conf.find("a") is not None:
                        pitching_table.append(conf.find("a").contents[0])
                    else:
                        pitching_table.append(conf.contents[0])

                pitcher_name = pitching_table[1].replace('\'', ' ')
                pitcher_name = str(pitcher_name.replace('.', ''))
                fan_graph_mapping[pitcher_name] = pitching_table[3:]
                pitching_table.clear()

            # Clear url. This is done to go to the next web page
            url = ''
    except RuntimeError as run_time_error:
        logger.error("Runtime error occurred :: " + str(run_time_error))
        raise
    except ConnectionError as connection_error:
        logger.error("Connection error occurred :: " + str(connection_error))
        raise

    b_ref_url = 'http://www.baseball-reference.com/leagues/MLB/' + str(year) + '-standard-pitching.shtml'
    soup = BeautifulSoup(urllib.request.urlopen(b_ref_url).read(), "html.parser")
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    strig = '<b>' + str(comments[15]) + '<b>'
    soup2 = BeautifulSoup(strig.encode("utf-8", "ignore"), "html.parser")

    for i in soup2.find_all("tr", {"class": "full_table non_qual"}):
        for conf in i.find_all("td"):
            t = add_space(conf.text)
            b_ref_data.append(t)

        remove = string.punctuation
        pattern = r"[{}]".format(remove)
        name_filtered = re.sub(pattern, "", b_ref_data[0])
        name_filtered = name_filtered.replace(u'\xa0', ' ')
        b_ref_mapping[name_filtered] = b_ref_data[1:]
        b_ref_data.clear()

    for k in fan_graph_mapping:
        if k in b_ref_mapping:
            temp_dict[k] = b_ref_mapping.get(k)

            if temp_dict:
                for q in fan_graph_mapping.get(k):
                    temp_dict[k].append(zero_out_empty_fields(q.rstrip(' %')))

    with open(consolidated_file, "a") as test_file:
        test_file.write(str(columns) + '\n')

        for k, v in temp_dict.items():
            test_file.write(str(k))
            for it in list(v):
                test_file.write(',' + it)
            test_file.write('\r')

    pitching_table.clear()
    fan_graph_mapping.clear()
    temp_dict.clear()
    b_ref_data.clear()
    b_ref_mapping.clear()

print(time.clock())
print('Done')
