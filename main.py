import json
import pandas as pd
import re
import argparse
import requests
#import pip3

def clean_RS_data(data):

    """
    This function takes the a json with the format
    of a property-list-simplified and return
    an array with just the identified properties:

    data: json with the data
    """
    #data = data['properties']['propertyList']
    data = data['propertyList']
    #pd.DataFrame.from_dict(data).to_excel('result/data.xls')
    data_clean = [pty for pty in data if not (pty['apn'] is None)]
    data_clean = pd.DataFrame.from_dict(data_clean)
    data_clean.drop_duplicates(subset=["apn"], keep=False, inplace=True)
    return data_clean
    

def clean_spreadsheet_data(data):
    """
    This function takes the an excel and return
    an array with just the identified properties:

    data: excel with the data
    """
    data.dropna(subset=["raw_apn"], inplace=True)
    data = data.drop(data[(data['checked?'].isna()) & (data['cf_score'] <= 3.0)].index)
    data['raw_apn'] = data['raw_apn'].apply(lambda x: str(x).replace('-', ''))
    data['raw_apn'] = data['raw_apn'].apply(lambda x: re.sub(r"\s+", "", x))
    data.sort_values("raw_apn", inplace=True)
    data.drop_duplicates(subset=["raw_apn"], inplace=True)

    return data


def get_json_data(path_json_data):
    """
    get the json object in the variable path_json_data.
    pathJsonObjectFile: path to the file that has the json object.
    ex. 'data/stats.json'
    """
    json_file = open(r'{}'.format(path_json_data), encoding="utf8")
    return json.load(json_file)


def get_excel_data(path_excel_data):
    """
    get the excel data in the variable path_excel_data.
    path_excel_data: path to the file that has the json object.
    ex. 'data/stats.xlsx'
    """
    excel_file = pd.ExcelFile(path_excel_data)
    excel_data = pd.read_excel(excel_file, 'Main', header=1)

    return excel_data


def write_JSON_File(fileName, data):
    """
    Write JSON file in newData folder
    """
    DataFile = open("{}".format(fileName), "w")
    DataFile.write(json.dumps(data, indent=4, sort_keys=False))
    DataFile.close()


def get_command_line_args():

    """
    This function makes a command-line interface and
    defines what arguments the program requires, it
    return the arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--rentalscape",
        help='path to the JSON file with the rentalscape data.'
    )
    parser.add_argument(
        "-s",
        "--spreadsheet",
        help='path to the spreadsheet with the Colombia data.'
    )

    args = parser.parse_args()

    return args


def check_pending(rs_data):
    """
    This function takes the data on RS a return the
    pending addresses
    """
    data_clean = rs_data[rs_data['address'].isnull()]
    return data_clean


def check_coverImage(rs_data):
    """
    This function takes the data on RS a return the
    peoperties with no cover pic
    """
    data_clean = rs_data[rs_data['coverImageUrl'].isnull()]
    return data_clean

def vrbo_live_validator(url):
    """
    This fuction validates if a vrbo listing is live
    """
    responses = requests.get(url)
    if len(responses.history) > 0:
        return 'yes'
    return 'NO'

def homeaway_live_validator(url):
    """
    This fuction validates if a homaway listing is live
    """
    responses = requests.get(url)
    if len(responses.history) > 1:
        return 'yes'
    return 'NO'

def active_check(spr_data):
    for i, listing in spr_data.iterrows():
        listing['active_code'] = ''
        if listing['url'].find('vrbo') > -1:
            listing['active_code'] = vrbo_live_validator(listing['url'])
        elif listing['url'].find('homeaway') > -1:
            listing['active_code'] = homeaway_live_validator(listing['url'])
    return spr_data


def check_confidence_score(rs_data, spr_data):

    """
    Properties with a confidence score at or below 3
    should not be displayed on RS until it has been
    verified through the QA.

    This function check that all the properties on with
    confidence score at or below aren't displayed.

    rs_data: data on RS.
    spr_data: excel with the colombian data.
    """

    rs_data.merge(spr_data,
                  how='left',
                  left_on="apn",
                  right_on="raw_apn",
                  left_index=True)


if __name__ == "__main__":

    """Getting Path to the files"""
    args = get_command_line_args()
    path_RS_Data = args.rentalscape
    path_SPR_Data = args.spreadsheet

    """Getting spreadsheet data"""
    spreadsheet_data = get_excel_data(path_SPR_Data)

    """Check active listings"""
    #spreadsheet_data = active_check(spreadsheet_data)
    #spreadsheet_data.to_csv('result/active_listings.csv')

    """Clean spreadsheet data"""
    spreadsheet_data = clean_spreadsheet_data(spreadsheet_data)

    """Getting RS data and cleaning it"""
    RS_data = get_json_data(path_RS_Data)
    RS_data = clean_RS_data(RS_data)

    """Check pending addresses in RS"""
    RS_pending = check_pending(RS_data)
    RS_pending.to_csv('result/RS_pending_address.csv')

    """Check cover image in RS"""
    RS_pending = check_coverImage(RS_data)
    RS_pending.to_csv('result/RS_no_image.csv')

    """Comparing Speadsheet vs RS """
    filter_Spreadsheet = ~spreadsheet_data['raw_apn'].isin(RS_data['apn'])
    in_Spreadsheet_not_RS = spreadsheet_data[filter_Spreadsheet]

    """Comparing RS vs Speadsheet"""
    filter_RS = ~RS_data['apn'].isin(spreadsheet_data['raw_apn'])
    in_RS_not_Spreadsheet = RS_data[filter_RS]

    """Getting CSVs"""
    in_RS_not_Spreadsheet.to_csv('result/in_RS_not_Spreadsheet.csv')
    in_Spreadsheet_not_RS.to_csv('result/in_Spreadsheet_not_RS.csv')

