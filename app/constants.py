flat_types=["csv","txt","tab"]
xl_types=["xls","xlsx","xlm","xlsm"]
#coltypes are database friendly type names
col_type_reg=["int","float","varchar(2000)"]
#regex also in functions file
regex={"ftype":"(.*)[.]{1}([A-z]+)$",
    "int":"^[0-9]*$",
    "float":"^[0-9]*[.]{1}[0-9]*$",
    "date":"""(^([1-9]|[1-2][0-9]|3[0-1])(/|-|.)(1[0-2]|0?[0-9])(/|-|.)([0-9]{2}|[0-9]{4})$|
    ^([0-9]{2}|[0-9]{4})(/|-|.)(1[0-2]|0?[0-9])(/|-|.)([1-9]|[1-2][0-9]|3[0-1])$)""",
    "varchar(2000)":".*"}
seperators={
     "commas":",",
     "pipes":"|",
     "tabs":"\t"
     }
col_data_types={
     "int": ["float","string","bool"],
     "float":["int","string"],
     "string":["date","bool","float","int"],
     "bool":["int","string"],
     "date":["string"]
     }
discrete_threshold=0.2
continuous_threshold=0.5