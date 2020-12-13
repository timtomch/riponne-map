import sys, getopt
from pymarc import marcxml, map_xml, record_to_xml, XMLWriter, Record, Field

valid_targets = ["musi", "musg", "laf", "vddoc", "BCUmu", "BCUpt", "BCUcg"]
inputfile = ''
outputfile = ''
target = ''
mapping = True

def record_map(record):
    try:
        if record['172']['2'] in target:
            if mapping == True:
                print("original record:")
                print(record)
                record = record_crosswalk(record)
                #record = dummy_record(record)
                print("replaced record:")
                print(record)
            writer.write(record)
    except TypeError:
        print("Record {} does not have a 072__$2 field".format(record['001']))
        
        #print(record)

def dummy_record(record):
    # To try stuff out. Remove when done debugging.
    newrecord = Record()
    try:
        newrecord.add_field(record['008'])
    except: 
        pass
    try:
        for field in record.get_fields('035'):
                newrecord.add_field(field)
    except: 
        pass
    
    return newrecord

      
def record_crosswalk(record):
    # This function maps a record to the format required. The original record is passed as argument and it returns the new record. 
    print("record_crosswalk called")
    newrecord = Record()
    
    # 008 field is mapped as is
    try:
        for field in record.get_fields('008'):
                newrecord.add_field(field)
    except: 
        pass
        
    # 019 field is mapped as is
    try:
        for field in record.get_fields('019'):
                newrecord.add_field(field)
    except: 
        pass
        
    # 035 field is mapped as is
    try:
        for field in record.get_fields('035'):
                newrecord.add_field(field)
    except: 
        pass
    
      
    # 040__$a is set to static value "RNV vdbcul"
    newrecord.add_field(
            Field(
                tag = '040',
                indicators = ['',''],
                subfields = ['a', "RNV vdbcul"]
                )
            )
    
    # 172__$a is mapped to 153__$a        
    try:
        newrecord.add_field(
            Field(
                tag = '153',
                indicators = ['',''],
                subfields = ['a', record['172']['a']]
                )
            )
    except: 
        pass
        
    # 172__$2 is mapped to 084__$a
    if record['172']['2'] in ["BCUR1","BCUR2","BCUR3"]:
        mappedvalue = "CLASBCUR"
    elif record['172']['2'] in ["vddoc","vddoc-la"]:
        mappedvalue = "vddoc"
    elif record['172']['2'] == "laf":
        mappedvalue = "laf"
    newrecord.add_field(
            Field(
                tag = '084',
                indicators = ['',''],
                subfields = ['a', mappedvalue]
                )
            )
    
    return newrecord    


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