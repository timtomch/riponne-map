import argparse, re, datetime
from pymarc import marcxml, map_xml, record_to_xml, XMLWriter, Record, Field

valid_targets = ["musi", "musg", "laf", "vddoc", "BCURmu", "BCURpt", "BCURcg"]
pt_regex = "^\(08\)"
mu_regex = "^\(086\.[08]\)78|^\(07\)78|^\(09\)|^78"
target = ''
inputfile = ''
mapping = True

def record_map(record):
    try:
        if record['172']['2'] == target:
            if mapping == True:
                record = record_crosswalk(record)
            writer.write(record)
        elif record['172']['2'] in ['BCUR1','BCUR2','BCUR3']:
            if re.search(pt_regex,record['172']['a']) != None:
                if target == 'BCURpt':
                    record = record_crosswalk(record)
                    writer.write(record)
            elif re.search(mu_regex,record['172']['a']) != None:
                if target == 'BCURmu':
                    if record['172']['2'] == 'BCUR1':
                        record = record_crosswalk(record)
                        writer.write(record)
                    else:
                        # Records matching the BCURmu (musicology, printed music) call number but not in BCUR1 are skipped
                        # Log this for safe keeping
                        print(f"SKIPPED: Record {record['001']} matches musicology call number but is outside BCUR1.")
            elif target == 'BCURcg':
                record = record_crosswalk(record)
                writer.write(record)
            
    except TypeError:
        print(f"WARNING: Record {record['001']} does not have a 172__$2 field")
      
def record_crosswalk(record):
    # This function maps a record to the format required. The original record is passed as argument and it returns the new record. 

    newrecord = Record()
    
    recordid = ''
    callnr = ''
    callorigin = ''
    newclassif = ''
    
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
                mappedvalue = vocab
                print(f"WARNING: 172__$2 for record {recordid} ({vocab}) is not in the list of mapped vocabularies.")
            
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
                # Extract subfields and concatenate them. The get_subfield() method will return them in the
                # order they are stored in the record, so no reordering is required.
                newclassif = ' -- '.join(field.get_subfields('a', 'c', 'd', 'e', 'h', 'l', 'm', 's', 't', 'v', 'x', 'X', 'y', 'z'))
                firstsubject = False
                
                # Look for unexpected subfields
                if len(field.get_subfields('9', '[')) > 0:
                    print(f"WARNING: Record {recordid} has unexpected 752 subfields:")
                    print(field)
                
                # Check for empty call numbers
                if len(callnr) < 1:
                    print(f"WARNING: Record {recordid} has an empty call number in 153__$a")
            
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
            print(f"SKIPPED: Field not mapped for record {recordid}: {field}")
    
    # Put the 153 field together
    if len(newclassif) < 1:
        # If there is no concatenated classification string, it was a record without 572, only store the call number:
        newrecord.add_ordered_field(
            Field(
                tag = '153',
                indicators = [' ',' '],
                subfields = [
                    'a', callnr]
                )
        )
    elif target in ["BCURmu", "BCURpt", "BCURcg"]:
        # If there is a concatenated classification string and target is one of the BCUR** vocabularies:
        newrecord.add_ordered_field(
            Field(
                tag = '153',
                indicators = [' ',' '],
                subfields = [
                    'a', callnr,
                    'a', target,
                    'j', newclassif]
                )
        )
    else:
        # Else, if there is a concatenated classification string, but it's another vocabulary:
        newrecord.add_ordered_field(
            Field(
                tag = '153',
                indicators = [' ',' '],
                subfields = [
                    'a', callnr,
                    'j', newclassif]
                )
        )
        
    # Add the existing 001 field (record id) as an additional 035 with (vtls_reroVD) prefix.
    newrecord.add_ordered_field(
        Field(
            tag = '035',
            indicators = [' ',' '],
            subfields = ['a', "(vtls_reroVD)" + recordid]
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
    
    # Edit and map the leader field
    # Position 17 is set to 'o' for temporary classifications (input file includes "temp")
    leader = list(record.leader)
    leader[6] = 'w'
    if inputfile.find('temp') > -1:
        leader[17] = 'o'
    else:
        leader[17] = 'n'
    newrecord.leader = ''.join(leader)
    
    return newrecord 
        

def main():
    global inputfile, target, mapping
    parser = argparse.ArgumentParser(description='Process and map classification authority records for BCUR.')
    parser.add_argument('-i','--inputfiles', type=str, nargs='+', help='one or more file(s) to be processed',required=True)
    parser.add_argument('-o','--outputfile', type=str, nargs=1, help='name of the output file',required=True)
    parser.add_argument('-m','--map', type=str, nargs=1, help='map target code',required=True,choices=valid_targets)
    
    args = parser.parse_args()
    
    targetcode = args.map[0]
    if targetcode in ('musi', 'musg'):
        mapping = False
    #elif target == 'vddoc':
        #target = ['vddoc','vddoc-la']

    
    outputfile = args.outputfile[0]
    
    global writer
    writer = XMLWriter(open(outputfile,'wb'))
    
    tstart = datetime.datetime.now()
    for infile in args.inputfiles:
        inputfile = infile
        if mapping:
            print(f"----- Processing {inputfile} with mapping {target} -----")
        else:
            print(f"----- Processing {inputfile} without mapping -----")
        target = targetcode
        map_xml(record_map,inputfile)
        
        if targetcode == 'vddoc':
            # For vddoc, also look for vddoc-la
            target = 'vddoc-la'
            map_xml(record_map,inputfile)
    
    tdiff = datetime.datetime.now() - tstart

    writer.close()    
    print(f'Job finished in {tdiff.total_seconds()} seconds. Output saved as {outputfile}')

if __name__ == "__main__":
   main()