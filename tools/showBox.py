#!/usr/bin/python

import os,cv2
import json

if __name__ == '__main__':

	''' load all the annotaitons: *.json '''
	json_path = '/home/luo/data/XiaHeRoad/WhiteBalance001/annotation.json'
	json_file = open(json_path)
	annos = json.load(json_file)

	out_dir = '/home/luo/benchshow'
	
	for anno in annos:
		im_dir = anno['dir']
		im_name = anno['name']
		im_path = os.path.join(im_dir,im_name)
		print im_name 
		im = cv2.imread(im_path)

		bboxes = anno['bbox']
		categories = anno['category']
		complexities = anno['complexity']

		if im_name.startswith("160823_053803259_Camera_3.jpg"):
			print len(bboxes)
		for idx in range(len(bboxes)):
			if im_name.startswith("160823_053803259_Camera_3.jpg"):
				print bboxes[idx]
			if im_name.find('Camera_3') != -1:
				cv2.rectangle ( im , ( int(bboxes[idx][1]), int(bboxes[idx][0]) ), (int(bboxes[idx][3]),  int(bboxes[idx][2])) , (255,0,0) , 5 )
			else:
				cv2.rectangle ( im , ( int(bboxes[idx][0]), int(bboxes[idx][1]) ), (int(bboxes[idx][2]),  int(bboxes[idx][3])) , (255,0,0) , 5 )
			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText( im, '{:s} c:{:s}'.format(categories[idx],complexities[idx]), (int(bboxes[idx][0]), int(bboxes[idx][1]) + 30 ), font, 1, (0,0,255), 2 ,1 )
		out_im_path = os.path.join(out_dir,im_name)
		cv2.imwrite(out_im_path,im)
