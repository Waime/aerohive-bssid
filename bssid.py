import aeromiko
import re
from datetime import datetime

now = datetime.now()

f = open('bssids' + now.strftime("%H%M%S") + '.csv', 'a') # open file in append mode, if it doesn't exist it creates the file with datetime in name

f.write('AP MOBILE;AP SAPPHIRE;BSSID;SSID\n')

username = "admin"
password = "REDACTED"

### aaaa:bbbbb:cccc => aa:aa:bb:bb:cc:cc
### This is necessary because the AP's return the bssids in groups of 4 characters
def fix_bssid_format(ugly_bssid):
    nocolons = ugly_bssid.replace(':', '')
    return ':'.join(a+b for a,b in zip(nocolons[::2], nocolons[1::2]))

### returns a dictionary of key = column and value = starting string index of the value of that column
### the start and end of the columns are determined by the dashes underneath the column names
def build_idx_dict(colline, dashline):
    dashes = list(map(lambda x: len(x) + 1, dashline.strip().split(' '))) # maps the dashes line to a list of dash lengths
    dashes.insert(0, 0) # insert a 0 at the front of the list, necessary to determine the start of the first column
    col_start_idx = []
    s = 0
    for item in dashes: # iterate over the column lengths and replace by running total, this is to determine the start of each column
        s += item
        col_start_idx.append(s)
    
    # creates a list of column names based off the previous list (start of the columns)
    columns = []
    for i in range(len(col_start_idx) - 1):
        start = col_start_idx[i]

        if (i < len(col_start_idx)):
            end = col_start_idx[i+1]
        else:
            end = len(colline)

        columns.append(colline[start:end].strip())

    columns.append("@@END")
    
    return dict(zip(columns, col_start_idx)) 

### returns start and end indexes for a given column, computed from given column dictionary
def get_column_idxs(colname, coldict):
    start_idx = coldict[colname]
    
    # determine the starting index of the next column using Dictionary.keys() 
    keys = list(coldict.keys())
    next_column = keys.index(colname) + 1
    end_idx = coldict[keys[next_column]]
    
    return (start_idx, end_idx)

### connects to a given ip and fetches formatted output of the show interface command
### returns: a list of csv formatted relevant lines
def get_bssids(ip):
    access_point = aeromiko.AP(ip, username, password)
    access_point.connect()
    
    hn = access_point.get_hostname()
    showint = access_point.send_command("show interface").split('\n') # turns every line into an element in a list
    
    coldict = build_idx_dict(showint[3], showint[4]) # [3] = line that contains names of column, [4] = contains the dashes

    r = re.compile(r'^Wifi[0-9]\.[0-9]') # line start with Wifi#.#

    # get indexes of relevant columns
    bssid_idxs = get_column_idxs('MAC addr', coldict)
    ssid_idxs = get_column_idxs('SSID', coldict)
    name_idxs = get_column_idxs('Name', coldict)

    # convert output of 'show interface' command into output with only the values we want in valid csv format
    def format_csv_line(x):
        o =  hn # AP MOBILE
        o += ";"
        o += hn + "," + ("2.4" if x[name_idxs[0]:name_idxs[1]].strip()[4:5] == "0" else "5") + "," + x[ssid_idxs[0]:ssid_idxs[1]].strip().replace('...', '') # AP SAPPHIRE
        o += ";"
        o += fix_bssid_format(x[bssid_idxs[0]:bssid_idxs[1]].strip()) # BSSID
        o += ";"
        o += x[ssid_idxs[0]:ssid_idxs[1]].strip().replace('...', '') # SSID
        return o
    
    out = list(map(format_csv_line, list(filter(r.match, showint)))) # map all matching lines with r to output defined in format_csv_line
    return out


with open("ip_list.txt", "r") as ips: # specify the file with ips to be used 
    for ip_line in ips:
        ip = ip_line.strip() # remove trailing \n character from ip
        print("querying ip: " + ip)
        try:
            out = get_bssids(ip)
        except:
            print("ip: " + ip + " could not be connected to")
            # TODO: write failed IP to a file
            out = ""

        if out:
            f.write('\n'.join(out) + '\n')
            f.flush() # immediately writes to csv after obtaining output instead of waiting until the program ends




