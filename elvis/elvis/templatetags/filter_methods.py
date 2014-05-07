from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

NUMBERS = {
    '0' : '',
    '1' : 'one',
    '2' : 'two',
    '3' : 'three',
    '4' : 'four',
    '5' : 'five',
    '6' : 'six',
    '7' : 'seven',
    '8' : 'eight',
    '9' : 'nine',
    '10' : 'ten',
    '11' : 'eleven',
    '12' : 'twelve',
    '13' : 'thirteen',
    '14' : 'fourteen',
    '15' : 'fifteen',
    '16' : 'sixteen',
    '17' : 'seventeen',
    '18' : 'eighteen',
    '19' : 'nineteen',
    '20' : 'twenty',
    '21' : 'twenty-one',
    '22' : 'twenty-two',
    '23' : 'twenty-three',
    '24' : 'twenty-four',
    '25' : 'twenty-five',
    '26' : 'twenty-six',
    '27' : 'twenty-seven',
    '28' : 'twenty-eight',
    '29' : 'twenty-nine',
    '30' : 'thirty'
}

'''
Custom filters must fail silently. Must register filters using register.filter(function_name_str, function).
Or can use decorator (@register.filter).
'''

@register.filter
def numToWord(number): 
	num = str(number)
	try:
		return NUMBERS[num]
	except:
		return number

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
def get_field(model, fieldname):
	if fieldname:
		if '-' in fieldname:
			fieldname = fieldname.replace('-', '')
		field = getattr(model, fieldname)
		if type(field) == date or type(field) == datetime:
			if fieldname == "date_of_composition" or fieldname == "birth_date" or fieldname == "death_date":
				return format_composition(field)
			else:
				return format_timestamp(field)
		return field

@register.filter
def rangefn(number): return range(1,number) + [number]

@register.filter
def pager(l, page_num): 
    start = 0 if (page_num-5) < 0 else (page_num-5)
    return l[start:page_num+5]

# @register.filter
# def format_time(timestamp):
#     today = datetime.now()
#     today = timezone.make_aware(today, timezone.get_default_timezone())
#     if today == timestamp:
#         return "just now"
#     elif today.day == timestamp.day and today.month == timestamp.month and today.year == timestamp.year:
#         return timestamp.time()
#     elif today.year == timestamp.year and today.month == timestamp.month:
#         return timestamp.strftime("%d %b")
#     elif today.year == timestamp.year:
#         return timestamp.strftime("%d %b")
#     else:
#         return timestamp.strftime("%d %b %Y")