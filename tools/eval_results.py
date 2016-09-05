#!/usr/bin/python

'''
	luo
	this program make statistics on the detection resutls 
	IoU criteron is used and the output file is send to the matlab 
	program to draw the ROC curves !
'''
import os
import json

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
		   'bottle', 'bus', 'car', 'cat', 'chair',
		   'cow', 'diningtable', 'dog', 'horse',
		   'motorbike', 'person', 'pottedplant'
		   'sheep', 'sofa', 'train', 'tvmonitor')

CLASS_EVAL = {'car'}

class BBoxUnit :
	dir = ""
	name = ""
	bbox = []
	category = ""
	iou = 0.0
	score = 0.0

	def __init__(self, bbox, category, iou, score, dir, name):
		self.bbox = bbox
		self.category = category
		self.iou = iou
		self.score = score
		self.dir = dir
		self.name = name

def search_bbox_in_benchmark(annotations,im_name):
	im_database = dict( [ (annotations[i]['name'],annotations[i]) for i in range(len(annotations))])
	if im_name in im_database:
		return im_database[im_name]
	else:
		print 'cannot find the benchmark image ' + im_name 
		exit()

def compute_IoU(GTBox, RefBox):
	x1 = RefBox[0]
	y1 = RefBox[1]
	width1 = RefBox[2]-RefBox[0]
	height1 = RefBox[3]-RefBox[1]

	ious = []
	for box in GTBox :
		x2 = int(box[0])
		y2 = int(box[1])
		width2 = int(box[2]) - int(box[0])
		height2 = int(box[3]) - int(box[1])
		
		endx = max(x1+width1, x2+width2)
		startx = min(x1,x2)
		width = width1+width2-(endx-startx)

		endy = max(y1+height1,y2+height2)
		starty = min(y1,y2)
		height = height1 + height2 - (endy-starty)

		ratio = 0.0
		if width <= 0 or height <= 0:
			ratio = 0 
		else:
			Area = width * height 
			Area1 = width1 * height1 
			Area2 = width2 * height2
			ratio = Area * 1./(Area1 + Area2 - Area)
		ious.append(ratio)

	return ious

if __name__ == '__main__':
	
	# first read the benchmark annotations
	annotated_json_file = '/home/luo/data/XiaHeRoad/WhiteBalance001/annotation.json'
	annotations = json.load(open(annotated_json_file,'r'))
	
	# first read all the detected bboxes
	im_detect_dir = '/home/luo/exp'
	
	# search detected files
	detect_list = []
	for root, dirs, files in os.walk(im_detect_dir):
		for f in files:
			detect_file = os.path.join(root,f)
			if os.path.isfile(detect_file) and os.path.splitext(detect_file)[1] == '.txt':
				detect_list.append(detect_file)
	
	# filter all detected boxes with images in the benchmark 
	bbox_units = [] 
	im_in_benchmark = [annotations[i]['name'] for i in range(len(annotations))]
	for detect_file in detect_list:
		f = open(detect_file, 'r')
		dir,name = os.path.split(detect_file)
		name = name.replace('.txt','.jpg')
		#whehter the detected image is in the benchmark 
		if name not in im_in_benchmark:
			continue

		lines = f.readlines()
		for line in lines:
			bbox_unit = BBoxUnit([],"",0.0,0.0,dir,name)
			words = line.split(' ')
			bbox_unit.bbox.append((int)(words[0]))
			bbox_unit.bbox.append((int)(words[1]))
			bbox_unit.bbox.append((int)(words[2]))
			bbox_unit.bbox.append((int)(words[3]))
			bbox_unit.score = float(words[4])
			bbox_unit.category = CLASSES[int(words[5])]
			bbox_units.append(bbox_unit)
	
	# compute IoU for each bbox
	iou_units = [] 		# store all the detected bbox results
	score_units = [] 	# store all the detected scores 
	category_units = [] # store all the detected category
	name_units = []     # store all the image name for each unit
	category_bench_units=[] # store the true category label for each unit
	complexity_bench_units =[] 
	id_bench_units = []

	for bbox in bbox_units:
		if bbox.category not in CLASS_EVAL:
			continue
		# search the corresponding box
		annotation = search_bbox_in_benchmark(annotations,bbox.name)
		# compute the iou regions
		GTBox = []
		for i in range(len(annotation['bbox'])):
			GTBox.append(annotation['bbox'][i])
		iou = compute_IoU( GTBox, bbox.bbox )
		

		iou_units.extend(iou)
		name_units.extend([bbox.name for i in iou])
		score_units.extend([bbox.score for i in iou])
		category_units.extend([bbox.category for i in iou])
		category_bench_units.extend(annotation['category'])
		complexity_bench_units.extend(annotation['complexity'])
		id_bench_units.extend([len(annotation['id']) for i in range(len(annotation['id']))])

	# format the results and output to the matlab interface     
	target = open('results.txt', 'w')
	
	for name in im_in_benchmark:
		indices = []
		for idx in range(len(name_units)):
			if name_units[idx] == name:
				indices.append(idx)
		if len(indices) <= 0:
			continue

		start_dix = indices[0]
		stop_dix = indices[-1]
			
		gap = id_bench_units[start_dix]
		is_false_negatives = [ False for i in range(gap) ]
		is_false_positive = True

		
		count = 0 
		for indice in indices:

			if count < gap :
				if iou_units[indice] > 0.5 and category_bench_units[indice] in CLASS_EVAL:
						is_false_positive = False
						target.write('1 {:f} {:f}\n'.format(score_units[indice],iou_units[indice]))
						print('{:s} 1 {:f} {:f}'.format(name,score_units[indice],iou_units[indice]))
						is_false_negatives[count] = True
				count = count + 1
			else:
				if is_false_positive:
					target.write('0 {:f} 0'.format(score_units[indice]))
					print('{:s} 0 {:f} 0'.format(name,score_units[indice]))
				is_false_positive = True
				count = 0 

		for i in range(len(is_false_negatives)):
			if category_bench_units[i] not in CLASS_EVAL:
				continue
			indicator = is_false_negatives[i]
			if not indicator:
				target.write('1 0 0\n')
				print('{:s} 1 0 0'.format(name))

	target.close()

