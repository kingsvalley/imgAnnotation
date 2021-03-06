#!/usr/bin/python

'''
	this program transform the annotation boxes aqcuired 
	by the imgAnnotation tool into a json format
'''
import os, sys
import json
import cv2
from PIL import Image

class BBoxUnix:
	id = 0
	dir = []
	name = []
	bbox = []
	category = []
	complexity = []
	light = []
	occlusion = []
	integrity = []
	distance = []
	
	def __init__(self, bbox, category, complexity, dir, name):
		self.id = 0
		self.bbox = bbox 
		self.category = category
		self.complexity = complexity
		self.dir = dir 
		self.name = name
		self.distance =[]
		self.occlusion = []
		self.integrity = []
		self.light = []


if __name__ == '__main__' :	
	
	if len(sys.argv) < 2:
		print 'input the annotation file : ***.annotation'
		sys.exit()
	
	''' read the annotation files '''
	# annotation file path
	annotation_file = sys.argv[1]
	print annotation_file
	#annotation_file = '/home/luo/imgAnnotation/annotation/XiaHeRoad/record001/camera_3.annotation'
	im_root_dir = '/home/luo/data/XiaHeRoad'
	f = open(annotation_file , "r") 
	lines = f.read().split('\n')
	annotated_objects = [] 
	for idx in range(len(lines)):
		if lines[idx].startswith('########## NEW FILE ##########'):
			path = lines[idx+1]
			dir, name = os.path.split(path[len('file :'):])
			dir = dir.replace('F:/Xiamen-2016-8-23/Data/XiaHeRoad',im_root_dir)
			name = name.replace('\r','')

			''' read image to recitify the height and width '''
			im = Image.open(os.path.join(dir,name))
			im_width,im_height = im.size

			bbox_unit = BBoxUnix([],[],[],dir,name)
			idx = idx+1
			count = 0
			while idx< len(lines)-1 and not lines[idx+1].startswith('########## NEW FILE ##########'):
				line = lines[idx]
				bbox = []
				category = []
				occlusion = False
				distance = False 
				light = False 
				integrity = False 


				if line.startswith('bbox'):
					bbox_str = line[6:]
					bbox = [int(float(i)) for i in bbox_str.split(',')]
					if bbox[0] <= 0 : 
						bbox[0] = 1
					if bbox[1] <= 0 :
						bbox[1] = 1

					bbox[2] = bbox[2] + bbox[0] 
					bbox[3] = bbox[3] + bbox[1]
					if bbox[2] > im_width:
						bbox[2] = im_width
					if bbox[3] > im_height:
						bbox[3] = im_height
					
					idx = idx + 1
					line = lines[idx]
					if line.startswith('category'):
						category = line[len('category: '):].strip()
						if category == '':
							category = 'car'
						idx = idx + 1
					else :
						category = 'car'
					
					line = lines[idx]
					if line.startswith('complexity: '):
						complexity = line[len('complexity: '):].strip()
						idx = idx + 1 
					else :
						complexity = '1'
						
					line = lines[idx]
					if line.startswith('distance: '):
						distance = True
						idx = idx + 1
					else :
						distance = False
					
					line = lines[idx]
					if line.startswith('integrity: '):
						integrity = True
						idx = idx + 1 
					else :
						integrity = False
					
					line = lines[idx]
					if line.startswith('light: '):
						light = True
						idx = idx + 1 
					else :
						light = False

					line = lines[idx]
					if line.startswith('occlusion: '):
						occlusion = True
						idx = idx + 1 
					else :
						occlusion = False

					bbox_unit.bbox.append(bbox)
					bbox_unit.category.append(category)
					bbox_unit.complexity.append(complexity)
					bbox_unit.occlusion.append(occlusion)
					bbox_unit.light.append(light)
					bbox_unit.integrity.append(integrity)
					bbox_unit.distance.append(distance)

				else:
					idx = idx + 1
			# end while
			annotated_objects.append(bbox_unit)
		#end if
	#end for
	jsonStr = json.dumps(annotated_objects, default=lambda o: o.__dict__, sort_keys=True, indent = 4 )
	print jsonStr

	out_json_path = annotation_file + '.json'
	target = open(out_json_path,'w')
	target.write(jsonStr)



