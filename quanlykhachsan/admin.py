from quanlykhachsan.models import Phong, LoaiPhong, TiLePhuThu
from quanlykhachsan import db, app, dao
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import request

from flask import redirect
import flask_login as login

from quanlykhachsan.models import TaiKhoan


def get_user_by_id(user_id):
    return TaiKhoan.query.get(user_id)


class MyAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        flag = 0
        if current_user.is_authenticated:
            user = get_user_by_id(current_user.get_id())
            if user.phanQuyen.value == 0:
                flag = 1

        return self.render('admin/index.html', flag=flag)


class MyModelView(ModelView):

    # for login: only access while login
    def is_accessible(self):
        return current_user.is_authenticated


class QuanLyPhongView(MyModelView):
    column_filters = ['trangThaiPhong', 'ma_loaiphong']
    can_view_details = True
    can_delete = False
    can_export = True
    page_size = 20
    column_list = ('id', 'trangThaiPhong', 'loaiphong')
    column_labels = {
        'id': 'Mã phòng',
        'trangThaiPhong': 'Trạng thái phòng',
        'loaiphong': 'Loại phòng',
    }


class QuanLyLoaiPhongView(MyModelView):
    column_filters = ['tenLoai', 'donGia', 'soNguoiToiDa', 'trangThaiLoaiPhong']
    can_view_details = True
    can_delete = False
    can_export = True
    page_size = 20
    column_labels = {
        'tenLoai': 'Loại phòng',
        'donGia': 'Đơn giá',
        'soNguoiToiDa': 'Số người tối đa',
        'trangThaiLoaiPhong': 'Trạng thái loại phòng'
    }


class TiLePhuThuView(MyModelView):
    column_filters = ['tenLoai', 'ten', 'giaTri']
    can_view_details = True
    can_delete = False
    can_export = True
    page_size = 20
    column_labels = {
        'tenLoai': 'Tên loại',
        'ten': 'Tên',
        'giaTri': 'Giá trị',
    }


class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        thongkedoanhthu = dao.thongke_doanhthu(id_loaiphong=request.args.get('type_room'),
                                               thang=request.args.get('month'), nam=request.args.get('year'))
        thongketansuat = dao.thongke_tansuat()

        return self.render('admin/thongKe.html', thongkedoanhthu=thongkedoanhthu, thongketansuat=thongketansuat)

    @expose('/thongkedoanhthu')
    def thongkedoanhthu(self):
        loaiphong = dao.load_loaiphong()

        thongkedoanhthu = dao.thongke_doanhthu(id_loaiphong=request.args.get('type_room'),
                                               thang=request.args.get('month'), nam=request.args.get('year'))

        return self.render('admin/thongKeDoanhThu.html', loaiphong=loaiphong, thongkedoanhthu=thongkedoanhthu)

    @expose('/thongketansuat')
    def thongketansuat(self):
        thongketansuat = dao.thongke_tansuat(thang=request.args.get('month'), nam=request.args.get('year'))

        return self.render('admin/thongKeTanSuat.html', thongketansuat=thongketansuat)

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app=app, name='Quản lý khách sạn', template_mode='bootstrap4', index_view=MyAdminView())
admin.add_view(QuanLyPhongView(Phong, db.session, name='Phòng'))
admin.add_view(QuanLyLoaiPhongView(LoaiPhong, db.session, name='Loại phòng'))
admin.add_view(TiLePhuThuView(TiLePhuThu, db.session, name='Tỉ lệ phụ thu'))
admin.add_view(ThongKeView(name='Thống kê'))
