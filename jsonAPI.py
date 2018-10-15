import os.path
import json
import fileinput


class JSON_Tools():
		
	def dump_Data_To_File(self, json_file_path, **kwargs):
		# Converts a Python dictionary to JSON formatted data and writes it to file
		all_dicts = {}
		
		if kwargs != None:
			for key, value in kwargs.items():
				all_dicts[key] = value
		
			with open(json_file_path, 'w') as outfile:
				json.dump(all_dicts, outfile)
				outfile.close()
				
	def dump_Data_To_string(self, **kwargs):
		# Converts a Python dictionary to JSON formatted data and writes it to file
		all_dicts = {}
		
		if kwargs != None:
			for key, value in kwargs.items():
				all_dicts[key] = value
		
		return json.dumps(all_dicts)
		
# 			with open(json_file_path, 'w') as outfile:
# 				json.dump(all_dicts, outfile)
# 				outfile.close()
				
	def Load_Data(self, json_file_path):
		# Converts a JSON formatted file to Python data structure
		with open(json_file_path) as json_data:
			return json.load(json_data)
		
	def Load_Data_From_String(self, json_string):
		# Converts a JSON string to Python data structure
		
		return json.loads(json_string)