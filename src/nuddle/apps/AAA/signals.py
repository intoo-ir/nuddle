

def my_callback(sender, **kwargs):
    print('Request Finished')


def create_new_user(sender, instance, created, **kwargs):
    if created:
        print('NEW USER CREATED', instance)


def update_user(sender, instance, created, **kwargs):
    if not created:
        print('USER UPDATED',instance)