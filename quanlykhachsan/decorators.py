from functools import wraps
from flask_login import current_user
from flask import redirect

from quanlykhachsan.models import TaiKhoan


# ko cho gọi trang login bằng đường link nếu đã đăng nhập
def get_user_by_id(user_id):
    return TaiKhoan.query.get(user_id)


def annonymous_user(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            user = get_user_by_id(current_user.get_id())
            if user.phanQuyen.value == 0:
                return redirect('/admin')
            else:
                return redirect('/soDoPhong')

        return f(*args, **kwargs)

    return decorated_func
