'''
USERS
'''

from django.shortcuts import render
from elvis.models.userprofile import UserProfile
from elvis.utils.helpers import partition 

# Render list of user profiles
def user_profiles(request):
    userprofiles = UserProfile.objects.all()
    active = filter(lambda u: u.user.is_active, userprofiles)
    userprofiles_list = partition(active, 4)
    return render(request, 'userprofile/userprofile_list.html', {'content': userprofiles_list, 'length':len(userprofiles)})

# Individual user profile
def user_view(request, pk):
    user = UserProfile.objects.filter(pk=pk)[0]
    return render(request, 'userprofile/userprofile_detail.html', {'content':user})

# Render temporary users who need to be registered (admin privileges)
# Register them by setting permissions and changing their state to active/not temporary
def registration(request):
	#if request.method == 'POST':
	temp_users = UserProfile.objects.filter(is_temp=True)
	print temp_users
	return render(request, 'registration/registration.html', {'users': temp_users})

def setPermissions(request):
	return render(request, 'registration/user_permissions.html')