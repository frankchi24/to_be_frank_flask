# -*- coding: utf-8 -*-
from sqlalchemy_mapping import posts, tags, tag
from sqlalchemy import and_, or_, asc, desc


def tag_to_list(tags_string):
	tags_list = tags_string.split()
	for tag in tags_list:
		print tag


