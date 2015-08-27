'''
Generic helper methods for views 
'''
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mass_mail

from elvis.models.tag import Tag
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.userprofile import UserProfile

from random import shuffle, randrange
from smtplib import SMTPException

RESULT_PER_PAGE = 25
RANDOM_RANGE = 10000    # Used for creating temporary username 

# Partition data into rows. Used for template organization
def partition(data, num_per_row):
    partitioned_data = []
    for x in range(0, len(data), num_per_row):
        partitioned_data.append(data[x:x+num_per_row])
    return partitioned_data


# Sort objects by value
def sort_objects(object_name, val):
    if val is None or val == "0" or val == "most":
        return object_name.objects.all()
    else:
        return object_name.objects.all().order_by(val)

# Utility method to paginate a query set 
def paginate(objects, GET, num=RESULT_PER_PAGE):
    paginator = Paginator(objects, num)
    page = GET.get("page")
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
    return object_list

# Return random userprofiles for display purposes 
def getRandomUsers(num=12):
    uprofs = [up for up in UserProfile.objects.all()]
    shuffle(uprofs)
    return uprofs[:num]

# Remove blank elements from list 
def removeBlanks(l): return [x for x in l if x != '']

'''
Tag helper stuff
'''

#TODO!!!!!: This will remove duplicates and return only one instance of tag, not list
def deduplicate(taglist): 
    try:
        return taglist[0]
    except IndexError:
        return None

# Retag with new_tag all pieces/movements that were tagged with old_tags 
def merge_tags(new_tag, old_tags):

    if new_tag == "New tag name":
        return

    tag_objs = [deduplicate(Tag.objects.filter(name=tag)) for tag in old_tags]
    if all(tag_objs):
        # Create a new tag
        new_tag_obj = Tag(name=new_tag)
        new_tag_obj.save()

        for tag in tag_objs:
            # Get pieces/movements tagged with the old id
            pieces = Piece.objects.filter(tags__id=tag.id)
            movements = Movement.objects.filter(tags__id=tag.id)

            # Tag pieces and movements with new tag 
            for piece in pieces.all():
                piece.tags.add(new_tag_obj)
                piece.save()
            for movement in movements.all():
                movement.tags.add(new_tag_obj)
                movement.save()

            # Delete old tag
            tag.delete()

    else:
        print("Some of old tags weren't found.")

# TODO: Check that old_tag exists 
# Tags everything that had old_tag with new_tags, then removes old_tag
def split_tags(old_tag, new_tags):
    if old_tag == "Existing tag name":
        return

    # Filter out names that might already exist
    existing = [tag.name for tag in Tag.objects.all()]
    replacements = [tag for tag in new_tags if tag not in existing]

    # Create new tag objects
    replacement_objects = []
    for replacement in replacements:
        t = Tag(name=replacement, approved=False)
        t.save()
        replacement_objects.append(t)

    # Get the old tag object and potentially dedup
    tag_obj = deduplicate(Tag.objects.filter(name=old_tag))

    # Find all pieces/movements that were tagged with it
    pieces = Piece.objects.filter(tags__id=tag_obj.id)
    movements = Movement.objects.filter(tags__id=tag_obj.id)

    # Tag each relevant piece with all the new tags 
    for piece in pieces.all():
        for replacement_obj in replacement_objects:
            piece.tags.add(replacement_obj)
            piece.save()
    for movement in movements.all():
        for replacement_obj in replacement_objects:
            movement.tags.add(replacement_obj)
            movement.save()

    # Now delete old tag
    tag_obj.delete()

# TODO : MAKE SURE DELETING ALL ASSOCIATED FKS (in piece_tags/movement_tags)
def delete_tag(tag): 
    tag.delete()

def review_tag(arraydata):
    if arraydata:
        green = "#90EE90"
        red = "#FA8072"
        arraydata = str(arraydata).strip()
        tuples = arraydata.split(';')
        for tup in tuples[:len(tuples)-1]:
            tup = tup.replace('(', '').replace(')', '')
            info = tup.split(',')
            tag_id = info[0]
            color = info[1]
            # Get the corresponding tag
            tag = Tag.objects.get(id=tag_id)
            # Approve the tag according to designated color
            if color == green:
                tag.approved = True
                tag.save()
            elif color == red:
                delete_tag(tag)

'''
Send an email to multiple addresses
'''
def sendemails(fromuser, emails, subject, message):
    datatuple = (subject, message, fromuser, emails)
    try:
        send_mass_mail((datatuple,), fail_silently=False)
        return True
    except SMTPException:
        print("exceptin")
        return False

''' 
Create a temporary user (not active). 
'''
def createTempUser(first_name, last_name, email):
    first_part = email.split('@')[0]
    username = first_part+str(randrange(RANDOM_RANGE))
    user = User(username=username, first_name=first_name, last_name=last_name, email=email, is_active=False)
    user.save()
    password = User.objects.make_random_password()
    user.set_password(password)
    userprofile = UserProfile(user=user)
    return user, userprofile

'''
Set permissions for users 
'''
def setPermissions(users, permissions):
    for user in users:
        for permission in permissions:  
            user.set_perm(permission)   # Or something along these lines 
