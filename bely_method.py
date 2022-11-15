"""module bely method
    Realizes the method by Andrei Bely from the book "Rythm as Dialectic in The Bronze Horseman"
    
"""
import operator as o
import decimal as d
import pandas as pd
import statistics


def __get_form_type__(read_line: str) -> int:
    """Helper function
        Take a string in format:
        [num] : Form some_num (some symbols): some text    
        and return value of some_num

    Args:
        read_line (str): String to process in format: 
        [num] : Form some_num (some symbols): some text
        
        for example:
        [500] : Form 2 (\--\-\-\-): lorem ipsum dolor sit amet

    Returns:
        int: some_num from input string
    """
    if 'Form' in read_line:
        read_line = read_line.split()
        return int(read_line[3])
    else:
        return 0

def compute_contrasts(f_in: str, f_out: str) -> str:
    """Takes the text from f_in, do Andrei Bely's method and put it in f_out

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
        avg_of_part = d.Decimal(contrast)              


        # skipping form's 0
        for line in f_input:            
            current_form_type = __get_form_type__(line)
            if current_form_type != 0:
                print("{} \tContarst's value: {:.3f}".format(line.strip(), contrast), file=f_output)
                break
            print(line.strip(), file=f_output)
            skipped_form0 += 1
        list_forms = list([skipped_form0] * 17)
        

        for i, line in enumerate(f_input, skipped_form0 + 1):

            line = line.strip()
            current_form_type = __get_form_type__(line)
            if flag_skip and current_form_type == 0:
                list_forms[0] += 1
                print(line, file=f_output)
                continue
            else:
                flag_skip = False

            n = i - list_forms[current_form_type]

            if current_form_type != 0:

                if list_forms[current_form_type] == skipped_form0:
                    list_forms[current_form_type] = i
                    contrast = 1
                else:
                    list_forms[int(current_form_type)] = i
                    if i == 1:
                        contrast = 1
                    elif n == 1:
                        contrast = d.Decimal("0.2")
                    elif n < 10:
                        contrast = d.Decimal(o.truediv(o.sub(n, 1), n))
                    else:
                        contrast = 1

                avg_of_part += d.Decimal(contrast)
                print("{} \tContrast's value: {:.3f}".format(line.strip(), contrast), file=f_output)

            else:
                avg_of_part = (avg_of_part * 4) / d.Decimal(n)
                print("Average contrast: {:.3f}, lines in fragment: {}".format(avg_of_part, n), file=f_output)
                print(line, file=f_output)                
                avg_of_part = 0
                list_forms[0] = i + 1
                flag_skip = True
                
    return "Done"


def avgs_to_excel(f_in: str, exc_out: str) -> None:
    # Average contrast: 2.048, lines in fragment: 20
    data = []
    with open(f_in, 'r', encoding='utf-8') as fin:
        for line in fin:
            if 'Average contrast:' in line:
                number = float(line.split()[2].strip(','))
                data.append(number)
    df = pd.DataFrame({'Averages': data, 'Total_Average': [round(statistics.mean(data), 4)] + ['' for _ in range(len(data)-1)]}) #columns=range(1, len(data)+1))
    df.to_excel(exc_out)
    del df
    
