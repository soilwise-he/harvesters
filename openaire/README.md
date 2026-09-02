# OpenAire harvester

The harvester fetches all records with a subject=soil (including soil organic carbon, soil tillage, etc) from OpenAire
It fetches records per month, but the publication date of the record. You can set the month to be harvested by setting
an environment variable `DATEFROM`

Note that OpenAire has a max records in a single query of 10.000. Usually months have between 1000-3000 records published.