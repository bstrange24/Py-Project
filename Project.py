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
logging.basicConfig(level='INFO', format=fmt, filename=r'C:\Users\hduser\Desktop\project\logs\Project.log',datefmt='%m-%d-%Y %I:%M:%S %p')
logger = logging.getLogger('Project')
logger.info("*** Starting Project ***")
logger.info(time.clock())

# Initialize list and maps
pitching_table = []
fan_graph_mapping = {}
temp_dict = {}
baseball_ref_data = []
baseball_ref_mapping = {}

# Header information for consolidated file
baseball_reference_header = 'Name,Age,Tm,Lg,W,L,WL_Perct,ERA,G,GS,GF,CG,SHO,SV,IP,H,R,ER,HR,BB,IBB,SO,HBP,BK,WP,BF,ERA_Plus,FIP,WHIP,H9,HR9,BB9,SO9,SO_W,'
fan_graph_header = 'FB_Perct,FB_Vel,SL_Perct,SL_Vel,CT_Perct,CT_Vel,CB_Perct,CB_Vel,CH_Perct,CH_Vel,SF_Perct,SF_Vel,KN_Perct,KN_Vel,XX_Perct'
fan_graph_column_list = ['FB_Perct', 'FB_Vel', 'SL_Perct', 'SL_Vel', 'CT_Perct', 'CT_Vel', 'CB_Perct', 'CB_Vel','CH_Perct', 'CH_Vel', 'SF_Perct', 'SF_Vel', 'KN_Perct', 'KN_Vel', 'XX_Perct']

# Years and pages for the fan graph and baseball reference website
pages = list(range(1, 11))
years = list(range(2007, 2018))

# Make any empty fields zero '0'
def zero_out_empty_fields(player_stat):
    if player_stat.isspace():
        player_stat = '0'
        return player_stat
    else:
        return player_stat

# Make \xa0 characters a space
def replace_unicode_chars(player_stat):
    filtered = player_stat.replace(u'\xa0', ' ')
    return filtered

# Clear maps and list used during each year
def clear_data_structure():
    pitching_table.clear()
    fan_graph_mapping.clear()
    temp_dict.clear()
    baseball_ref_data.clear()
    baseball_ref_mapping.clear()

# Loop over all the years from 2007 to 2017
for year in years:
    for field in fan_graph_column_list:
        columns = baseball_reference_header + field

        # Set fan graph url to the year that is getting processed
        base_fan_graph_url = 'http://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=30&type=4&season=' + str(year) + '&month=0&season1=' + str(year) + '&ind=0&team=0&rost=0&age=17,58&filter=&players=0&page='

        # Set baseball reference url to the year that is getting processed
        baseball_ref_url = 'http://www.baseball-reference.com/leagues/MLB/' + str(year) + '-standard-pitching.shtml'

        logger.info("Baseball Reference URL :: " + str(baseball_ref_url))
        logger.info("Year processing :: " + str(year))
        logger.info("Field processing :: " + field)

        # Consolidated file with fan graph and baseball reference data
        consolidated_file = r'C:\Users\hduser\Desktop\project\consolidated\\' + str(year) + '\\' + str(year) + '_' + field + '_consolidated.csv'
        logger.info("Consolidated file name :: " + consolidated_file)

        try:
            for page in pages:
                fan_graph_url = base_fan_graph_url + str(page) + "_50"
                logger.info("Fan Graph URL :: " + str(fan_graph_url))

                # Open url with BeautifulSoup
                soup = BeautifulSoup(urllib.request.urlopen(fan_graph_url).read(), "html.parser")

                for players in soup.findAll("tr", {"class": "rgRow"})[0:]:
                    for stats in players.findAll("td", {"class": "grid_line_regular"}):
                        if stats.find("a") is not None:
                            pitching_table.append(stats.find("a").contents[0])
                        else:
                            pitching_table.append(stats.contents[0])

                    pitcher_name = pitching_table[1].replace('\'', ' ')
                    pitcher_name = str(pitcher_name.replace('.', ' '))
                    fan_graph_mapping[pitcher_name] = pitching_table[fan_graph_column_list.index(field) + 3:fan_graph_column_list.index(field) + 4]

                    pitching_table.clear()

                for players in soup.findAll("tr", {"class": "rgAltRow"})[0:]:
                    for stats in players.findAll("td", {"class": "grid_line_regular"}):
                        if stats.find("a") is not None:
                            pitching_table.append(stats.find("a").contents[0])
                        else:
                            pitching_table.append(stats.contents[0])

                    pitcher_name = pitching_table[1].replace('\'', ' ')
                    pitcher_name = str(pitcher_name.replace('.', ''))
                    fan_graph_mapping[pitcher_name] = pitching_table[fan_graph_column_list.index(field) + 3:fan_graph_column_list.index(field) + 4]

                    pitching_table.clear()

                # Clear url. This is done to go to the next web page
                fan_graph_url = ''
        except ConnectionError as connection_error:
            logger.error("Connection error occurred during fan graph processing :: " + str(connection_error))
            raise
        except IndexError as index_error:
            logger.error("Indexing error occurred during fan graph processing :: " + str(index_error))
            raise
        except KeyError as key_error:
            logger.error("KeyError error occurred during fan graph processing :: " + str(key_error))
            raise

        try:
            # Open baseball reference url with BeautifulSoup
            soup = BeautifulSoup(urllib.request.urlopen(baseball_ref_url).read(), "html.parser")
            # Extract comments
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            elements = '<b>' + str(comments[15]) + '<b>'
            # Parse baseball reference data
            baseball_ref_soup = BeautifulSoup(elements.encode("utf-8", "ignore"), "html.parser")

            # Loop over parsed baseball reference data and get the players names and append them to the baseball reference list
            for element in baseball_ref_soup.find_all("tr", {"class": "full_table non_qual"}):
                for name in element.find_all("td"):
                    player_name = replace_unicode_chars(name.text)
                    baseball_ref_data.append(player_name)

                # Remove any special characters that the baseball reference website uses
                remove = string.punctuation
                pattern = r"[{}]".format(remove)
                name_filtered = re.sub(pattern, "", baseball_ref_data[0])
                name_filtered = name_filtered.replace(u'\xa0', ' ')
                # Add baseball reference data to the baseball reference map
                baseball_ref_mapping[name_filtered] = baseball_ref_data[1:]
                # Clear map for the next iteration
                baseball_ref_data.clear()

            # Loop over values in the fan graph map
            for key in fan_graph_mapping:
                # If the fan graph map key (players name) is in the baseball reference map,
                # add the baseball reference map value to the temporary dictionary
                if key in baseball_ref_mapping:
                    temp_dict[key] = baseball_ref_mapping.get(key)

                    # Loop over the fan graph map and append the data to the temporary dictionary.
                    # The temporary dictionary will have the data from both websites keyed on the players name
                    if temp_dict:
                        for keys in fan_graph_mapping.get(key):
                            temp_dict[key].append(zero_out_empty_fields(keys.rstrip(' %')))
        except ConnectionError as connection_error:
            logger.error("Connection error occurred during baseball ref processing :: " + str(connection_error))
            raise
        except IndexError as index_error:
            logger.error("Indexing error occurred during baseball ref processing :: " + str(index_error))
            raise
        except KeyError as key_error:
            logger.error("KeyError error occurred during baseball ref processing :: " + str(key_error))
            raise

        try:
            # Open consolidated output file for writing
            with open(consolidated_file, "a") as output_file:
                # Write column fields to output file
                output_file.write(columns + '\n')
                # Loop over temporary dictionary
                for key, value in temp_dict.items():
                    # Write keys to output file
                    output_file.write(str(key))
                    # Loop over values in the temporary dictionary and write to the output file
                    for values in list(value):
                        output_file.write(',' + values)
                    # Write carriage return after each record
                    output_file.write('\r')
        except IOError as io_error:
            logger.error("IO error occurred when writing consolidated file :: " + str(io_error))
            raise
        except KeyError as key_error:
            logger.error("KeyError error occurred when writing consolidated file:: " + str(key_error))
            raise

        # Clear list and dictionaries for the next year
        clear_data_structure()

print(time.clock())
print('Done')
