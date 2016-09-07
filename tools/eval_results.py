#!/usr/bin/python

'''
	this program make statistics on the detection resutls 
	IoU criteron is used and the output file is send to the matlab 
	program to draw the ROC curves !
'''
import os, cv2
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
	json_dir =  '/home/luo/imgAnnotation/annotation/XiaHeRoad/record001/'
	annotated_json_file = json_dir + 'annotation.json'
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
	distance_bench_units = []
	integrity_bench_units = []
	light_bench_units = []
	occlusion_bench_units = []

	complexity_bench_units =[] 
	id_bench_units = []
	detected_bbox_units = []
	bench_bbox_units = []

	for bbox in bbox_units:

		# skip these categories not for current evaluations
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
		
		bench_bbox_units.extend(annotation['bbox'])
		detected_bbox_units.extend([bbox.bbox for i in iou])
		name_units.extend([bbox.name for i in iou])
		score_units.extend([bbox.score for i in iou])
		category_units.extend([bbox.category for i in iou])
		category_bench_units.extend(annotation['category'])
		complexity_bench_units.extend(annotation['complexity'])
		occlusion_bench_units.extend(annotation['occlusion'])
		light_bench_units.extend(annotation['light'])
		integrity_bench_units.extend(annotation['integrity'])
		distance_bench_units.extend(annotation['distance'])
		id_bench_units.extend([len(annotation['id']) for i in range(len(annotation['id']))])

	# format the results and output to the matlab interface     
	target = open('/home/luo/imgAnnotation/tools/drawROC/results/results.txt', 'w')
	target_for_img = open('results.txt','w')

	img_annotations = dict()

	for name in im_in_benchmark:
		
		img_annotations[name] = []
		
		indices = []

		# compute the range of bbox idx belongs to each image
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
		true_positive_dict = dict()
		
		#print gap
		for idx in range(len(indices)):
			#print idx 
			indice = indices[idx]
			#print score_units[indice]
			#print "iou {:f} c: {:s}".format(iou_units[indice],category_bench_units[indice])

			count = (idx+1) % gap
				
			if iou_units[indice] > 0.5 and category_bench_units[indice] in CLASS_EVAL:
				# not a false postive 
				is_false_positive = False

				# not a negative
				index = count-1
				if count == 0 :
					index = gap - 1
				is_false_negatives[index] = True

				if count not in true_positive_dict:
					true_positive_dict[count] = []
					true_positive_dict[count].append(score_units[indice])
					true_positive_dict[count].append(iou_units[indice])
					true_positive_dict[count].append(indice)
				else:
					if true_positive_dict[count][0] < score_units[indice]:
						true_positive_dict[count][0] = score_units[indice]
						true_positive_dict[count][1] = iou_units[indice]
						true_positive_dict[count][2] = indice
			
			if count == 0 :
				if is_false_positive:
					target.write('0 {:f} 0\n'.format(score_units[indice]))
					print('{:s} 0 {:f} 0'.format(name,score_units[indice]))
					bbox_show = detected_bbox_units[indice];
					bbox_show.append(0)
					img_annotations[name].append(bbox_show)
				is_false_positive = True


		for key in true_positive_dict.keys():
			indice = true_positive_dict[key][2]
			if light_bench_units[indice] or occlusion_bench_units[indice] or integrity_bench_units[indice] or  distance_bench_units[indice]:
				continue
			
			target.write('1 {:f} {:f}\n'.format(true_positive_dict[key][0],true_positive_dict[key][1]))
			print '{:s} 1 {:f} {:f}'.format(name,true_positive_dict[key][0],true_positive_dict[key][1])
			bbox_show = detected_bbox_units[indice];
			bbox_show.append(1)
			img_annotations[name].append(bbox_show)

		for i in range(len(is_false_negatives)):
				
			if  light_bench_units[indices[i]] or  occlusion_bench_units[indices[i]] or integrity_bench_units[indices[i]] or  distance_bench_units[indices[i]]:
				continue

			indicator = is_false_negatives[i]
			if category_bench_units[indices[i]] not in CLASS_EVAL:
				continue
			if not indicator:
				target.write('1 0 0\n')
				print('{:s} 1 0 0'.format(name))
				bbox_show = bench_bbox_units[indices[i]];
				bbox_show.append(2)
				img_annotations[name].append(bbox_show)

	target.close()
	json_str = json.dumps(img_annotations, default=lambda o: o.__dict__, sort_keys=True, indent = 4)
	target_for_img.write(json_str)
	target_for_img.close()


	for key in img_annotations:
		annotation = search_bbox_in_benchmark(annotations,key)
		im_dir = annotation['dir']
		im_path = os.path.join(im_dir,key)
		im = cv2.imread(im_path)
		font = cv2.FONT_HERSHEY_SIMPLEX
		for bbox in img_annotations[key]:
			if bbox[4] == 0 :
				cv2.putText( im, 'false_alarm', ( int(bbox[0]), int(bbox[1])+30 ), font, 1, (0,0,255), 2 ,1)
				cv2.rectangle ( im , ( int(bbox[0]), int(bbox[1]) ), (int(bbox[2]),  int(bbox[3])) , (255,0,0) , 5 )
			elif bbox[4] == 1:
				cv2.rectangle ( im , ( int(bbox[0]), int(bbox[1]) ), (int(bbox[2]),  int(bbox[3])) , (255,255,0) , 5 )
			else:
				cv2.putText( im, 'miss', ( int(bbox[0]), int(bbox[1])+30 ), font, 1, (0,0,255), 2 ,1)
				cv2.rectangle ( im , ( int(bbox[0]), int(bbox[1]) ), (int(bbox[2]),  int(bbox[3])) , (255,0,255) , 5 )

		out_dir = '/home/luo/exp'
		cv2.imwrite(os.path.join(out_dir,key)+".jpg",im)

