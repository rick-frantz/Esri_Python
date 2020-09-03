import arcpy, csv, os
geodb = 'DublinGoBag031620.gdb'
folder = 'G:\\GIS Data\\ArcSDE Exports'
arcpy.env.workspace = folder + '\\'+ geodb
print (arcpy.env.workspace)

header = ['Field Name','Field Type','Field Alias'] # insert other field names here

datasets = arcpy.ListDatasets(feature_type='feature')
datasets = [''] + datasets if datasets is not None else []
print("Found " + str(len(datasets)) + " feature classes")

for ds in datasets:
    for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
        path = os.path.join(arcpy.env.workspace, ds, fc)
        print(path)

        csvout = folder + '\\DublinSchemas\\GDBschema_'+fc+'.csv'
        with open(csvout, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=header, lineterminator='\n')
            writer.writeheader()

            fields = arcpy.ListFields(fc)
            fields_data = []
            for field in fields:
                writer.writerow({'Field Name':field.name, 'Field Type':field.type, 'Field Alias':field.aliasName}) # insert other field properties here

print("All done.")
