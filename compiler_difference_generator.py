'''
Author : ABHIRAJ.G
Email id : abhiraj.garakapati@gmail.com

Input should be like this: 
python -W ignore db4.py <latest compiler rev> <previous compiler rev> <work directory> <MAINLINE or STAGING>

Example:
python -W ignore db7.py 304 299 STAGING

(Automated way of collecting data from db about the jobid's of a particular compiler rev and doing diff between all 32/64 bit bmks/apps and tabulating results. Also printing the runnable  format.)
'''

# Import section:
#########################################
import MySQLdb
import os
import re
import sys
from prettytable import PrettyTable
import HTML
import glob
#########################################

# Command line arguments:
#########################
path = sys.argv
#########################

# All Functions:
######################################################################################################################

# Function to convert a flag file to dictionary
def flag(path):
	z=0
	f={}
	file1 = [line.rstrip('\n') for line in open(path)]
	for i in file1:
		if(len(file1[z].split(":="))==2):
			a=file1[z].split(":=")[0]
			a = re.sub('[# ]', '', a)
			f[a]=file1[z].split(":=")[1]
		z=z+1
	return f



# Function to Print the output in a tabular form if "prettytable" module cannot be used.
def print_result(x):
	if (x[1]==None):
		print "%-20s %-20s %-20s %-20s %-20s %-20s %-20s"%(x[0],"N/A",x[2],x[3],x[4],x[5],x[6])
	else:
		print "%-20s %-20s %-20s %-20s %-20s %-20s %-20s"%(x[0],x[1],x[2],x[3],x[4],x[5],x[6])

def print_table(x):
	t=0
	t = PrettyTable(["Name","AppsuiteName","Fk_runStatus","Fk_sched_machineName","StartTime","EndTime","Runid"])
	# print data_cur
	for k,i in zip(x,range(0,len(x))):
		for j in range(0,len(k)):
			t.add_row(x[i][j])
			
	print t
	
def print_diff_table_1(c1,c2,d1):	
	t=0
	t = PrettyTable(["Name","AppsuiteName","Fk_runStatus","Fk_sched_machineName","StartTime","EndTime","Runid"])
				
	for i in range(0,len(c1)):
		for j in range(0,len(c2)):
			if (c1[i] == c2[j]):
				j=0
				break
			else:
				continue
		if (j+1 == len(c2)):
			if (d1[c1[i]][2].split("-")[1] == "failures"):
				pass
			else:
				t.add_row(d1[c1[i]])
	print t
	print "\n"

def print_diff_table(c1,c2,d1):	
	t=0
	t = PrettyTable(["Name","AppsuiteName","Fk_runStatus","Fk_sched_machineName","StartTime","EndTime","Runid"])
				
	for i in range(0,len(c1)):
		for j in range(0,len(c2)):
			if (c1[i] == c2[j]):
				j=0
				break
			else:
				continue
		if (j+1 == len(c2)):
			t.add_row(d1[c1[i]])
	print t
	print "\n"	
	

	
def print_all_diff_table(c1,c2,d1):	
	t = PrettyTable(["Name "+path[1],"Name "+path[2]])
	c=[]
	count=0
	for i in range(0,len(c1)):
		for j in range(0,len(c2)):
			if (c1[i] == c2[j]):
				c.append([c1[i],c2[j]])
				count+=1
				j=0
				break
			else:
				continue
	for i in range(0,len(c1)):
		t.add_row(c[i])
	print t
	print "total : "+str(count)
	print "length of "+path[1]+" is : "+str(len(c1))
	print "length of "+path[2]+" is : "+str(len(c2))
	print "\n"	
	
def print_status_file(jobID):	
	
	cur=con.cursor()
	cur.execute("SELECT runStatus FROM JobStatus;")
	data=cur.fetchall()
	cur.close()
	
	n=0
	
	while (n<=len(data)-1):
		cur=con.cursor()
		cur.execute("SELECT COUNT(*) FROM JobRunQueue,Application WHERE ((runid LIKE '%"+jobID[0]+"') AND (Application.appID = JobRunQueue.fk_appID) AND fk_runStatus = '"+data[n][0]+"');")
		count=cur.fetchall()
		cur.close()
		count = int(re.sub('[L]', '', str(count[0][0])))
		if (count==0):
			pass
		else:
			data_aquired=[]
			cur=con.cursor()
			cur.execute("SELECT name,appsuiteName,JobRunQueue.fk_runStatus,JobRunQueue.fk_sched_machineName,JobRunQueue.startTime,JobRunQueue.endTime,JobRunQueue.runid  FROM JobRunQueue,Application WHERE ((runid LIKE '%"+jobID[0]+"%') AND (Application.appID = JobRunQueue.fk_appID) AND fk_runStatus = '"+data[n][0]+"') ORDER BY appsuiteName,name ASC;")
			data_aquired.append(cur.fetchall())
			print_table(data_aquired)
			
		n=n+1	

	
# Function to Fetch all the required information from the database and Printing the failures in tabular form including run format.
def db_diff(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = data_aquired_to_list_dict(data_cur)
	(c2,d2) = data_aquired_to_list_dict(data_pre)		
	(c11,d11) = all_data_aquired_to_list_dict(data_cur)
	(c22,d22) = all_data_aquired_to_list_dict(data_pre)
	# print_diff_table_html(c1,c2,d11)
	print_diff_table(c1,c2,d11)
	
	print_runcommands(jobID1,c1,c2,d1,type)

def rev_db_diff(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = data_aquired_to_list_dict(data_cur)
	(c2,d2) = data_aquired_to_list_dict(data_pre)		
	(c11,d11) = all_data_aquired_to_list_dict(data_cur)
	(c22,d22) = all_data_aquired_to_list_dict(data_pre)
	# print_diff_table_1_html(c2,c1,dict(d22.items() + d11.items()))
	print_diff_table_1(c2,c1,dict(d22.items() + d11.items()))
	
	print_runcommands(jobID1,c1,c2,d1,type)
	
def all_db_diff(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = all_data_aquired_to_list_dict(data_cur)
	(c2,d2) = all_data_aquired_to_list_dict(data_pre)		

	# print_diff_table_html(c1,c2,dict(d2.items() + d1.items()))
	print_diff_table(c1,c2,dict(d2.items() + d1.items()))
	
	print_runcommands(jobID1,c1,c2,d1,type)

def rev_all_db_diff(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = all_data_aquired_to_list_dict(data_cur)
	(c2,d2) = all_data_aquired_to_list_dict(data_pre)		

	# print_diff_table_html(c2,c1,dict(d2.items() + d1.items()))
	print_diff_table(c2,c1,dict(d2.items() + d1.items()))
	print_runcommands(jobID1,c1,c2,d1,type)
	

	# print_diff_table(c1,c2,d11)
	
	# print_runcommands(jobID1,c1,c2,d1,type)


	# print_diff_table(c2,c1,dict(d2.items() + d1.items()))
	# print_runcommands(jobID1,c1,c2,d1,type)
	
def display_all_in_list(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = all_data_aquired_to_list_dict(data_cur)
	(c2,d2) = all_data_aquired_to_list_dict(data_pre)		

	
	print_all_diff_table(c1,c2,d1)
	
	# print_runcommands(jobID1,c1,c2,d1,type)	
		
	
	# print_diff_table_1(c2,c1,dict(d22.items() + d11.items()))
	
	# print_runcommands(jobID1,c1,c2,d1,type)
	
	# print_diff_table(c1,c2,dict(d2.items() + d1.items()))
	
	# print_runcommands(jobID1,c1,c2,d1,type)


	
	
# Function to To fetch respective CompilerRev from the data base and save it as a dictionary.
def jobids_compilerRev(compilerRev):
	data=[]
	data1=[]
	data2=[]
	d={}
	if (path[3]=="MAINLINE"):
		cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%WeeklyFuncTestingMainline/MAINLINE/"+compilerRev+"%' LIMIT 4;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%WeeklyFuncTestingMainline/MAINLINE/"+compilerRev+"%' order by startDate desc LIMIT 4;")
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%WeeklyFuncTestingMainline/MAINLINE/"+compilerRev+"%' order by startDate LIMIT 4;")
		data1=cur.fetchall()
		cur.close()
		cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%mx32FuncTestMainline/MAINLINE/"+compilerRev+"%' LIMIT 2;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%mx32FuncTestMainline/MAINLINE/"+compilerRev+"%' order by startDate desc LIMIT 2;")
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%mx32FuncTestMainline/MAINLINE/"+compilerRev+"%' order by startDate LIMIT 2;")
		data2=cur.fetchall()
		cur.close()
		data=data1+data2
	elif (path[3]=="STAGING"):
		cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"%') LIMIT 4;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"%') order by startDate desc LIMIT 4;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"%') order by startDate LIMIT 4;")
		
		# Latest.
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/32/passing_c_cpp_fortran_omp_bmks%') order by startDate desc LIMIT 1;")
		data1=cur.fetchall()
		cur.close()
		cur=con.cursor()
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/64/passing_c_cpp_fortran_omp_bmks%') order by startDate desc LIMIT 1;")
		data2=cur.fetchall()
		cur.close()
		cur=con.cursor()
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/32/passing_c_cpp_fortran_apps%') order by startDate desc LIMIT 1;")
		data3=cur.fetchall()
		cur.close()
		cur=con.cursor()
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/64/passing_c_cpp_fortran_apps%') order by startDate desc LIMIT 1;")
		
		# First.
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/32/passing_c_cpp_fortran_omp_bmks%') order by startDate LIMIT 1;")
		# data1=cur.fetchall()
		# cur.close()
		# cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/64/passing_c_cpp_fortran_omp_bmks%') order by startDate LIMIT 1;")
		# data2=cur.fetchall()
		# cur.close()
		# cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/32/passing_c_cpp_fortran_apps%') order by startDate LIMIT 1;")
		# data3=cur.fetchall()
		# cur.close()
		# cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/64/passing_c_cpp_fortran_apps%') order by startDate LIMIT 1;")
		data4=cur.fetchall()
		cur.close()
		data=data1+data2+data3+data4
	for i in range(0,len(data)):
		a=[]
		a=[data[i][1].split("/")[-2],data[i][1].split("/")[-1].split("_")[-1]]
		d["_".join(a)]=data[i]
	
	return d	
		
def jobids_compilerRev1(compilerRev):
	data=[]
	data1=[]
	data2=[]
	d={}
	if (path[3]=="MAINLINE"):
		cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%WeeklyFuncTestingMainline/MAINLINE/"+compilerRev+"%' LIMIT 4;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%WeeklyFuncTestingMainline/MAINLINE/"+compilerRev+"%' order by startDate desc LIMIT 4;")
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%WeeklyFuncTestingMainline/MAINLINE/"+compilerRev+"%' order by startDate LIMIT 4;")
		data1=cur.fetchall()
		cur.close()
		cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%mx32FuncTestMainline/MAINLINE/"+compilerRev+"%' LIMIT 2;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%mx32FuncTestMainline/MAINLINE/"+compilerRev+"%' order by startDate desc LIMIT 2;")
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs Where logDir LIKE '%mx32FuncTestMainline/MAINLINE/"+compilerRev+"%' order by startDate LIMIT 2;")
		data2=cur.fetchall()
		cur.close()
		data=data1+data2
	elif (path[3]=="STAGING"):
		cur=con.cursor()
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"%') LIMIT 4;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"%') order by startDate desc LIMIT 4;")
		# cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"%') order by startDate LIMIT 4;")
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/32/passing_c_cpp_fortran_omp_bmks%') order by startDate LIMIT 1;")
		data1=cur.fetchall()
		cur.close()
		cur=con.cursor()
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/64/passing_c_cpp_fortran_omp_bmks%') order by startDate LIMIT 1;")
		data2=cur.fetchall()
		cur.close()
		cur=con.cursor()
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/32/passing_c_cpp_fortran_apps%') order by startDate LIMIT 1;")
		data3=cur.fetchall()
		cur.close()
		cur=con.cursor()
		cur.execute("select jobID,logDir,runStatus,compilerName,compilerType,compilerPath,bitness from Jobs WHERE (logDir LIKE '%STAGING/"+compilerRev+"/64/passing_c_cpp_fortran_apps%') order by startDate LIMIT 1;")
		data4=cur.fetchall()
		cur.close()
		data=data1+data2+data3+data4
	for i in range(0,len(data)):
		a=[]
		a=[data[i][1].split("/")[-2],data[i][1].split("/")[-1].split("_")[-1]]
		d["_".join(a)]=data[i]
	
	return d			
	
def db_log_path(jobID1):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	(c1,d1) = data_aquired_to_list_dict(data_cur)
	return d1[c1[0]][7].split("/*")[0]
	
	
	
############################################################################################################
# Initial Funtions:

def status_file(jobID):	
	
	cur=con.cursor()
	cur.execute("SELECT runStatus FROM JobStatus;")
	data=cur.fetchall()
	cur.close()
	
	data_aquired=[]
	n=0
	
	while (n<=len(data)-1):
		cur=con.cursor()
		cur.execute("SELECT COUNT(*) FROM JobRunQueue,Application WHERE ((runid LIKE '%"+jobID[0]+"') AND (Application.appID = JobRunQueue.fk_appID) AND fk_runStatus = '"+data[n][0]+"');")
		count=cur.fetchall()
		cur.close()
		count = int(re.sub('[L]', '', str(count[0][0])))
		if (count==0):
			pass
		else:
			cur=con.cursor()
			# cur.execute("SELECT name,appsuiteName,JobRunQueue.fk_runStatus,JobRunQueue.fk_sched_machineName,JobRunQueue.startTime,JobRunQueue.endTime,JobRunQueue.runid  FROM JobRunQueue,Application WHERE ((runid LIKE '%"+jobID[0]+"%') AND (Application.appID = JobRunQueue.fk_appID) AND fk_runStatus = '"+data[n][0]+"') ORDER BY appsuiteName,name ASC;")
			cur.execute("SELECT Application.name,Application.appsuiteName,JobRunQueue.fk_runStatus,JobRunQueue.fk_sched_machineName,JobRunQueue.startTime,JobRunQueue.endTime,JobRunQueue.runid,concat(Jobs.logDir,'/*',JobRunQueue.runid,'*') FROM Jobs,JobRunQueue,Application WHERE ((runid LIKE '%"+jobID[0]+"%') AND (Application.appID = JobRunQueue.fk_appID) AND (Jobs.jobID LIKE '%"+jobID[0]+"%') AND fk_runStatus = '"+data[n][0]+"') ORDER BY appsuiteName,name ASC;")
			data_aquired.append(cur.fetchall())
		n=n+1
	return data_aquired

def data_aquired_to_list_dict(data_aquired):
	
	d1={}
	c1=[]
	
	for k,i in zip(data_aquired,range(0,len(data_aquired))):
		for j in range(0,len(k)):
			try:
				if (data_aquired[i][j][2].split("-")[1] == "failures"):
					b=[]
					b=[data_aquired[i][j][0],data_aquired[i][j][6].split("_")[-6]]
					c1.append("_".join(b)) 
					d1["_".join(b)] = data_aquired[i][j]
				else:
					break	
			except Exception:
				pass
	return (c1,d1)

def all_data_aquired_to_list_dict(data_aquired):
	
	d1={}
	c1=[]
	
	for k,i in zip(data_aquired,range(0,len(data_aquired))):
		for j in range(0,len(k)):
			# if (data_aquired[i][j][2].split("-")[1] == "failures"):
				b=[]
				b=[data_aquired[i][j][0],data_aquired[i][j][6].split("_")[-6]]
				c1.append("_".join(b)) 
				d1["_".join(b)] = data_aquired[i][j]
			# else:
				# break	
	return (c1,d1)	
	
def print_diff_table_html(c1,c2,d1,d2,table,only_count=0):	
	count=0
	t=0
	# t = PrettyTable(["Name","AppsuiteName","TestStatus","Fk_sched_machineName","StartTime","EndTime","Runid","LogPath"])
	if(table == "regression"):
		t = HTML.Table(header_row= HTML.TableRow(["Name","AppsuiteName","TestStatus","PrevTestStatus","Machine","PrevMachine","StartTime","EndTime","Runid","LogPath"], bgcolor='LightGrey'))			
	else:
		t = HTML.Table(header_row= HTML.TableRow(["Name","AppsuiteName","TestStatus","Machine","StartTime","EndTime","Runid","LogPath"], bgcolor='LightGrey'))	
	for i in range(0,len(c1)):
		for j in range(0,len(c2)):
			if (c1[i] == c2[j]):
				j=0
				# print c1[i],c2[j],"break"
				break
			else:
				# print c1[i],c2[j],"continue"
				continue
		if (j+1 == len(c2)):
			# print c1[i],c2[j],"if"
			try:
				path2 = glob.glob(d1[c1[i]][7])[0].split("testing/")[1]
				path1 = "http://msdnkvstability.amd.com/AQI_logs/"
				path = path1 + path2
				if (d1[c1[i]][1]==None):
					temp=[]
					if(table == "regression"):
						try:
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
						except Exception:
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],"N/A",d1[c1[i]][3],"N/A",d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
					else:
						try:
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
						except Exception:
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
					t.rows.append(temp)
					# t.rows.append(HTML.TableRow(temp, bgcolor='LightGreen'))
					count = count+1
				else:
					temp=[]
					if(table == "regression"):
						try:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
						except Exception:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],"N/A",d1[c1[i]][3],"N/A",d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
					else:
						try:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
						except Exception:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
					t.rows.append(temp)
					# t.rows.append(HTML.TableRow(d1[c1[i]], bgcolor='LightGreen'))
					count = count+1
						
			except Exception:
				path = "Log file not present."
				if (d1[c1[i]][1]==None):
					temp=[]
					if(table == "regression"):
						try:
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
						except Exception:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],"N/A",d1[c1[i]][3],"N/A",d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
					else:
						try:
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
						except Exception:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
					t.rows.append(temp)
					# t.rows.append(HTML.TableRow(temp, bgcolor='LightGreen'))
					count = count+1
				else:
					temp=[]
					if(table == "regression"):
						try:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
						except Exception:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],"N/A",d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
					else:
						try:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
						except Exception:
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
					t.rows.append(temp)
					# t.rows.append(HTML.TableRow(d1[c1[i]], bgcolor='LightGreen'))
					count = count+1
	if (only_count == 0):
		
		if (count != 0):
			if(table == "regression"):
				print "<p><font color='Red'>Regressions :</font></p>"
			elif(table == "new_benchmarks"):
				print "<p><font color='Green'>New Benchmarks :</font></p>"	
			elif(table == "missing_benchmarks"):
				print "<p><font color='Red'>Missing Benchmarks :</font></p>"	
			print t
		else:
			if(table == "regression"):
				print "<p><font color='Red'>Regressions : None.</font></p>"
			elif(table == "new_benchmarks"):
				print "<p><font color='Green'>New Benchmarks : None.</font></p>"	
			elif(table == "missing_benchmarks"):
				print "<p><font color='Red'>Missing Benchmarks : None.</font></p>"	
	print "\n"	
	return count
	
# Regression.
def regression_html(jobID1,jobID2,type):
	table = "regression"
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = data_aquired_to_list_dict(data_cur)
	(c2,d2) = data_aquired_to_list_dict(data_pre)		
	(c11,d11) = all_data_aquired_to_list_dict(data_cur)
	(c22,d22) = all_data_aquired_to_list_dict(data_pre)
	count = print_diff_table_html(c1,c2,d11,d22,table)
	return count

# Progressions.

def print_diff_table_1_html(c1,c2,d1,d2,only_count=0):	
	t=0
	count=0
	# t = PrettyTable(["Name","AppsuiteName","Fk_runStatus","Fk_sched_machineName","StartTime","EndTime","Runid"])
	t = HTML.Table(header_row= HTML.TableRow(["Name","AppsuiteName","TestStatus","PrevTestStatus","Machine","PrevMachine","StartTime","EndTime","Runid","LogPath"], bgcolor='LightGrey'))

	for i in range(0,len(c1)):
		for j in range(0,len(c2)):
			if (c1[i] == c2[j]):
				j=0
				break
			else:
				continue
		if (j+1 == len(c2)):
			try:
				if (d1[c1[i]][2].split("-")[1] == "failures"):
					pass
				else:
					try:
						path2 = glob.glob(d1[c1[i]][7])[0].split("testing/")[1]
						path1 = "http://msdnkvstability.amd.com/AQI_logs/"
						path = path1 + path2
						if (d1[c1[i]][1]==None):
							temp=[]
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
							t.rows.append(temp)
							# t.rows.append(HTML.TableRow(temp, bgcolor='LightGreen'))
							count = count+1
						else:
							temp=[]
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>"]
							t.rows.append(temp)
							# t.rows.append(HTML.TableRow(d1[c1[i]], bgcolor='LightGreen'))
							count = count+1
							
					except Exception:
						path = "Log file not present."
						if (d1[c1[i]][1]==None):
							temp=[]
							temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
							t.rows.append(temp)
							# t.rows.append(HTML.TableRow(temp, bgcolor='LightGreen'))
							count = count+1
						else:
							temp=[]
							temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d2[c1[i]][2],d1[c1[i]][3],d2[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],path]
							t.rows.append(temp)
							# t.rows.append(HTML.TableRow(d1[c1[i]], bgcolor='LightGreen'))
							count = count+1
			except Exception:
				pass
	if (only_count == 0):	
		if (count != 0):
			print "<p><font color='Green'>Progressions :</font></p>"	
			print t
		else:
			print "<p><font color='Green'>Progressions : None.</font></p>"	
	print "\n"
	return count

def progressions_html(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = data_aquired_to_list_dict(data_cur)
	(c2,d2) = data_aquired_to_list_dict(data_pre)		
	(c11,d11) = all_data_aquired_to_list_dict(data_cur)
	(c22,d22) = all_data_aquired_to_list_dict(data_pre)
	count = print_diff_table_1_html(c2,c1,dict(d22.items() + d11.items()),d22)
	return count

# Known issues.

def data_aquired_to_list_dict_known_issues(data_aquired):
	
	d1={}
	c1=[]
	
	for k,i in zip(data_aquired,range(0,len(data_aquired))):
		for j in range(0,len(k)):
			try:
				if (data_aquired[i][j][2].split("-")[1] == "failures"):
					b=[]
					b=[data_aquired[i][j][0],data_aquired[i][j][2],data_aquired[i][j][6].split("_")[-6]]
					c1.append("_".join(b)) 
					d1["_".join(b)] = data_aquired[i][j]
				else:
					break	
			except Exception:
				pass
	return (c1,d1)	
	
def print_diff_table_html_known_issues(c1,c2,d1,only_count=0):	
	count=0
	t=0
	# t = PrettyTable(["Name","AppsuiteName","Fk_runStatus","Fk_sched_machineName","StartTime","EndTime","Runid","LogPath"])
	t = HTML.Table(header_row= HTML.TableRow(["Name","AppsuiteName","TestStatus","Machine","StartTime","EndTime","Runid","LogPath","JIRA ID"], bgcolor='LightGrey'))			
	for i in range(0,len(c1)):
		for j in range(0,len(c2)):
			if (c1[i] == c2[j]):
				try:
					path2 = glob.glob(d1[c1[i]][7])[0].split("testing/")[1]
					path1 = "http://msdnkvstability.amd.com/AQI_logs/"
					path = path1 + path2
				except Exception:
					path = ""
				if (d1[c1[i]][1]==None):
					temp=[]
					try:
						temp_var = [c1[i].split('_done')[0],c1[i].split('_')[-1]]
						temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>",get_jira_ticket_id['_'.join(temp_var)]]
					except Exception:
						temp=[d1[c1[i]][0],"N/A",d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>","None"]
					t.rows.append(temp)
					# t.rows.append(HTML.TableRow(temp, bgcolor='LightGreen'))
					count = count+1
				else:
					temp=[]
					try:
						temp_var = [c1[i].split('_done')[0],c1[i].split('_')[-1]]
						temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>",get_jira_ticket_id['_'.join(temp_var)]]
					except Exception:
						temp=[d1[c1[i]][0],d1[c1[i]][1],d1[c1[i]][2],d1[c1[i]][3],d1[c1[i]][4],d1[c1[i]][5],d1[c1[i]][6],"<a href="+path+">web_link</a>","None"]
					t.rows.append(temp)
					# t.rows.append(HTML.TableRow(d1[c1[i]], bgcolor='LightGreen'))
					count = count+1
				break
			else:
				continue
	if (only_count == 0):
		if (count != 0):
			print "<p><font color='Chocolate'>Known issues :</font></p>"	
			print t
		else:
			print "<p><font color='Chocolate'>Known issues : None.</font></p>"		
	print "\n"	
	return count	

def known_issues_html(jobID1,jobID2,type):
	
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = data_aquired_to_list_dict_known_issues(data_cur)
	(c2,d2) = data_aquired_to_list_dict_known_issues(data_pre)		
	# (c11,d11) = all_data_aquired_to_list_dict(data_cur)
	# (c22,d22) = all_data_aquired_to_list_dict(data_pre)
	count = print_diff_table_html_known_issues(c1,c2,d1)
	return count

# New Benchmarks.	
def new_benchmarks_html(jobID1,jobID2,type):
	table = "new_benchmarks"
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = all_data_aquired_to_list_dict(data_cur)
	(c2,d2) = all_data_aquired_to_list_dict(data_pre)		

	count = print_diff_table_html(c1,c2,dict(d2.items() + d1.items()),d2,table)
	return count

# Missing Benchmarks.
def missing_benchmarks_html(jobID1,jobID2,type):
	table = "missing_benchmarks"
	n=0
	data=[]
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	
	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
	
	# print_table(data_cur)
	# print_table(data_pre)
	# print data_cur
	# print data_pre
	
	(c1,d1) = all_data_aquired_to_list_dict(data_cur)
	(c2,d2) = all_data_aquired_to_list_dict(data_pre)		

	count = print_diff_table_html(c2,c1,dict(d2.items() + d1.items()),d2,table)
	return count

def count_all(jobID1,jobID2):
	data_cur=[]
	data_pre=[]
	d1={}
	c1=[]
	d2={}
	c2=[]
	d11={}
	c11=[]
	d22={}
	c22=[]
	dk1={}
	ck1=[]
	dk2={}
	ck2=[]

	data_cur = status_file(jobID1)
	data_pre = status_file(jobID2)
		
	(c1,d1) = data_aquired_to_list_dict(data_cur)
	(c2,d2) = data_aquired_to_list_dict(data_pre)		
	(c11,d11) = all_data_aquired_to_list_dict(data_cur)
	(c22,d22) = all_data_aquired_to_list_dict(data_pre)
	(ck1,dk1) = data_aquired_to_list_dict_known_issues(data_cur)
	(ck2,dk2) = data_aquired_to_list_dict_known_issues(data_pre)		
	
	Regressions_count.append(print_diff_table_html(c1,c2,d11,d22,"regression",1))
	Progressions_count.append(print_diff_table_1_html(c2,c1,dict(d22.items() + d11.items()),d22,1))
	Known_issues_count.append(print_diff_table_html_known_issues(ck1,ck2,dk1,1))
	New_benchmarks_count.append(print_diff_table_html(c11,c22,dict(d22.items() + d11.items()),d22,"new_benchmarks",1))
	Missing_benchmarks_count.append(print_diff_table_html(c22,c11,dict(d22.items() + d11.items()),d22,"missing_benchmarks",1))
	
Regressions_count = []
Progressions_count = []
Known_issues_count = []
New_benchmarks_count = []
Missing_benchmarks_count = []	
	
def print_summary_table_html(m32_apps,m64_apps,mx32_apps,m32_bmks,m64_bmks,mx32_bmks,run_ids):	
	count = 0
	t = 0
	table_types = ["Regressions","Progressions","Known issues","New Benchmarks","Missing Benchmarks"]
	if (path[3]=="MAINLINE"):
		t = HTML.Table(header_row= HTML.TableRow(["","m64_bmks","m64_apps","m32_bmks","m32_apps","mx32_bmks","mx32_apps"], bgcolor='LightGrey'))
	else:
		t = HTML.Table(header_row= HTML.TableRow(["","m64_bmks","m64_apps","m32_bmks","m32_apps"], bgcolor='LightGrey'))

	temp=[]
	for i in range(0,len(table_types)):
		temp=[]
		if (m32_apps[i] == 0):
			m32_apps[i] = "0"
		if (m64_apps[i] == 0):
			m64_apps[i] = "0"
		if (mx32_apps[i] == 0):
			mx32_apps[i] = "0"
		if (m32_bmks[i] == 0):
			m32_bmks[i] = "0"
		if (m64_bmks[i] == 0):
			m64_bmks[i] = "0"
		if (mx32_bmks[i] == 0):
			mx32_bmks[i] = "0"
		if (path[3]=="MAINLINE"):
			temp=[table_types[i],"<A HREF='#64 Bit Bmks "+table_types[i]+"'>"+str(m64_bmks[i])+"</A>","<A HREF='#64 Bit Apps "+table_types[i]+"'>"+str(m64_apps[i])+"</A>","<A HREF='#32 Bit Bmks "+table_types[i]+"'>"+str(m32_bmks[i])+"</A>","<A HREF='#32 Bit Apps "+table_types[i]+"'>"+str(m32_apps[i])+"</A>","<A HREF='#mx32 Bit Bmks "+table_types[i]+"'>"+str(mx32_bmks[i])+"</A>","<A HREF='#mx32 Bit Apps "+table_types[i]+"'>"+str(mx32_apps[i])+"</A>"]
		else:
			temp=[table_types[i],"<A HREF='#64 Bit Bmks "+table_types[i]+"'>"+str(m64_bmks[i])+"</A>","<A HREF='#64 Bit Apps "+table_types[i]+"'>"+str(m64_apps[i])+"</A>","<A HREF='#32 Bit Bmks "+table_types[i]+"'>"+str(m32_bmks[i])+"</A>","<A HREF='#32 Bit Apps "+table_types[i]+"'>"+str(m32_apps[i])+"</A>"]
		t.rows.append(temp)
	temp=["Run_ids"] + run_ids
	t.rows.append(temp)		
	print t
	print "\n"	
	return count

def jira_ticket_id_list():
	file_object  = open('get_jira_id.txt','r')
	jira_ticket_id={}
	# print file_object.readline()
	for line in file_object: 
		a=line
		b=a.split(':')
		for i in range(0,len(b[2].split(','))):
			c=[b[1],b[2].split(',')[i]]
			jira_ticket_id['_'.join(c).split()[0]] = b[0]
		
	return jira_ticket_id
	
######################################################################################################################	
#Connecting to a Database:
####################################################################
con=MySQLdb.connect(db='aqidb',user='qa',passwd='test123')
####################################################################

#Generating JIRA Ticket List:
####################################################################
get_jira_ticket_id = {}
get_jira_ticket_id = jira_ticket_id_list()
####################################################################

# For count.
######################################################################################################
count_all(jobids_compilerRev(path[1])["64_bmks"],jobids_compilerRev(path[2])["64_bmks"])
count_all(jobids_compilerRev(path[1])["64_apps"],jobids_compilerRev(path[2])["64_apps"])
count_all(jobids_compilerRev(path[1])["32_bmks"],jobids_compilerRev(path[2])["32_bmks"])
count_all(jobids_compilerRev(path[1])["32_apps"],jobids_compilerRev(path[2])["32_apps"])

if (path[3]=="MAINLINE"):
	count_all(jobids_compilerRev(path[1])["mx32_bmks"],jobids_compilerRev(path[2])["mx32_bmks"])
	count_all(jobids_compilerRev(path[1])["mx32_apps"],jobids_compilerRev(path[2])["mx32_apps"])

if (path[3]=="MAINLINE"):	
	m64_bmks = [Regressions_count[0],Progressions_count[0],Known_issues_count[0],New_benchmarks_count[0],Missing_benchmarks_count[0]]
	m64_apps = [Regressions_count[1],Progressions_count[1],Known_issues_count[1],New_benchmarks_count[1],Missing_benchmarks_count[1]]
	m32_bmks = [Regressions_count[2],Progressions_count[2],Known_issues_count[2],New_benchmarks_count[2],Missing_benchmarks_count[2]]
	m32_apps = [Regressions_count[3],Progressions_count[3],Known_issues_count[3],New_benchmarks_count[3],Missing_benchmarks_count[3]]
	mx32_bmks = [Regressions_count[4],Progressions_count[4],Known_issues_count[4],New_benchmarks_count[4],Missing_benchmarks_count[4]]
	mx32_apps = [Regressions_count[5],Progressions_count[5],Known_issues_count[5],New_benchmarks_count[5],Missing_benchmarks_count[5]]

	run_ids = [jobids_compilerRev(path[1])["32_apps"][0],jobids_compilerRev(path[1])["64_apps"][0],jobids_compilerRev(path[1])["mx32_apps"][0],jobids_compilerRev(path[1])["32_bmks"][0],jobids_compilerRev(path[1])["64_bmks"][0],jobids_compilerRev(path[1])["mx32_bmks"][0]]

else:
	m64_bmks = [Regressions_count[0],Progressions_count[0],Known_issues_count[0],New_benchmarks_count[0],Missing_benchmarks_count[0]]
	m64_apps = [Regressions_count[1],Progressions_count[1],Known_issues_count[1],New_benchmarks_count[1],Missing_benchmarks_count[1]]
	m32_bmks = [Regressions_count[2],Progressions_count[2],Known_issues_count[2],New_benchmarks_count[2],Missing_benchmarks_count[2]]
	m32_apps = [Regressions_count[3],Progressions_count[3],Known_issues_count[3],New_benchmarks_count[3],Missing_benchmarks_count[3]]
	mx32_bmks = [0,0,0,0,0]
	mx32_apps = [0,0,0,0,0]
	run_ids = [jobids_compilerRev(path[1])["32_apps"][0],jobids_compilerRev(path[1])["64_apps"][0],jobids_compilerRev(path[1])["32_bmks"][0],jobids_compilerRev(path[1])["64_bmks"][0]]

######################################################################################################
	
#Html
#####################################################################################################################
print "<A NAME='Top'>"
print "<h1><font color='Blue'><center><u>Report for AQI Functional testing for "+path[3]+"-BUILD-"+path[1]+"</u></center></font></h1>"
print "<h2><font color='Blue'><u>SUMMARY:</u></font></h2>"
print_summary_table_html(m32_apps,m64_apps,mx32_apps,m32_bmks,m64_bmks,mx32_bmks,run_ids)

if (path[3]=="MAINLINE"):	
	print """
	<p><font color='Red' size="3">Note:</font></p>
	<ul>
	  <li><font color='Black' size="2">This Report contains results (Regressions, Progressions, Known issues , New Benchmarks & Missing Benchmarks) for all (m32, m64 & mx32) apps & bmks.</font></li>
	  <li><font color='Black' size="2">Click on the above numbers present in the table to go to respective tables.</font></li>
	  <li><font color='Black' size="2">Above is the comparison between """+path[3]+"""-BUILD-"""+path[1]+""" with """+path[3]+"""-BUILD-"""+path[2]+""".</font></li>
	  <li><font color='Black' size="2">Known issues are failed issues which are common in both build's.</font></li>
	</ul>"""
else:
	print """
	<p><font color='Red' size="3">Note:</font></p>
	<ul>
	  <li><font color='Black' size="2">This Report contains results (Regressions, Progressions, Known issues , New Benchmarks & Missing Benchmarks) for all (m32 & m64) apps & bmks.</font></li>
	  <li><font color='Black' size="2">Click on the above numbers present in the table to go to respective tables.</font></li>
	  <li><font color='Black' size="2">Above is the comparison between """+path[3]+"""-BUILD-"""+path[1]+""" with """+path[3]+"""-BUILD-"""+path[2]+""".</font></li>
	  <li><font color='Black' size="2">Known issues are failed issues which are common in both build's.</font></li>
	</ul>"""
#M64 Bit Bmks

print "<A NAME='64 Bit Bmks'>"

print "<h2><font color='DarkGreen'><u>Benchmarks tested with -m64:</u></font></h2>"	

# print "<p><font color='DarkMagenta'>Log Path : "+db_log_path(jobids_compilerRev(path[1])["64_bmks"])+"/*Runid*</font></p>"

print "<A NAME='64 Bit Bmks Regressions'>"
m64_bmks_regression_count = regression_html(jobids_compilerRev(path[1])["64_bmks"],jobids_compilerRev1(path[2])["64_bmks"],"64_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Bmks Progressions'>"
m64_bmks_progression_count = progressions_html(jobids_compilerRev(path[1])["64_bmks"],jobids_compilerRev1(path[2])["64_bmks"],"64_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Bmks Known issues'>"
m64_bmks_known_issues_count = known_issues_html(jobids_compilerRev(path[1])["64_bmks"],jobids_compilerRev1(path[2])["64_bmks"],"64_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Bmks New Benchmarks'>"
m64_bmks_new_apps_count = new_benchmarks_html(jobids_compilerRev(path[1])["64_bmks"],jobids_compilerRev1(path[2])["64_bmks"],"64_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Bmks Missing Benchmarks'>"
m64_bmks_missing_apps_count = missing_benchmarks_html(jobids_compilerRev(path[1])["64_bmks"],jobids_compilerRev1(path[2])["64_bmks"],"64_bmks")

print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

#M64 Bit Apps

print "<A NAME='64 Bit Apps'>"

print "<h2><font color='DarkGreen'><u>Apps tested with -m64:</u></font></h2>"	

# print "<p><font color='DarkMagenta'>Log Path : "+db_log_path(jobids_compilerRev(path[1])["64_apps"])+"/*Runid*</font></p>"

print "<A NAME='64 Bit Apps Regressions'>"
m64_apps_regression_count = regression_html(jobids_compilerRev(path[1])["64_apps"],jobids_compilerRev1(path[2])["64_apps"],"64_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Apps Progressions'>"
m64_apps_progression_count = progressions_html(jobids_compilerRev(path[1])["64_apps"],jobids_compilerRev1(path[2])["64_apps"],"64_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Apps Known issues'>"
m64_apps_known_issues_count = known_issues_html(jobids_compilerRev(path[1])["64_apps"],jobids_compilerRev1(path[2])["64_apps"],"64_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Apps New Benchmarks'>"
m64_apps_new_apps_count = new_benchmarks_html(jobids_compilerRev(path[1])["64_apps"],jobids_compilerRev1(path[2])["64_apps"],"64_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='64 Bit Apps Missing Benchmarks'>"
m64_apps_missing_apps_count = missing_benchmarks_html(jobids_compilerRev(path[1])["64_apps"],jobids_compilerRev1(path[2])["64_apps"],"64_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

#M32 Bit Bmks

print "<A NAME='32 Bit Bmks'>"

print "<h2><font color='DarkGreen'><u>Benchmarks tested with -m32:</u></font></h2>"	

# print "<p><font color='DarkMagenta'>Log Path : "+db_log_path(jobids_compilerRev(path[1])["32_bmks"])+"/*Runid*</font></p>"

print "<A NAME='32 Bit Bmks Regressions'>"	
m32_bmks_regression_count = regression_html(jobids_compilerRev(path[1])["32_bmks"],jobids_compilerRev1(path[2])["32_bmks"],"32_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Bmks Progressions'>"
m32_bmks_progression_count = progressions_html(jobids_compilerRev(path[1])["32_bmks"],jobids_compilerRev1(path[2])["32_bmks"],"32_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Bmks Known issues'>"
m32_bmks_known_issues_count = known_issues_html(jobids_compilerRev(path[1])["32_bmks"],jobids_compilerRev1(path[2])["32_bmks"],"32_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Bmks New Benchmarks'>"
m32_bmks_new_apps_count = new_benchmarks_html(jobids_compilerRev(path[1])["32_bmks"],jobids_compilerRev1(path[2])["32_bmks"],"32_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Bmks Missing Benchmarks'>"
m32_bmks_missing_apps_count = missing_benchmarks_html(jobids_compilerRev(path[1])["32_bmks"],jobids_compilerRev1(path[2])["32_bmks"],"32_bmks")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

#M32 Bit Apps

print "<h2><font color='DarkGreen'><u>Apps tested with -m32:</u></font></h2>"
print "<A NAME='32 Bit Apps'>"

# print "<p><font color='DarkMagenta'>Log Path : "+db_log_path(jobids_compilerRev(path[1])["32_apps"])+"/*Runid*</font></p>"

print "<A NAME='32 Bit Apps Regressions'>"
	
m32_apps_regression_count = regression_html(jobids_compilerRev(path[1])["32_apps"],jobids_compilerRev1(path[2])["32_apps"],"32_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Apps Progressions'>"
		
m32_apps_progression_count = progressions_html(jobids_compilerRev(path[1])["32_apps"],jobids_compilerRev1(path[2])["32_apps"],"32_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Apps Known issues'>"

m32_apps_known_issues_count = known_issues_html(jobids_compilerRev(path[1])["32_apps"],jobids_compilerRev1(path[2])["32_apps"],"32_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Apps New Benchmarks'>"
	
m32_apps_new_apps_count = new_benchmarks_html(jobids_compilerRev(path[1])["32_apps"],jobids_compilerRev1(path[2])["32_apps"],"32_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

print "<A NAME='32 Bit Apps Missing Benchmarks'>"

m32_apps_missing_apps_count = missing_benchmarks_html(jobids_compilerRev(path[1])["32_apps"],jobids_compilerRev1(path[2])["32_apps"],"32_apps")
print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"



if (path[3]=="MAINLINE"):
		
	#MX32 Bit Bmks
	
	print "<A NAME='MX32 Bit Bmks'>"
	
	print "<h2><font color='DarkGreen'><u>Benchmarks tested with -mx32:</u></font></h2>"	
	
	# print "<p><font color='DarkMagenta'>Log Path : "+db_log_path(jobids_compilerRev(path[1])["mx32_bmks"])+"/*Runid*</font></p>"
	
	print "<A NAME='mx32 Bit Bmks Regressions'>"
	mx32_bmks_regression_count = regression_html(jobids_compilerRev(path[1])["mx32_bmks"],jobids_compilerRev1(path[2])["mx32_bmks"],"mx32_bmks")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Bmks Progressions'>"
	mx32_bmks_progression_count = progressions_html(jobids_compilerRev(path[1])["mx32_bmks"],jobids_compilerRev1(path[2])["mx32_bmks"],"mx32_bmks")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Bmks Known issues'>"
	mx32_bmks_known_issues_count = known_issues_html(jobids_compilerRev(path[1])["mx32_bmks"],jobids_compilerRev1(path[2])["mx32_bmks"],"mx32_bmks")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Bmks New Benchmarks'>"
	mx32_bmks_new_apps_count = new_benchmarks_html(jobids_compilerRev(path[1])["mx32_bmks"],jobids_compilerRev1(path[2])["mx32_bmks"],"mx32_bmks")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Bmks Missing Benchmarks'>"
	mx32_bmks_missing_apps_count = missing_benchmarks_html(jobids_compilerRev(path[1])["mx32_bmks"],jobids_compilerRev1(path[2])["mx32_bmks"],"mx32_bmks")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	#MX32 Bit Apps
	
	print "<A NAME='MX32 Bit Apps'>"
	
	print "<h2><font color='DarkGreen'><u>Apps tested with -mx32:</u></font></h2>"
	
	# print "<p><font color='DarkMagenta'>Log Path : "+db_log_path(jobids_compilerRev(path[1])["mx32_apps"])+"/*Runid*</font></p>"
	
	print "<A NAME='mx32 Bit Apps Regressions'>"
	mx32_apps_regression_count = regression_html(jobids_compilerRev(path[1])["mx32_apps"],jobids_compilerRev1(path[2])["mx32_apps"],"mx32_apps")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Apps Progressions'>"
	mx32_apps_progression_count = progressions_html(jobids_compilerRev(path[1])["mx32_apps"],jobids_compilerRev1(path[2])["mx32_apps"],"mx32_apps")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Apps Known issues'>"
	mx32_apps_known_issues_count = known_issues_html(jobids_compilerRev(path[1])["mx32_apps"],jobids_compilerRev1(path[2])["mx32_apps"],"mx32_apps")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

	print "<A NAME='mx32 Bit Apps New Benchmarks'>"
	mx32_apps_new_apps_count = new_benchmarks_html(jobids_compilerRev(path[1])["mx32_apps"],jobids_compilerRev1(path[2])["mx32_apps"],"mx32_apps")
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"
	
	print "<A NAME='mx32 Bit Apps Missing Benchmarks'>"
	mx32_apps_missing_apps_count = missing_benchmarks_html(jobids_compilerRev(path[1])["mx32_apps"],jobids_compilerRev1(path[2])["mx32_apps"],"mx32_apps")
	
	print "<A HREF='#Top'><font size='1'>Back to top</font></A>\n"

#####################################################################################################################
