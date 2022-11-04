"""module bely method
    Realizes the method by Andrei Bely from the book "Rythm as Dialectic in The Bronze Horseman"
    
"""
import operator as o
import decimal as d


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
    read_line = read_line.split()
    return int(read_line[3])


def compute_contrasts(f_in: str, f_out: str) -> str:
    """Takes the text from f_in, do Andrei Bely method and put it in f_out

    Args:
        f_in (str): name of input file with text to process
        f_out (str): name of output file with processeded text

    Returns:
        str: 'Done' if algorithm ended up with a success
    """

    with open(f_in, 'r', encoding='utf-8') as f_input, \
        open(f_out, 'w', encoding='utf-8') as f_output:
        contrast = 1
        current_form_type = 0
        flag_skip = False
        total_avg = d.Decimal(0)
    
        
        skipped_form0 = 0
        for line in f_input:            
            current_form_type = __get_form_type__(line)
            if current_form_type != 0:
                print('{} \tзначение контрастности: {:.3f}'.format(line.strip(), contrast), file=f_output)
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

                total_avg += d.Decimal(contrast)
                print('{} \tзначение контрастности: {:.3f}'.format(line.strip(), contrast), file=f_output)

            else:
                total_avg = (total_avg * 4) / d.Decimal(n)
                print("Среднее значение контрастности: {:.3f}, строк в фрагменте: {}".format(total_avg, n), file=f_output)
                print(line, file=f_output)                
                total_avg = 0
                list_forms[0] = i + 1
                flag_skip = True
                
    return "Done"



# compute_contrasts("SashaTop.txt", "SashaSuperTop.txt")
