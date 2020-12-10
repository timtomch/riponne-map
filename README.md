# BCU Riponne mapping project - Dec 2020

I got invovled in a metadata cleanup project following the RenouVaud project, in which some former RERO member libraries migrated from VTLS Virtua to ExLibris Alma.
Some local classification data was lost during the migration. This project aims to extract select classification authority records from the former system
and map them to the model used by Alma.

## Lab notes

### Dec 9, 2020
Added logic for records without `172__$a`

Successfully ran the processing routine for `musg` on all `temp*` source files.

To merge the resulting XML files, I used this [XSL Transform from Oliver Becker](XLST/merge.xslt) ([source](http://web.archive.org/web/20160809092524/http://www2.informatik.hu-berlin.de/~obecker/XSLT/#merge)). 

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
- [ ] Add BCUR switching logic
- [ ] Start work on mapping function

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

