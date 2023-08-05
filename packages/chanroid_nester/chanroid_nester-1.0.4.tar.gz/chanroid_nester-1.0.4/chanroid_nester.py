# -*- coding:utf-8 -*-
import sys

def print_list(array, indent=False, numOfTabs=0, fh=sys.stdout):
	# array - 출력할 배열, numOfTabs - 들여쓰기 할 탭 수
	for item in array:
		if (isinstance(item, list)):
			print_list(item, indent, numOfTabs+1, fh)
		else:
			if indent:
				for tab in range(numOfTabs):
					print("\t", end='', file=fh)
			print(item)