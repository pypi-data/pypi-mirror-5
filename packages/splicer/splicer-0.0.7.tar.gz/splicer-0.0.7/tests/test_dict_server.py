from datetime import date
from nose.tools import *

from splicer import Query, Schema, Field
from splicer.servers.dict_server import DictServer


employee_records = [
  dict(
    employee_id=1234, 
    full_name="Tom Tompson", 
    employment_date=date(2009,1,17)
  ),
  dict(
    employee_id=4567, 
    full_name="Sally Sanders",
    employment_date=date(2010,2,24),
    manager_id = 1234
  ),
  dict(
    employee_id=8901, 
    full_name="Mark Markty",
    employment_date=date(2010,3,1),
    manager_id = 1234
  )
]

def test_dict_server_with_schemas():
  server = DictServer(
    employees = dict(
      schema = dict(
        fields=[
          dict(name="employee_id", type="INTEGER"),
          dict(name="full_name", type="STRING"),
          dict(name="employment_date", type="DATE"),
          dict(name="manager_id", type="INTEGER")
        ]
      ),
      rows = employee_records
    )
  )

  employees = server.get_relation('employees')

  assert_sequence_equal(
    employees.schema.fields,
    [
      Field(name="employee_id", type="INTEGER"),
      Field(name="full_name", type="STRING"),
      Field(name="employment_date", type="DATE"),
      Field(name="manager_id", type="INTEGER")  
    ]
  )

  assert_sequence_equal(
    list(employees),
    [
      (1234, 'Tom Tompson', date(2009, 1, 17), None),
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234)
    ]
  )