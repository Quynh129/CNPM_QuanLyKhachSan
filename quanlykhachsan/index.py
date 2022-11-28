from flask import Flask, render_template, request, redirect, session
import quanlykhachsan.dao
from quanlykhachsan import app, login
from quanlykhachsan import admin, dao
from flask_login import login_user, logout_user
from quanlykhachsan.decorators import annonymous_user


@app.route('/')  # define để biết trang chủ
def index():
    return render_template('trangChu.html')


# gọi trang Yêu cầu đă phòng (của KH)
@app.route('/yeuCauDatPhong')
def yeucau():
    return render_template('yeuCauDatPhong.html')


# gọi trang Đăng nhập
@app.route('/dangNhap')
def dangnhap():
    return render_template('dangNhap.html')


# xử lý đăng nhập
@login.user_loader
def load_user(user_id):  # Hàm tải dữ liệu người dùng cho Flask-Login
    return dao.get_user_by_id(user_id)


@app.route('/dangNhap-admin', methods=['post'])
def admin_login():
    username = request.form['username']  # name in html, not id
    password = request.form['password']

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)
        if str(user.phanQuyen) == 'PhanQuyen.ADMIN':
            return redirect('/admin')
        else:
            return redirect('/soDoPhong')


@app.route('/dangNhap', methods=['get', 'post'])
def login_my_user():
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            if str(user.phanQuyen) == 'PhanQuyen.ADMIN':
                return redirect('/admin')
            else:
                return redirect('/soDoPhong')
    return render_template('dangNhap.html')


@app.route('/dangXuat')
def logout_my_user():
    logout_user()
    return redirect('/dangNhap')


# -----kết-----


# gọi trang Sơ đồ phòng
@app.route('/soDoPhong')
def sodophong():
    return render_template('soDoPhong.html')


# gọi trang Đặt phòng
@app.route('/datPhong')
def datphong():
    return render_template('datPhong.html')


# gọi trang Thuê phòng
@app.route('/thuePhong')
def thuephong():
    return render_template('thuePhong.html')


# gọi trang Thanh toán
@app.route('/thanhToan')
def thanhtoan():
    return render_template('thanhToan.html')


# gọi trang Chi tiết phiếu đặt
@app.route('/chiTietPhieuDat')
def chitietphieudat():
    return render_template('chiTietPhieuDat.html')


# gọi trang Chi tiết phiếu thue
@app.route('/chiTietPhieuThue')
def chitietphieuthue():
    return render_template('chiTietPhieuthue.html')


# gọi trang Chi tiết phiếu đặt
@app.route('/chiTietHoaDon')
def chitiethoadon():
    return render_template('chiTietHoaDon.html')


# gọi trang Xếp phòng
@app.route('/xepPhong')
def xepphong():
    return render_template('xepPhong.html')


if __name__ == '__main__':
    app.run(debug=True)
