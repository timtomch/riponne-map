import argparse, re, datetime
from pymarc import marcxml, map_xml, record_to_xml, XMLWriter, Record, Field

# List of target map codes that the script understands
valid_targets = ["musi", "musg", "laf", "vddoc", "BCURmu", "BCURpt", "BCURcg"]

# Regular expressions to identify phonotheque (pt) and musicology (mu) records based on classification numbers:
pt_regex = "^\(08\)"
mu_regex = "^\(086\.[08]\)78|^\(07\)78|^\(09\)|^78"

# Global variables that are used across mutliple functions
target = ''
inputfile = ''
mapping = True

# The record_map function is called for each record in the source files. It determines which operations to run on each record
# depending on the target map code.
def record_map(record):
    try:
        if record['172']['2'] == target:
            # For straightforward target code, run field mapping if necessary, then store each found record.
            if mapping == True:
                record = record_crosswalk(record)
            writer.write(record)
        elif record['172']['2'] in ['BCUR1','BCUR2','BCUR3']:
            # For BCUR1, 2 and 3 records, the processing is different according to the call nr in 172__$a
            if re.search(pt_regex,record['172']['a']) != None:
                # If 172__$a matches the phonotheque call nrs and it's the target, run the field mapping function
                if target == 'BCURpt':
                    record = record_crosswalk(record)
                    writer.write(record)
            elif re.search(mu_regex,record['172']['a']) != None:
                # If 172__$a matches the musicology call nrs and it's the target, run the field mapping function
                # but only if 172__$2 is BCUR1
                if target == 'BCURmu':
                    if record['172']['2'] == 'BCUR1':
                        record = record_crosswalk(record)
                        writer.write(record)
                    else:
                        # Records matching the BCURmu (musicology, printed music) call number but not in BCUR1 are skipped
                        # Log this for safe keeping
                        print(f"SKIPPED: Record {record['001'].value()} matches musicology call number but is outside BCUR1.")
            elif target == 'BCURcg':
                # If neither call number format matches and we're looking for general collection records, run the field mapping function
                record = record_crosswalk(record)
                writer.write(record)
            
    except TypeError:
        print(f"WARNING: Record {record['001'].value()} does not have a 172__$2 field")


# This function maps a record to the format required. The original record is passed as argument and it returns the new record.      
def record_crosswalk(record):
        
    # A new record object is created. As we walk through fields in the original record, we will add the mapped fields to this new one.
    newrecord = Record()
    
    # Local variables to hold values that will be used outside of the for loop are defined here.
    recordid = ''
    callnr = ''
    callorigin = ''
    newclassif = ''
    
    # The first 572 field is mapped differently, this variable enables this behaviour. After the first 572 is mapped, it is set to False.
    firstsubject = True
    
    # Walk through each field in the original record
    for field in record.get_fields():
        
        # 001 field will not be mapped as is, but is recorded as record ID. It will be stored as a 035 later on.
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
            
        # 172__$2 is mapped to 084__$a according to which vocabulary is being mapped.
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
            
            # 172__$a will be mapped to 153__$a later on
            try: 
                callnr = field.get_subfields('a')[0]
            except IndexError:
                print(f"WARNING: record {recordid} has no 172__$a.")
        
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
    
    # Check for empty or missing call numbers
    if len(callnr) < 1:
        print(f"WARNING: Record {recordid} has an empty call number in 153__$a")
    
    # Put the 153 field together
    if len(newclassif) < 1:
        # If there is no concatenated classification string, it was a record without 572, only store the call number.
        # If the target is in one of the BCUR* vocabularies, also add the target as a $a 
        if target in ["BCURmu", "BCURpt", "BCURcg"]:
            newrecord.add_ordered_field(
                Field(
                    tag = '153',
                    indicators = [' ',' '],
                    subfields = [
                        'a', callnr,
                        'a', target]
                        )
                    )
        else:
            newrecord.add_ordered_field(
                Field(
                    tag = '153',
                    indicators = [' ',' '],
                    subfields = [
                        'a', callnr]
                        )
                    )
    else:
        # If there is a concatenated classification string, same process but with the new classification in a $j
        if target in ["BCURmu", "BCURpt", "BCURcg"]:
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
        
# The main function is called when the script is run. Input arguments are processed and the mapping function is
# called according to target map code on each input file.
def main():
    global inputfile, target, mapping
    parser = argparse.ArgumentParser(description='Process and map classification authority records for BCUR.')
    parser.add_argument('-i','--inputfiles', type=str, nargs='+', help='one or more file(s) to be processed',required=True)
    parser.add_argument('-o','--outputfile', type=str, nargs=1, help='name of the output file',required=True)
    parser.add_argument('-m','--map', type=str, nargs=1, help='map target code',required=True,choices=valid_targets)
    
    args = parser.parse_args()
    
    targetcode = args.map[0]
    
    # For musi and musg records, found records are copied as-is, no field mapping.
    if targetcode in ('musi', 'musg'):
        mapping = False

    outputfile = args.outputfile[0]
    
    # Open a new XML document in which target records will be stored
    global writer
    writer = XMLWriter(open(outputfile,'wb'))
    
    # Record start processing time
    tstart = datetime.datetime.now()
    
    # Loop through the list of input files and call the mapping function
    for infile in args.inputfiles:
        inputfile = infile
        target = targetcode
        if mapping:
            print(f"----- Processing {inputfile} with mapping {target} -----")
        else:
            print(f"----- Processing {inputfile} without mapping -----")
        
        # This applies the mapping function to each record in inputfile
        map_xml(record_map,inputfile)
        
        if targetcode == 'vddoc':
            # For vddoc, also look for vddoc-la
            target = 'vddoc-la'
            map_xml(record_map,inputfile)
    
    # Calculate the total time elapsed
    tdiff = datetime.datetime.now() - tstart
    
    # Close the output document
    writer.close()
    
    print(f'Job finished in {tdiff.total_seconds()} seconds. Output saved as {outputfile}')

if __name__ == "__main__":
   main()