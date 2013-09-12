from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

'''
Custom filters must fail silently. Must register filters using register.filter(function_name_str, function).
Or can use decorator (@register.filter).
'''

@register.filter
def assign_id(name, counter): return str(name)+str(counter)

@register.filter
def get_value(dictionary, key): return dictionary.get(key)

@register.filter
def get_length(dictionary): 
	length = 0
	for key,val in dictionary.iteritems():
		length += len(val)
	return length

@register.filter
def rangefn(number): return range(1,number) + [number]

@register.filter
def pager(l, page_num): 
	start = 0 if (page_num-5) < 0 else (page_num-5)
	return l[start:page_num+5]

@register.filter
def format_time(timestamp):
	today = datetime.now()
	today = timezone.make_aware(today, timezone.get_default_timezone())
	if today == timestamp:
		return "just now"
	elif today.day == timestamp.day and today.month == timestamp.month and today.year == timestamp.year:
		return timestamp.time()
	elif today.year == timestamp.year and today.month == timestamp.month:
		return timestamp.strftime("%d %b")
	elif today.year == timestamp.year:
		return timestamp.strftime("%d %b")
	else:
		return timestamp.strftime("%d %b %Y")