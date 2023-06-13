
import os
import subprocess 
import tempfile
import time
import boto3
import botocore
s3_client=boto3.client('s3')
s3_resource = boto3.resource('s3')

import pymysql
import json

task=os.environ['task']
rds_endpoint = os.environ['rds_endpoint']
secret_string=os.environ['secret_string']
aws_region=os.environ['aws_region']
mysql_database=os.environ['mysql_database']

secret_dict=eval(secret_string)
username = secret_dict['username']
print(username)
password = secret_dict['password']
mysql_host_name=rds_endpoint[0:-5]
print(mysql_host_name)

file_name=os.environ['file_name']
s3_bucket=os.environ['s3_bucket']
s3_key=os.environ['s3_key']
s3_key_withoutextension=os.environ['s3_key_withoutextension']

if task=='rds_init':  
  print('the task is rds_init')
  try:
    stage=1
    # download s3 file to locally
    s3_resource.Bucket(s3_bucket).download_file(s3_key, file_name)
    #print(open(file_name).read())
    file= open(file_name, 'r') 
    # read all content of a file
    lines=file.readlines()
    # check if string present in a file
    count=0
    for line in lines:
      if 'DELIMITER &&' in line:
        count=count+1
    procedures_num=count
    print('file_name is {}, including {} procedures'.format(file_name,procedures_num))
    stage=2
    # execute the whole file using MySQL command line
    # first to solve the problem 'mysql not found'
    # find mysql 
    
    find_sql='which mysql'
    process1=subprocess.run(find_sql, stdout=subprocess.PIPE, shell=True )
    result=process1.stdout.decode('utf-8')
    print("MySQL installed in {}".format(result))
    mysql_path=result[0:-7]
    print('mysql_path is {}'.format(mysql_path))
    # set MySQL bin folder to PATH
    set_path="export PATH={}:$PATH".format(result)
    process2=subprocess.Popen(set_path,shell=True)

    #current_workdir=os.getcwd()
    #print(current_workdir)
    #file_path='{}/{}'.format(current_workdir,file_name)
    #print('file_path is {}'.format(file_path))
    # finally execute .sql file
    mysql_command='mysql -h {} -u {} -p{} -D {} < /{}'.format(mysql_host_name,username,password,mysql_database,file_name)
    print('init_command is {}'.format(mysql_command))
    process=subprocess.Popen(mysql_command,shell=True)
    
    stage=3 
    # test for db
    conn = pymysql.connect(host=mysql_host_name, user=username, password=password, db=mysql_database, connect_timeout=10)
    print('connection to {} is successful'.format(mysql_host_name))
    sql_query=' SELECT count(ROUTINE_NAME) FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE="PROCEDURE" AND ROUTINE_SCHEMA={} and ROUTINE_NAME LIKE "sp_{}%";'.format(mysql_database,s3_key_withoutextension)
    #sql_query=' SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE="PROCEDURE";'.format(s3_key_withoutextension)
    # the above mysql command line may take time to complete
    # use a loop to find the final result of executing command line
    attempts=0
    MAX_WAIT_CYCLES=20
    print("Executing {}".format(sql_query))
    record=0
    while attempts < MAX_WAIT_CYCLES:
      attempts += 1
      time.sleep(3) 
      with conn.cursor() as cur:
        cur.execute(sql_query)
      record=cur.fetchone()[0] 
      if record==procedures_num :
        break
    conn.commit
    if record==procedures_num:
      print('Result after checking is {}'.format(record))
      print('Database Init completed. {}/{}'.format(s3_bucket,s3_key))
    else:
      print('Result after checking is {}, supposed to be {}'.format(record,procedures_num))
      print('Database Init failed. {}/{}'.format(s3_bucket,s3_key))
  except botocore.exceptions.ClientError as e:
    if stage==1 and e.response['Error']['Code'] == "404":
      print("The object does not exist. {}".format(e))
    else:
      print_content="error occurred during stage {} : {}".format(stage,e)
      print(print_content)  
      
elif task =='web_request':
  print('the task is web_request')
  # to continue with tasks for web
