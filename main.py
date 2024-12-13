from Tools.query_executor import query_executor
from Tools.query_generator_tool import query_generator

res = query_generator('how many employees are present in total')
query_executor(res['query'])