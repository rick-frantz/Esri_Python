# Import system modules
import arcpy
print "arcpy loaded"

#Set the version owner Database Connection
db = "GIS@GEODATAvDefault.sde"

#set the username of a person that has ArcGIS desktop installed on the computer running this script- must have the connection file listed below 
user = "gisadmin"

# Set the administrative workspace
arcpy.env.workspace = "C:\\Users\\" + user + "\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\" + db
arcpy.env.overwriteOutput = True
print "workspace loaded"

codeblock1 = """rec=0
def autoIncrement():
	global rec
	pStart ="""

codeblock2 = """
	pInterval = 1
	if (rec == 0):
		rec = pStart
	else:
		rec += pInterval
	return rec"""
	
fieldName = "FacilityID"
expression = "autoIncrement()"
communication = "Ready to start!"

print "entering try"
try:
	mapDoc = r'\\full path to mapdoc.mxd'
	mxd = arcpy.mapping.MapDocument(mapDoc)
	lyrs = arcpy.mapping.ListLayers(mxd)
	for lyr in lyrs:
		try:
			s1 = lyr.dataSource
			s2 = '\\'
			s3 = s1.rfind(s2)
			fc = s1[(s3)+ len(s2):]
			print "\n" + fc + " starting"
			
			#Make sure the FacilityID field exists
			if len(arcpy.ListFields(fc,fieldName)) > 0:
			
				# Make a layer from the feature class
				arcpy.MakeFeatureLayer_management(fc , "fcLayer")
				#print fc, "layer made"
				
				try:
					# Select Feature with max FacilityID
					arcpy.SelectLayerByAttribute_management("fcLayer", "NEW_SELECTION", "FacilityID = (SELECT MAX( CAST (FacilityID AS INTEGER)) FROM " + fc + ")")
					#print "Max FacilityID selected"
					
					# Assign variable to max FacilityID
					cursor = arcpy.SearchCursor("fcLayer", '')
					for row in cursor:
						maxfacID = (row.FacilityID)
						print "The maximum FacilityID for " + fc + " is " + maxfacID
						maxfacIDint = int(maxfacID) + 1
						#print "The next FacilityID will be ", maxfacIDint
					
					try:
						# Select Featuers with no FacilityID
						arcpy.SelectLayerByAttribute_management("fcLayer", "NEW_SELECTION", " [FacilityID] IS NULL ")
						arcpy.SelectLayerByAttribute_management ("fcLayer", "ADD_TO_SELECTION", " [FacilityID] = '' ")
						arcpy.SelectLayerByAttribute_management ("fcLayer", "ADD_TO_SELECTION", " [FacilityID] = '0' ")
						sr = int(arcpy.GetCount_management ("fcLayer").getOutput(0))
						print sr, "records selected in " + fc
						
						if sr > 0:
							codeblock= codeblock1 + str(maxfacIDint) + codeblock2
							
							# Execute CalculateField 
							arcpy.CalculateField_management("fcLayer", fieldName, expression, "PYTHON", codeblock)
							print "Blanks populated in " + fc
							communication = communication + "\nLayer " + fc + " had " + str(sr) + " records calculated."
						else:
							print "None selected in " + fc
							communication = communication + "\nLayer " + fc + " is good to go."
					except:
						print "Couldn't select or calculate any records in " + fc
						communication = communication + "\nLayer " + fc + " didn't get any new FacilityIDs but may need them."
				except:
					print "Max FacilityID not found in " + fc
					communication = communication + "\nLayer " + fc + " couldn't determine the maximum existing FacilityID."
			else:
				print "No FacilityID, Dude in " + fc
				communication = communication + "\nLayer " + fc + " doesn't have a FacilityID field."
		except:
			print "Fail in the layer portion of " + fc
			communication = communication + "\nSomething went TERRIBLY wrong with the " + fc + " layer."
			#print fc
			#print arcpy.GetMessages()
	print "All done boss."

except:
	communication = communication + "\n" + str(arcpy.GetMessages())
	
#Email when finished. Useful for scheduled scripts that don't output print commands
import smtplib, time, datetime

#Get the current time
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

sender = 'gis@dublin.oh.us'
receivers = ['gis@dublin.oh.us']

message = """From: From GIS <gis@dublin.oh.us>
To: To GIS <gis@dublin.oh.us>
Subject: FacilityID's calculated

FacilityIDS in """ + db + """ were calculated at  """ + st + """

""" + communication + """ 

Thank you and goodbye. Chumps"""

try:
   smtpObj = smtplib.SMTP('bounce.dublin.oh.us')
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except SMTPException:
   print "Error: unable to send email"
