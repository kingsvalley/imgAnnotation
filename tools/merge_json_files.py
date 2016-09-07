#!/usr/bin/python

'''
	this program merges serval annotation json files into a single json file
'''
import os
import json

if __name__ == '__main__':
	
	# first read the results
	json_annotated_file = []
	json_dir = '/home/luo/imgAnnotation/annotation/XiaHeRoad/record001/'
	#json_annotated_file.append ('/home/luo/data/XiaHeRoad/WhiteBalance001/camera_1.annotation.json')
	#json_annotated_file.append ('/home/luo/data/XiaHeRoad/WhiteBalance001/camera_1.annotation.json')
	#json_annotated_file.append ('/home/luo/data/XiaHeRoad/WhiteBalance001/camera_2.annotation.json')
	#json_annotated_file.append ('/home/luo/data/XiaHeRoad/WhiteBalance001/camera_3.annotation.json')
	json_annotated_file.append (json_dir + 'camera_1.annotation.json')
	json_annotated_file.append (json_dir + 'camera_2.annotation.json')
	json_annotated_file.append (json_dir + 'camera_3.annotation.json')
	json_annotated_file.append (json_dir + 'camera_4.annotation.json')
	out_path = json_dir + 'annotation.json'

	annotated_list = []
	for json_file in json_annotated_file :
		f = open(json_file, 'r')
		annotated_data = json.load(f)
		annotated_list.extend(annotated_data)
	
	count = 0
	for anno in annotated_list:
		anno['id'] = []
		for bbox in anno['bbox']:
			anno['id'].append( count )
			count = count + 1

	## for camera 3 we need rotate the bbbox
	print 'Note! we rotate the bbox for the camera 3 \n'
	for anno in annotated_list:
		if anno['dir'].find('Camera 3') == -1 :
			continue 
		for bbox in anno['bbox']:
			tmp = bbox[0]
			bbox[0] = bbox[1]
			bbox[1] = tmp

			tmp = bbox[2]
			bbox[2] = bbox[3]
			bbox[3] = tmp
			


	target = open( out_path , 'w' )
	json_str = json.dumps(annotated_list , default=lambda o: o.__dict__, sort_keys=True, indent = 4 )
	print json_str
	
	target.write(json_str)

