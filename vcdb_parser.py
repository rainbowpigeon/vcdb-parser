import ijson
import pandas as pd
from pandas import json_normalize
from helper import *


# https://github.com/vz-risk/VCDB/blob/master/data/joined/vcdb.json.zip
VCDB_FILENAME = "vcdb_formatted.json"
# https://unstats.un.org/unsd/methodology/m49/overview/
UNSD_FILENAME = "unsd_country_codes.csv"


def type_filter(database, incident_type):
    """
    Filters database based on incident type and returns the filtered database
    :param database: pandas DataFrame
    :param incident_type: String that is one of these: ("malware", "error", "hacking", "misuse", "social")
    :return: pandas DataFrame with columns filtered based on incident_type input
    """
    incident_types = ("malware", "error", "hacking", "misuse", "social")
    subtypes = ["variety", "vector", "result"]
    if incident_type not in incident_types:
        raise Exception("Allowed incident types: {}".format(", ".join(incident_types)))

    if incident_type == "social":
        subtypes.append("target")

    filters = ["action.{}.{}".format(incident_type, subtype) for subtype in subtypes]
    filters.insert(0, "incident_id")

    filtered_df = database.filter(items=filters)
    return filtered_df.dropna()


def additional_filter(database, column_inputs):
    """
    Filters database based on columns
    :param database: pandas DataFrame
    :param column_inputs: String specifying columns concatenated with ','
    :return: pandas DataFrame with columns filtered
    """
    column_list = column_inputs.split(",")
    if "incident_id" not in column_list:
        column_list.insert(0, "incident_id")
    filtered_df = database.filter(items=column_list)
    return filtered_df.dropna()


def merging_filter(database, additional_database):
    """
    Merges two databases using data from both databases in the final merged database
    :param database: pandas DataFrame
    :param additional_database: another pandas DataFrame
    :return: pandas DataFrame with data merged from both inputs
    """
    pd.set_option('display.max_columns', None)
    # display.max_rows as well?
    final_filter = database.merge(additional_database, on='incident_id', how='inner')
    return final_filter


def parse_vcdb_json_into_df(filename):
    """
    Parses and filters VCDB json file into Pandas DataFrame, returning that DataFrame
    :param filename: String specifying filename of VCDB json file
    :return: pandas DataFrame
    """
    with open(filename, "r") as datafile:
        incidents = ijson.items(datafile, 'item')
        # filter incidents that were NOT chosen randomly as mentioned at
        # https://github.com/vz-risk/VCDB#warning-on-sampling
        # removes around 1500 incidents to around 6400
        incidents = [i for i in incidents if not i.get('plus').get('sub_source')]
    df = json_normalize(incidents)
    return df


def clean_df(df):
    """
    Drops columns with mostly NaNs and hardly any useful data to use/extract from the DataFrame
    :param df: pandas DataFrame
    :return: pandas DataFrame with useless columns dropped
    """

    null_percentage_threshold = 90.0
    row_count = float(get_row_count(df))
    allowed_cols = ("action", "actor", "discovery_method")
    cols_to_remove = ["source_id", "schema_version"]

    for col in df.columns:
        # Part 1: Clean some plus columns
        if col.startswith("plus") and "timeline" not in col:
            cols_to_remove.append(col)
            # Dropped columns:
            # plus.analysis_status
            # plus.analyst
            # plus.asset.total
            # plus.attribute.confidentiality.credit_monitoring
            # plus.attribute.confidentiality.data_abuse
            # plus.created
            # plus.dbir_year
            # plus.github
            # plus.master_id
            # plus.modified
        # Part 2: Clean columns with lots of NaN values
        # if the NaNs are not because of json flattening (where the column names would have nested attributes)
        elif '.' not in col or (not col.startswith(allowed_cols)):
            null_percentage = 100 * float(get_column_nulls_count(df, col)) / row_count
            if null_percentage > null_percentage_threshold:
                cols_to_remove.append(col)

    df.drop(columns=cols_to_remove, inplace=True)
    return df


def query_df_for_value(df, column, query):
    """
    Recommended to be used with columns without any nulls at all:
      timeline.incident.year
      security_incident: ("Confirmed", "Suspected", "Near miss", "False positive")
      victim.country: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
    Usage:
      df_result = query_df_for_value(df, "victim.country", "US")
      print(df_result)
    :param df: pandas DataFrame
    :param column: Column in a pandas DataFrame
    :param query: String representing column value
    :return: pandas DataFrame with rows containing the queried value. Empty string if no such rows.
    """
    if col_contains_lists(df, column):
        query_mask = df[column].apply(lambda x: query in x)
    else:
        query_mask = df[column].values == query

    if not df[query_mask].empty:
        return df[query_mask]
    else:
        return ""


def parse_unsd_csv_into_df(filename):
    """
    :param filename: String specifying CSV filename containing m49 country codes from UNSD
    :return: pandas DataFrame with 2 columns: Joined_Region_Code, Joined_Region_Name
    """
    df = pd.read_csv(filename, dtype=str)

    m4i_cols = ("Region Code", "Region Name", "Sub-region Code", "Sub-region Name",
                "Intermediate Region Code", "Intermediate Region Name")

    m4i_df = df.filter(items=m4i_cols).drop_duplicates()
    m4i_df.dropna(subset=['Region Code'], inplace=True)
    # drops Antarctica but that is fine

    super_region_df = m4i_df.filter(items=("Region Code", "Region Name")).drop_duplicates()
    m4i_df = pd.concat([super_region_df, m4i_df])

    # Formatting
    code_cols = ["Region Code", "Sub-region Code", "Intermediate Region Code"]
    m4i_df[code_cols] = m4i_df[code_cols].apply(lambda x: x.str.zfill(3))
    m4i_df["Sub-region Code"] = m4i_df["Sub-region Code"].fillna("000")

    m4i_df["Joined_Region_Code"] = m4i_df["Region Code"] + m4i_df["Sub-region Code"]
    # using str.cat for fun
    m4i_df["Joined_Region_Name"] = m4i_df["Region Name"].str.cat(m4i_df["Sub-region Name"], sep=" - ")

    # For regions without sub-regions, just use region name as final region name
    mask = m4i_df["Sub-region Name"].isnull()
    m4i_df.loc[mask, 'Joined_Region_Name'] = m4i_df.loc[mask, 'Region Name']

    # For sub-regions with intermediate regions, use intermediate codes and names in final codes and names instead
    mask = m4i_df["Intermediate Region Name"].notnull()
    m4i_df.loc[mask, 'Joined_Region_Name'] = m4i_df.loc[mask, 'Region Name'] + " - " + m4i_df.loc[
        mask, 'Intermediate Region Name']
    m4i_df.loc[mask, 'Joined_Region_Code'] = m4i_df.loc[mask, 'Region Code'] + m4i_df.loc[
        mask, 'Intermediate Region Code']

    m4i_df = m4i_df.filter(items=("Joined_Region_Code", "Joined_Region_Name"))

    return m4i_df


def main():
    df = parse_vcdb_json_into_df(VCDB_FILENAME)
    df = clean_df(df)

    # print(query_df_for_value(df, "security_incident", "Suspected"))

    m4i_df = parse_unsd_csv_into_df(UNSD_FILENAME)
    mapping = dict(m4i_df[["Joined_Region_Code", "Joined_Region_Name"]].values)
    df["victim.region_name"] = df["victim.region"].apply(lambda x: [mapping.get(v) for v in x])

    print(get_unique_col_values(df, "victim.region_name"))


if __name__ == "__main__":
    main()
