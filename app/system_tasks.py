from background_task import background
from background_task.models import Task
from .models import CustomUser


# run this task: python manage.py process_tasks
def start():
    update_achievement(repeat=Task.HOURLY, repeat_until=None)
    add_point_by_achievement(repeat=Task.WEEKLY, repeat_until=None)
    ban_user(repeat=Task.HOURLY, repeat_until=None)
    delete_user_violated(repeat=Task.DAILY, repeat_until=None)


def __check(user, achievement):
    if user.post_count >= achievement['post_count'] \
            and user.liked_people >= achievement['liked_people'] \
            and user.follower_count >= achievement['follower_count']:
        return True
    return False


def __get_achievement(user):
    achievements = [
        {'post_count': 20, 'liked_people': 100, 'follower_count': 1000},
        {'post_count': 50, 'liked_people': 300, 'follower_count': 3000},
        {'post_count': 50, 'liked_people': 500, 'follower_count': 5000},
        {'post_count': 100, 'liked_people': 500, 'follower_count': 5000},
        {'post_count': 100, 'liked_people': 1000, 'follower_count': 10000},
    ]
    for i in range(len(achievements), 0, -1):
        if __check(user, achievements[i - 1]):
            return i
    return 0


@background()
def update_achievement():
    list_user = CustomUser.objects.raw(
        'select u.*,'
        'count(distinct if(r.feedback_value = 1, r.user_id, null)) as liked_people,'
        'count(distinct if(p.status = 1, p.id, null)) as post_count,'
        'count(distinct f.follower_id) as follower_count '
        'from app_customuser u '
        'left join app_post p on u.id = p.user_id '
        'left join app_postreaction r on p.id = r.post_id '
        'left join app_follow f on u.id = f.followed_id '
        'group by u.id')
    for user in list_user:
        user.achievement = __get_achievement(user)
        user.save()


@background()
def add_point_by_achievement():
    list_user = CustomUser.objects.filter(achievement__gt=0)
    add_points = [0, 100, 120, 150, 160, 170]
    for user in list_user:
        user.point += add_points[user.achievement]
        user.save()


@background()
def ban_user():
    list_user = CustomUser.objects.raw(
        'select u.*,'
        'count(distinct if(p.status = 3, p.id, null)) as count '
        'from app_customuser u '
        'left join app_post p on u.id = p.user_id '
        'group by u.id')

    for user in list_user:

        user.count_violated = user.count
        if user.count_violated >= 3:
            user.is_active = 0
        user.save()


@background()
def delete_user_violated():
    list_user_ban_5 = CustomUser.objects.filter(count_violated__gte=5)
    for user in list_user_ban_5:
        user.is_deleted = True
        user.save()


@background()
def delete_user_not_login():
    list_user = CustomUser.objects.filter(last_login__gte=30)
    for user in list_user:
        user.is_deleted = True
        user.save()
