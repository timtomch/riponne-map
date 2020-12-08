import sys, getopt
from pymarc import marcxml, map_xml, record_to_xml, XMLWriter, Record, Field

valid_targets = ["musi", "musg", "laf", "vddoc", "BCUmu", "BCUpt", "BCUcg"]
inputfile = ''
outputfile = ''
target = ''
mapping = True

def record_map(record):
    if record['172']['2'] in target:
        writer.write(record)
        #print(record)
      
    


def main(argv):
    usage = f"Usage: riponne-main.py -m <map target code> -i <inputfile> -o <outputfile>\nMap target code is one of {valid_targets}"
    global inputfile, outputfile, target, mapping
    try:
        opts, args = getopt.getopt(argv,"hm:i:o:",["ifile=","ofile=", "map="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-m", "--map"):
            if arg in valid_targets:
                target = arg
            else:
                print(f"Invalid mapping option. Must be one of {valid_targets}")
                sys.exit(2)
                
    if target in ('musi', 'musg'):
        mapping = False
    elif target == 'vddoc':
        target = ['vddoc','vddoc-la']
        
    
    
    if mapping:
        print(f"Processing {inputfile} with mapping {target}")
    else:
        print(f"Processing {inputfile} without mapping")
    
    
    global writer
    writer = XMLWriter(open(outputfile,'wb'))
    map_xml(record_map,inputfile)
    writer.close()    
    print(f'Saved as {outputfile}')

if __name__ == "__main__":
   main(sys.argv[1:])