import arcpy

#Set the administrative Database Connection
db = 'SA@GEODATAvDefault.sde'

#Set the version owner Database Connection
dbcv = "GIS@GEODATAvDefault.sde"

#Name the new version to be created
v = "GIS"

#set the username of a person that has ArcGIS desktop installed on the computer running this script- must have the connection file listed below 
user = "gisadmin" 

################## End of parameters ##################

try:
	# Set the workspace
	arcpy.env.workspace = "C:\\Users\\" + user + "\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\" + db

	#Administrative Database Connection
	dbc = 'Database Connections/' + db

	# Block new connections to the database.
	arcpy.AcceptConnections(dbc, False)
	print "in"

	# Disconnect all users from the database.
	arcpy.DisconnectUser(dbc, "ALL")
	print "disconnected"

	# Get a list of versions to pass into the ReconcileVersions tool.
	versionList = arcpy.ListVersions(dbc)
	print "versions listed"

	# Execute the ReconcileVersions tool.
	arcpy.ReconcileVersions_management(dbc, "ALL_VERSIONS", "sde.DEFAULT", versionList, "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION", "c:/temp/reconcilelog.txt")
	print "reconciled"
	
	# Run the compress tool. 
	arcpy.Compress_management(dbc)
	print "compressed"

	# Rebuild indexes and analyze the states and states_lineages system tables
	arcpy.RebuildIndexes_management(dbc, "SYSTEM")
	print "indexes rebuilt"

	# Analyze Datasets
	arcpy.AnalyzeDatasets_management(dbc, "SYSTEM", "", "ANALYZE_BASE", "ANALYZE_DELTA", "NO_ANALYZE_ARCHIVE")
	print "analyzed"

	# Allow the database to begin accepting connections again
	arcpy.AcceptConnections(dbc, True)
	print "connections back"

	# Create the new version.
	arcpy.CreateVersion_management("Database Connections/" + dbcv, "sde.DEFAULT", v, "PUBLIC")
	communication = "Good to go."
except:
	communication = (arcpy.GetMessages())
	
	# Allow the database to begin accepting connections again
	arcpy.AcceptConnections(dbc, True)
	print "connections back"
	
#Email when finished. Useful for scheduled scripts that don't output print commands
import smtplib, time, datetime

#Get the current time
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

sender = 'gis@dublin.oh.us'
receivers = ['gis@dublin.oh.us']

message = """From: From GIS <gis@dublin.oh.us>
To: To GIS <gis@dublin.oh.us>
Subject: RPC

The Geodatabase """ + db + """ was reconciled, posted and compressed at  """ + st + """

""" + communication + """ 

Thank you and goodbye. Suckas"""

try:
   smtpObj = smtplib.SMTP('bounce.dublin.oh.us')
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except SMTPException:
   print "Error: unable to send email"
