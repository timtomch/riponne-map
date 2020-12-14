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
    
    recordid = ''
    callnr = ''
    callorigin = ''
    
    firstsubject = True
    
    for field in record.get_fields():
        
        if field.tag == '001':
            recordid = field.value()
        
        # 008 field is mapped as is (if it exists)
        elif field.tag == '008':
            newrecord.add_field(field)
        
        # 019 field is mapped as is (if it exists)
        elif field.tag == '019':
            newrecord.add_field(field)
        
        # 035 fields are mapped as is (if they exist)
        elif field.tag == '035':
            newrecord.add_field(field)
            
        # 172__$2 is mapped to 084__$a
        elif field.tag == '172':
            vocab = field.get_subfields('2')[0]
            if vocab in ["BCUR1","BCUR2","BCUR3"]:
                mappedvalue = "CLASBCUR"
            elif vocab in ["vddoc","vddoc-la"]:
                mappedvalue = "vddoc"
            elif vocab == "laf":
                mappedvalue = "laf"
            else:
                print(f"WARNING 172__$2 for record {recordid} ({vocab}) is not in the list of mapped vocabularies.")
            
            newrecord.add_ordered_field(
                Field(
                    tag = '084',
                    indicators = [' ',' '],
                    subfields = ['a', mappedvalue]
                    )
                )
            
            # 172__$a will be mapped to 153__$a  
            callnr = field.get_subfields('a')[0]
        
        # The first 572 is mapped to 153__$j (concatenating subfields)
        elif field.tag == '572':
            if firstsubject == True:
                newclassif = ' -- '.join(field.get_subfields('a', 'c', 'd', 'e', 'h', 'l', 'm', 's', 't', 'v', 'x', 'X', 'y', 'z', '9', '['))
                newrecord.add_ordered_field(
                    Field(
                        tag = '153',
                        indicators = [' ',' '],
                        subfields = [
                            'a', callnr,
                            'j', newclassif]
                        )
                )
                firstsubject = False
            
            # All 572s are mapped to 753s
            # Keeping the oringial subfield structure
            subjectfield = field
            subjectfield.tag = '753'
            newrecord.add_ordered_field(subjectfield)   
        
        # 680 fields are mapped as is (if they exist)     
        elif field.tag == '680':
            newrecord.add_ordered_field(field)
        
        # Log all unmapped fields
        else:
            print(f"WARNING field not mapped for record {recordid}: {field}")
        
    # Add the existing 001 field (record id) as an additional 035
    newrecord.add_ordered_field(
        Field(
            tag = '035',
            indicators = [' ',' '],
            subfields = ['a', recordid]
            )
        )
      
    # 040__$a is set to static value "RNV vdbcul"
    newrecord.add_ordered_field(
            Field(
                tag = '040',
                indicators = [' ',' '],
                subfields = ['a', "RNV vdbcul"]
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