# Documentation for bssid.py

## Prerequisites 

* Linux machine (not tested on windows) with POSIX compliant shell
* Python 3 with pip
	* `pip install Aeromiko`
* (opt) `grep` to obtain list of IPs from Aerohive
* (opt) `awk` to filter said list for duplicates
* list of all IPs (see below if you need help)
* SSH username and pw

## Setting up

Open `bssid.py` and change the `username` and `password` variables to match your AP SSH credentials, then:

```sh
pip install Aeromiko
```

## Running

Once you've obtained a list of APs to connect to (be sure to name this file `ip_list.txt`, separating every ip by a newline), run the script.

```sh
python3 bssid.py
```

The script will periodically log to the terminal and the resulting csv file can be found in the current directory under `bssid%H%M%S.csv`.

## (Optional) Obtaining IPs from Aerohive Classic Hivemanager & ExtremeCloud IQ

(because exporting doesn't include the management IPs `Mgt0 Interface`)

1. Make a filtered view: exclude all columns except `Mgt0 Interface`.
2. Right click devices page and save page as html. Name it something like `page.html`
3. search the `page.html` file for all the IPv4 addresses:

```sh
cat page.html \
	| grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" \
	| grep -E "^172.18|^10.32" \
	>> ip_list_with_duplicates.txt
```

```
First line: grab contents of page.html
2nd line: match (through extended regex meaning multiple matches per line are possible) all occurrences of ip addresses (and match only those ip addresses through -o, as opposed to the full line)
3rd line: match from those ip addresses only those starting with 172.18 or 10.32 (valid ranges for management IPs of APs in our network)
4th line: append the resulting IPS onto a file called ip_list.txt -- if it does not exist, it creates the file
```

After collecting all the IPs, the resulting file will contain duplicates. Filter these out using awk (https://stackoverflow.com/a/1444448)

```sh
awk '!seen[$0]++' ip_list_with_duplicates.txt > ip_list.txt
```
