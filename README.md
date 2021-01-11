# BCU Riponne mapping project - Dec 2020

I got invovled in a metadata cleanup project following the RenouVaud project, in which some former RERO member libraries migrated from VTLS Virtua to ExLibris Alma.
Some local classification data was lost during the migration. This project aims to extract select classification authority records from the former system
and map them to the model used by Alma.

## Usage
The main script is called `riponne-main.py` and can be run from the command-line as follows:

```
python riponne-main.py -i <SOURCE FILE(S)> -o <OUTPUT FILE> -m <MAPPING>
```
Where
* `<SOURCE FILE(S)>` (required) is the path to one or more files in MARCXML format on which to run the script. A wildcard character can be used to select multiple files.
* `<OUTPUT FILE>` (required) is the path to the file that will be written as output.
* `<MAPPING>` (required) is one of `musi`, `musg`, `laf`, `vddoc`, `BCURmu`, `BCURpt` or `BCURcg` (vocabularies to be mapped)

Log information will be output on the console. If you wish to store it in a log file, simply redirect the output to a file (see example below).

Example:

```
python riponne-main.py -i source-files/*.xml -o output/laf.xml -m laf >> log/20210105-laf.log
```


### System Requirements
Python version 3.6 or higher is required. This was tested with version 3.8.5.

The following libraries are used. You may need to install them prior to running the script:
* [pymarc](pymarc.readthedocs.io/) (for handling MARC records)
* [argparse](https://docs.python.org/3/library/argparse.html) (for parsing arguments)
* [re](https://docs.python.org/3/library/re.html) (for pattern-matching using regular expressions)
* [datetime](https://docs.python.org/3/library/datetime.html) (for tracking run time)

## Lab notes
These are my personal notes while working on this code. Feel free to disregard.

### Jan 11, 2021
Modified the script to map `019__$a` fields to `680__$i` at the request of client. Also corrected two small cataloguing inconsistencies in the source files that were discovered by analyzing the logs.

Did a fresh run on all vocabularies and delivered new mapped files.


### Jan 5, 2021
Modified logging format to be more readable, no longer logging fields that are skipped by design. Also, the log now is in French.


### Dec 15, 2020
Added another failsafe for records without `172__$a` field and ran vddoc mapping successfully.
The vddoc routine is run twice for each file, once looking for `vddoc` and once for `vddoc-la` so it takes twice as long to process (about 140 seconds instead of 70ish).
Not super efficient, could be done better, but it works. Memory usage might be an issue if running the function on a larger number of records.

Added more inline documentation and cleaned up code a little.

Corrected the CLASBCUR routine that wasn't storing `153__$a` properly when classification strings were missing.

Also found out when trying to merge a few output files that [XSLT merge](XSLT/merge.xslt) isn't doing what we want (merging records).
But thanks to the fact that the tree is quite simple, it's easy to merge them with a series of quick bash lines:

```
$ sed '$d' firstfile.xml > merged.xml
$ sed '$d' middlefile.xml | tail -n +3 >> merged.xml 
$ tail -n +3 lastfile.xml >> merged.xml 
```

This does the trick, but it would be more elgant to write a little script to do it in one fell swoop.

TO DO:
- [ ] Write a better way to merge XMLs

### Dec 14, 2020
Rewrote the main function using [`argparse`](https://docs.python.org/3/howto/argparse.html) in order to accept multiple input files and loop through them. This way, output from
mulitple input files is stored in the same file.

Fixed some faulty logic that wasn't mapping temporary (short) records well enough.

Added some processing to the LDR (position 17 is set to `w` for full records and `o` for temp/short records).

Enhanced logging functionality to track all skipped fields and subfields.

Did some stress testing and ran all mappings for client to check.

TO DO:
- [x] Write usage documentation
- [x] Add failsafe for records without a 172__$a
- [x] Run vddoc mapping


### Dec 13, 2020
Completed the mapping function, including BCUR regex logic. Trial run on BCURmu successful.

More stress tests required.

TO DO:
- [x] Log unmapped subfields
- [x] Complete inline documentation
- [x] Investigate if merging resulting files can happen in Python (accept multiple input files)


### Dec 12, 2020
Completed most of the mapping function.

TO DO:
- [x] Map remaining 572s - find a way to copy field with all subfields
- [x] Check if all possible subfields are taken care of in 153__$j concatenation
- [x] Add failsafe for 153__$a in case there are no 572s
- [x] Find out what needs to happen to LDR
- [x] Log all unmapped fields
- [x] Less permissive error catching - log all errors

Need to do some stress-testing too.

### Dec 9, 2020
Added logic for records without `172__$a`

Successfully ran the processing routine for `musg` on all `temp*` source files.

To merge the resulting XML files, I used this [XSL Transform from Oliver Becker](XSLT/merge.xslt) ([source](http://web.archive.org/web/20160809092524/http://www2.informatik.hu-berlin.de/~obecker/XSLT/#merge)). 

Usage (I need to find a better way to call Java8, which is needed by the latest version of Saxon):

```
/Library/Internet\ Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java -jar ../SaxonHE10-3J/saxon-he-10.3.jar output/musg0.xml XSLT/merge.xslt with=musg1.xml > musg01.xml
```

Come to think of it, this could be done in Python directly as well, I suppose.

### Dec 8, 2020
Started playing with sample file. Able to read XMLMARC using pymarc, check against `172__$a` and write file.

Running small function tests on the [walkthrough.ipynb](walkthrough.ipynb) iPython notebook then moving on to [riponne-main.py](riponne-main.py) for processing.

XML output files can be cleaned up (i.e. nicely indented etc.) by using `xmllint -format -recover outfile.xml > outfile-clean.xml`.

TO DO:
- [x] Add logic for records without `172__$a`
- [x] Add BCUR switching logic
- [x] Start work on mapping function

### Dec 3, 2020
After trying to write my own XSL transform, I realized an easy way to get a list of all MARC tags in the source file is to use MarcEdit:
1. Convert MARCXML to MARC (edit: this is not actually necessary, MarcEdit can open MARCXML natively)
2. Run the Field Count report in MarcEdit

Sample:

| Field | Subfield | In Records | Total | 
|-------|----------|------------|-------| 
| 000   |          | 5          | 5     | 
| 001   |          | 5          | 5     | 
| 005   |          | 5          | 5     | 
| 008   |          | 5          | 5     | 
| 035   |          | 5          | 5     | 
|       | $a       |            | 5     | 
| 039   |          | 5          | 5     | 
|       | $d       |            | 2     | 
|       | $a       |            | 3     | 
|       | $c       |            | 2     | 
|       | $b       |            | 3     | 
|       | $y       |            | 5     | 
|       | $z       |            | 5     | 
| 040   |          | 5          | 5     | 
|       | $a       |            | 5     | 
|       | $b       |            | 1     | 
| 072   |          | 1          | 1     | 
|       | $a       |            | 1     | 
| 172   |          | 5          | 5     | 
|       | $e       |            | 1     | 
|       | $a       |            | 5     | 
|       | $d       |            | 1     | 
|       | $2       |            | 5     | 
| 572   |          | 3          | 8     | 
|       | $a       |            | 8     | 
|       | $x       |            | 3     | 
|       | $2       |            | 8     | 
|       | $v       |            | 7     | 

