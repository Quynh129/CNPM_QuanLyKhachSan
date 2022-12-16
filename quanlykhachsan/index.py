from flask import Flask, render_template, request, redirect, session, jsonify
import quanlykhachsan.dao
from quanlykhachsan import app, login
from quanlykhachsan import admin, dao, controllers
from flask_login import login_user, logout_user, login_required
from quanlykhachsan.decorators import annonymous_user
from datetime import datetime
import datetime as date_time


@login.user_loader
def load_user(user_id):  # Hàm tải dữ liệu người dùng cho Flask-Login
    return dao.get_user_by_id(user_id)


app.add_url_rule('/', 'index', controllers.index)
app.add_url_rule('/dangNhap', 'login_my_user', controllers.login_my_user, methods=['get', 'post'])
app.add_url_rule('/dangNhap-admin', 'admin_login', controllers.admin_login, methods=['post'])
app.add_url_rule('/dangXuat', 'logout_my_user', controllers.logout_my_user)
app.add_url_rule('/soDoPhong', 'sodophong', controllers.sodophong)
app.add_url_rule('/datPhong', 'datphong', controllers.datphong)
app.add_url_rule('/yeuCauDatPhong', 'yeucau', controllers.yeucau, methods=['get', 'post'])
app.add_url_rule('/chiTietPhieuDatRong/<int:phong_id>', 'chitietphieudat_null', controllers.chitietphieudat_null,
                 methods=['get', 'post'])
app.add_url_rule('/chiTietPhieuDat/<int:phieudatphong_id>', 'chitietphieudat_data', controllers.chitietphieudat_data,
                 methods=['get', 'post'])
app.add_url_rule('/thuePhong', 'thuephong', controllers.thuephong)
app.add_url_rule('/chiTietPhieuThueRong/<int:phong_id>', 'chitietphieuthue_null', controllers.chitietphieuthue_null,
                 methods=['get', 'post'])
app.add_url_rule('/chiTietPhieuThueDatTruoc/<int:phieudatphong_id>', 'chitietphieudattruoc',
                 controllers.chitietphieudattruoc, methods=['get', 'post'])
app.add_url_rule('/chiTietPhieuThue_HD/<int:phieuthuephong_id>', 'chitietphieuthue', controllers.chitietphieuthue,
                 methods=['get', 'post'])


if __name__ == '__main__':
    app.run(debug=True)
