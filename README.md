# BCU Riponne mapping project - Dec 2020

I got invovled in a metadata cleanup project following the RenouVaud project, in which some former RERO member libraries migrated from VTLS Virtua to ExLibris Alma.
Some local classification data was lost during the migration. This project aims to extract select classification authority records from the former system
and map them to the model used by Alma.

## Lab notes

### Dec 3, 2020
After trying to write my own XSL transform, I realized an easy way to get a list of all MARC tags in the source file is to use MarcEdit:
1. Convert MARCXML to MARC
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

### Dec 8, 2020
Started playing with sample file. Able to read XMLMARC using pymarc, check against `172__$a` and write file.

Running small function tests on the [walkthrough.ipynb](walkthrough.ipynb) iPython notebook then moving on to [riponne-main.py](riponne-main.py) for processing.

TO DO:
* Add logic for records without `172__$a`
* Add BCUR switching logic
* Start work on mapping function