#!/usr/bin/python

import os,cv2
import json

if __name__ == '__main__':

	''' load all the annotaitons: *.json '''
	json_dir = '/home/luo/imgAnnotation/annotation/XiaHeRoad/record001/'
	json_path = json_dir + 'annotation.json'
	json_file = open(json_path)
	annos = json.load(json_file)

	out_dir = '/home/luo/show'
	
	for anno in annos:
		im_dir = anno['dir']
		im_name = anno['name']
		im_path = os.path.join(im_dir,im_name)
		im = cv2.imread(im_path)

		bboxes = anno['bbox']
		categories = anno['category']
		complexities = anno['complexity']
		distances = anno['distance']
		lights = anno['light']
		occlusions = anno['occlusion']
		integritise = anno['integrity']

		for idx in range(len(bboxes)):
			if im_name.find('Camera_3') != -1:
				cv2.rectangle ( im , ( int(bboxes[idx][1]), int(bboxes[idx][0]) ), (int(bboxes[idx][3]),  int(bboxes[idx][2])) , (255,0,0) , 5 )
			else:
				cv2.rectangle ( im , ( int(bboxes[idx][0]), int(bboxes[idx][1]) ), (int(bboxes[idx][2]),  int(bboxes[idx][3])) , (255,0,0) , 5 )
			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText( im, '{:s} d:{:b} o:{:b} i:{:b} l:{:b} '.format(categories[idx],distances[idx],occlusions[idx],integritise[idx],lights[idx]), (int(bboxes[idx][0]), int(bboxes[idx][1]) + 30 ), font, 1, (0,0,255), 2 ,1 )
		out_im_path = os.path.join(out_dir,im_name)
		cv2.imwrite(out_im_path.replace('.jpg','_b.jpg'),im)
