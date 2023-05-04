"""module bely method
    Realizes the method by Andrei Bely from the book "Rythm as Dialectic in The Bronze Horseman"
    
"""
import operator as oper
import decimal as dec
import pandas as pd
import re
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows

def __get_form_type__(read_line: str) -> int:
    """Helper function
        Take a string in format:
        [num] : Form %some_num% (some symbols): some text    
        and return value of some_num

    Args:
        read_line (str): String to process in format: 
        [num] : Form some_num (some symbols): some text
        
        for example:
        [500] : Form 2 (\--\-\-\-): lorem ipsum dolor sit amet

    Returns:
        int: some_num from input string
    """
    regex_form = r'Form (\d+)'
    regex_calc = r'Form 0 [(]calculation[)]'
    match = re.search(regex_form, read_line)
    if match:
        if re.search(regex_calc, read_line):
            return -1
        else:
            return int(match.group(1))
    else:
        return 0
    # if 'Form' in read_line:
    #     read_line = read_line.split()
    #     return int(read_line[3])
    # else:
    #     return 0

def compute_contrasts(f_in: str, f_out: str) -> str:
    """Takes the text from f_in, does Andrei Bely's method and puts it in f_out

    Args:
        f_in (str): name of input file with text to process
        f_out (str): name of output file with processeded text

    Returns:
        str: 'Done' if algorithm ended up with a success
    """
    
    with open(f_in, 'r', encoding='utf-8') as f_input, \
        open(f_out, 'w', encoding='utf-8') as f_output:            
            
        # Text can contain non-poetry text which is don't needed to be processed
        # so we skip it and memorize the number of skipped forms
        skipped_form0: int = 0
        
        # The first meaningful poetry line in the text starts with the biggest contrast
        contrast : int = 1
        
        # so after we find a new non-poetry text with form 0 we must skip it
        flag_skip: bool = False
        
        current_form_type: int
        avg_of_part = dec.Decimal(contrast)

        # skipping form's 0
        for line in f_input:            
            current_form_type = __get_form_type__(line)
            if current_form_type != 0:
                print("{} \tContrast's value: {:.3f}".format(line.strip(), contrast), file=f_output)
                break
            print(line.strip(), file=f_output)

        list_forms = list([-1] * 17)
        list_forms[current_form_type] = 0
        list_forms[0] = 1

        # main algorithm
        for i, line in enumerate(f_input, 1):

            line = line.strip()
            current_form_type = __get_form_type__(line)
            
            if flag_skip and current_form_type == 0:
                print(line, file=f_output)
                skipped_form0 += 1
                continue
            else:
                list_forms[1:] = list(map(lambda x: x + skipped_form0 if x != -1 else x, list_forms))[1:]
                skipped_form0 = 0
                flag_skip = False

            n = i - list_forms[current_form_type]

            if current_form_type > 0:

                list_forms[0] += 1
                
                if list_forms[current_form_type] == -1:
                    list_forms[current_form_type] = i
                    contrast = 1
                else:
                    list_forms[int(current_form_type)] = i
                    if n == 1:
                        contrast = dec.Decimal("0.2")
                    elif n < 10:
                        contrast = dec.Decimal(oper.truediv(oper.sub(n, 1), n))
                    else:
                        contrast = 1

                avg_of_part += dec.Decimal(contrast)
                print("{} \tContrast's value: {:.3f}".format(line.strip(), contrast), file=f_output)

            else:
                skipped_form0 += 1
                if current_form_type == -1:
                    avg_of_part = (avg_of_part * 4) / dec.Decimal(n)
                    print(line, "Average contrast: {:.3f}, lines in fragment: {}".format(avg_of_part, list_forms[0]), file=f_output)
                    avg_of_part = 0
                    list_forms[0] = 0
                else:
                    print(line, file=f_output)
                flag_skip = True
                
    return "Done"


def avgs_to_excel(f_in: str, exc_out: str) -> None:
    regex = r"contrast.*(\d+\.\d+).*"
    data = []
    with open(f_in, 'r', encoding='utf-8') as fin:
        for line in fin:
            if 'Average contrast:' in line:
                match = re.search(regex, line)
                data.append(float(match.group(1)))
    df = pd.DataFrame({'Averages': data})#, 'Total_Average': [round(statistics.mean(data), 4)] + ['' for _ in range(len(data)-1)]}) #columns=range(1, len(data)+1))
    df.to_excel(exc_out)
    del df
    

def made_plot_excel(f_in: str, exc_out: str) -> None:
    regex = r"contrast.*(\d+\.\d+).*"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "bely's method"

    # create line chart
    line_chart = LineChart()
    line_chart.title = "Eugenu Onegin"
    line_chart.legend = None
    line_chart.y_axis.title = "Averages"
    line_chart.x_axis.title = "Chapters"

    worksheet.column_dimensions['A'].width = 20
    worksheet.column_dimensions['B'].width = 20

    data = []
    with open(f_in, 'r', encoding='utf-8') as fin:
        data = [re.search(regex, line).group(1) for line in fin if 'Average contrast:' in line] 

    df = pd.DataFrame({'Chapters': list(range(1, len(data)+1)), 'Averages': data})


    for i in dataframe_to_rows(df, index=False, header=True):
        worksheet.append(i)

    # reference data that will be used for chart by column and row numbers
    values = Reference(worksheet, min_col=2, min_row=2, max_col=2, max_row=len(data)+1)

    # add data values for line chart
    line_chart.add_data(values)

    # reference dates that will be used for chart by column and row numbers
    data = Reference(worksheet, min_col=1, min_row=2, max_col=1, max_row=len(data)+1)

    # set the categories / x-axis values
    line_chart.set_categories(data)

    # add chart to worksheet
    worksheet.add_chart(line_chart, anchor='D15')

    # save workbook
    workbook.save(exc_out)
    
    del df

