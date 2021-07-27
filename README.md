# vcdb-parser
Python tool to parse and clean the VERIS Community Database JSON file into a pandas DataFrame, and match UN M49 region codes used to their region string names

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/does-not-contain-msg.svg)](https://forthebadge.com)

Check out my site at https://rainbowpigeon.netlify.app!

***Note: This is not meant to be a robust framework of any sort. It was just a small script to get familiar with some pandas functions.***

## Requirements

### Software

- Python 3
```cmd
pip install ijson
pip install pandas
```

### Files

- VCDB JSON file: https://github.com/vz-risk/VCDB/blob/master/data/joined/vcdb.json.zip
- UN M49 CSV file: https://unstats.un.org/unsd/methodology/m49/overview/

## About

The [VERIS Community Database](https://github.com/vz-risk/VCDB) is a neat compilation of security breaches and incidents. This Python tool takes that data and parses it into a pandas DataFrame structure that can be used for further processing and analysis.

In short, this script:
- Removes incidents that were *not* chosen randomly (see: https://github.com/vz-risk/VCDB#warning-on-sampling)
- Removes columns that consist mostly of NaNs
- Removes columns with hardly any useful data to extract
- Creates lookup dictionary of UN M49 region codes to region names using CSV provided by the United Nations Statistics Division
- Maps the UN M49 codes used in `victim.region` column to their region names in a new `victim.region_name` column

## Other information that might be of use

- The VCDB is also available in CSV format here: https://github.com/vz-risk/VCDB/blob/master/data/csv/vcdb.csv.zip
- The list of columns present in the VCDB can be found here: https://github.com/vz-risk/VCDB/blob/master/vcdb-keynames-real.txt
- The list of columns, values, and their meanings can be found here: https://github.com/vz-risk/VCDB/blob/master/vcdb-labels.json
- If you are legitimately looking for a VCDB parser, you should probably use this: https://github.com/RiskLens/verispy
