Docker + MySQL Client + Python

Base Image: python:3.10-slim-buster

ECS won't be installed MySQL Database. It connects external MySQL database in the same VPC in the cloud.
MySQL Client is intalled only and ECS will set up external database using MySQL Command Line.

Note:
AWS RDS for MySQL (Not Aurora MySQL) have below limitations for data loading:
1) No Data API
    We can't execute SQL query out of VPC
2) No execute_many method
    We can't execute multiple lines at one time. 
    It is possible to execute line by line for "SELECT ..., INSERT..." statements using 'cursor.execute()'.
    But we can't create procedures for multiple lines at one time.

For MySQL DB Init, the solution is to use lambda outside of VPC to trigger/run ECS task using images built in this repository.
