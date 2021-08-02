#Takes in a list of numbers between 0 and 1. Outputs comma separated string containing numbers. 
def probs_to_string(doubles):
    ret = []
    for d in doubles:
        ret.append(str(int(d*1000)))
    return ",".join(ret)

def string_to_probs(prob_string):
    ret = []
    for digits in prob_string.split(","):
        ret.append(float(digits)/1000)
    return ret