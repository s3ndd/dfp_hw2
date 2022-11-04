"""
Homework 2 Team 13:

Name: Xiao Shi
Andrew ID: xiaoshi
Email: xiaoshi@andrew.cmu.edu

Name: Sheldon Shi
Andrew ID: lijuns
Email: lijuns@andrew.cmu.edu
"""
from enum import Enum
from typing import TextIO, List


class RecordType(Enum):
    """
    Define all record type enums
    """
    EXCHANGE_COMPLEX_HEADER = '0 '
    EXCHANGE_HEADER = '1 '
    FIRST_COMB_COMM = '2 '
    SECOND_COMB_COMM = '3 '
    THIRD_COMB_CORR = '4 '
    FIRST_PHYS_REC = '81'
    SECOND_PHYS_REC = '82'
    FIRST_PHYS_REC_FLOAT = '83'
    SECOND_PHYS_REC_FLOAT = '84'
    PRICE_SPECS = 'P '
    RISK_ARRAY_PARAMS = 'B '
    COMM_REDEF = 'R ',
    INTRA_COMM_TIERS = 'C '
    INTRA_COMM_SERIES = 'E '
    TIERED_SCANNED = 'S '
    COMB_COMM_GRPS = '5 '
    INTER_COMM_SPREADS = '6 '
    PHYS_DEBT_SEC = '9 '
    OPT_ON_COMB = 'X '
    DAILY_ADJ = 'V '
    SPLIT_ALLOC = 'Y '
    DELTA_SPLIT_ALLOC = 'Z '
    CURR_CONV_RATE = 'T '


def main():
    raw_file = 'cme.20210709.c.pa2'
    result_file = 'CL_expirations_and_settlements.txt'
    date_range = ['2021-09', '2023-12']
    filter_futures_code = 'CL'
    filter_options_code = 'LO'
    # read file and process the data line by line
    with open(raw_file, 'r') as reader, open(result_file, 'w') as writer:
        print('Start processing...')
        record = reader.readline()
        total_record = 0
        output_b, output_81 = [], []
        while record:
            try:
                # only process type B and type 81
                record_type = RecordType(record[:2])
                if record_type == RecordType.RISK_ARRAY_PARAMS:
                    parse_risk_array_params(output_b, record, filter_futures_code, filter_options_code, date_range[0],
                                            date_range[1])
                elif record_type == RecordType.FIRST_PHYS_REC:
                    parse_first_phys_rec(output_81, record, filter_futures_code, filter_options_code, date_range[0],
                                         date_range[1])
                total_record += 1
                record = reader.readline()
            except ValueError:
                print('Invalid record. Ignore.')
        # write the formatted record to the final output
        print_first_table_header(writer)
        print_formatted_records(writer, output_b)
        print_second_table_header(writer)
        print_formatted_records(writer, output_81)
        print(f'Process {total_record} records. {len(output_b)} type B records and {len(output_81)} type 81 records.')
        print('Done!')


def parse_risk_array_params(output: List[str], record: str, filter_futures_code: str, filter_options_code: str,
                            start: str,
                            end: str) -> None:
    """
    parses the type B record and returns a formatted string
    https://www.cmegroup.com/confluence/display/pubspan/Type+B+-+Expanded
    :param output: a list of formatted record
    :param record: a raw type B record
    :param filter_futures_code: to be parsed future code
    :param filter_options_code: to be parsed option code
    :param start: date range
    :param end: date range
    :return:
    """
    if len(record) < 165:
        # ignor invalid recode
        print('ignor invalid type B record:', record)
        return

    # fetching the related data
    commodity_code = record[5:15].strip()
    product_type_code = 'Opt' if record[15:18].upper() == 'OOF' else record[15:18].capitalize()
    futures_contract_month = convert_date(record[18:24].strip())
    option_contract_month = convert_date(record[27:33].strip())
    expiration_settlement_date = convert_date(record[91:99].strip())
    underlying_commodity_code = record[99:109].strip()

    # if the underlying commodity code is the filter_commodity_code, it will parse the recode
    futures_code = underlying_commodity_code
    contract_month = None
    if futures_code == filter_futures_code:
        contract_type = product_type_code
        formatted_record = None
        if contract_type == 'Fut':
            # future
            contract_month = futures_contract_month
            futures_exp_date = expiration_settlement_date
            formatted_record = f'{futures_code:<7}   {contract_month:<8}   {contract_type:<8}   {futures_exp_date:<8}\n'
        elif contract_type == 'Opt' and commodity_code == filter_options_code:
            # option
            contract_month = option_contract_month
            options_exp_date = expiration_settlement_date
            options_code = commodity_code
            formatted_record = f'{futures_code:<7}   {contract_month:<8}   {contract_type:<8}   {" ":<8}    {options_code:<7}   {options_exp_date}\n'
        if formatted_record is not None and contract_month is not None and (start <= contract_month <= end):
            output.append(formatted_record)


def parse_first_phys_rec(output: List[str], record: str, filter_futures_code: str, filter_options_code: str, start: str,
                         end: str) -> None:
    """
    parses the type 81 record and returns a formatted string
    https://www.cmegroup.com/confluence/display/pubspan/Type+8+-+Expanded
    :param output: a list of formatted record
    :param record: a raw type B record
    :param filter_futures_code: to be parsed future code
    :param filter_options_code: to be parsed option code
    :param start: date range
    :param end: date range
    """
    if len(record) < 123:
        # ignor invalid recode
        print('ignor invalid type 81 record:', record)
        return
    # fetch related data
    commodity_product_code = record[5:15].strip()
    underlying_commodity_product_code = record[15:25].strip()
    product_type_code = 'Opt' if record[25:28].upper() == 'OOF' else record[25:28].capitalize()
    option_right_code = record[28:29].upper()
    futures_contract_month = convert_date(record[29:35])
    option_contract_month = convert_date(record[38:44])
    option_strike_price = int(record[47:54]) / 100
    high_precision_settlement_price = int(record[108:122]) / 100

    # if the underlying commodity code is the filter_commodity_code, it will parse the recode
    futures_code = underlying_commodity_product_code
    contract_month = None
    if futures_code == filter_futures_code:
        contract_type = product_type_code
        formatted_record = None
        if contract_type == 'Fut':
            # future
            contract_month = futures_contract_month
            settlement_price = high_precision_settlement_price
            formatted_record = f'{futures_code:<7}   {contract_month:<8}   {contract_type:<8}   {" ":>6}   {settlement_price:>10.2f}\n'
        elif contract_type == 'Opt' and commodity_product_code == filter_options_code:
            # option
            contract_month = option_contract_month
            contract_type = 'Put' if option_right_code.upper() == 'P' else 'Call'
            strike_price = option_strike_price
            settlement_price = high_precision_settlement_price
            formatted_record = f'{futures_code:<7}   {contract_month:<8}   {contract_type:<8}   {strike_price:>6.2f}   {settlement_price:>10.2f}\n '

        if formatted_record is not None and contract_month is not None and (start <= contract_month <= end):
            output.append(formatted_record)


def print_first_table_header(output: TextIO) -> None:
    """
    writes the table header to the given file
    :param output: the file handler
    """
    output.writelines(['Futures   Contract   Contract   Futures     Options   Options\n',
                       'Code      Month      Type       Exp Date    Code      Exp Date\n',
                       '-------   --------   --------   --------    -------   --------\n'])


def print_second_table_header(output: TextIO) -> None:
    """
    writes the table header to the given file
    :param output: the file handler
    """
    output.writelines(['Futures   Contract   Contract   Strike   Settlement\n',
                       'Code      Month      Type       Price    Price\n',
                       '-------   --------   --------   ------   ----------\n'])


def print_formatted_records(output: TextIO, records: List[str]) -> None:
    """
    writes the formatted records to the given file
    :param records: formatted records
    :param output: the file handler
    """
    output.writelines(records)


def convert_date(date: str) -> str:
    """
    converts CCYYMMDD TO CCYY-MM-DD
    :param date: CCYYMMDD date
    :return: converted date
    """
    if len(date) == 8:
        return f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    elif len(date) == 6:
        return f'{date[:4]}-{date[4:6]}'
    else:
        return date


if __name__ == '__main__':
    main()
