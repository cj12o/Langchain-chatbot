from subprocess import check_output
import subprocess
import re
import asyncio
import time
import psutil
import streamlit as st 
def monitor(): 
    cmd='powershell "Get-Counter \\"\\Memory\\Available Bytes\\",\\"\\Memory\\Committed Bytes\\""'
    op=check_output(cmd, shell=True)
    op=op.decode()
    pattern=" .*[1-9]"
    match=re.findall(pattern=pattern,string=op)
    ram=float(int(match[1].strip())/2**30)
    ram="{:.2f}".format(ram)
    # yield ram
    return ram

# def fetcher():
#     while True:
#         sol=monitor()
#         return sol
#         time.sleep(2)
    
# def main():
#     for ram in monitor():
#         # print(f"{ram} GB") 
#         print(ram)
 
# # main()
def monitor():
    ram=psutil.virtual_memory()
    print(ram.used)

monitor()