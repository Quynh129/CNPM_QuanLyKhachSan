from quanlykhachsan.models import Phong, LoaiPhong, LoaiKhachHang, TiLePhuThu
from quanlykhachsan import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')


admin = Admin(app=app, name='Quản lý khách sạn', template_mode='bootstrap4')
admin.add_view(ModelView(Phong, db.session))
admin.add_view(ModelView(LoaiPhong, db.session))
admin.add_view(ModelView(LoaiKhachHang, db.session))
admin.add_view(ModelView(TiLePhuThu, db.session))
admin.add_view(ThongKeView(name='Thống kê'))
