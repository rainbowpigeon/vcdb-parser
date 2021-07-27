# vcdb-parser
Python tool to parse and clean the VERIS Community Database JSON file into a pandas DataFrame, and match UN M49 country codes used to their string names

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
