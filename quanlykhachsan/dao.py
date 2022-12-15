import json
from quanlykhachsan import app, db
from quanlykhachsan.models import TaiKhoan, KhachHang, LoaiPhong, Phong, \
    PhieuDatPhong, PhieuThuePhong, PhieuThueChiTiet, TiLePhuThu, PhieuThueTiLe
import hashlib
from flask import session
from sqlalchemy import func, update
from flask_login import current_user

import datetime
from datetime import datetime as date_time


# PHẦN LOGIN
# ----- 1. Xác thực tài khoản
# ----- 2. Lấy username
# ----- 3. Lấy Id
def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return TaiKhoan.query.filter(TaiKhoan.tenTaiKhoan.__eq__(username.strip()),
                                 TaiKhoan.matKhau.__eq__(password)).first()


def get_username(username):
    return TaiKhoan.query.filter(TaiKhoan.tenTaiKhoan.__eq__(username.strip())).all()


def get_user_by_id(user_id):
    return TaiKhoan.query.get(user_id)


# -----kết thúc phần login-----


# PHẦN PHÒNG + LOẠI PHÒNG
def load_loaiphong():
    return LoaiPhong.query.all()


def get_loaiphong_by_phongid(phong_id):
    query = db.session.query(LoaiPhong.id, LoaiPhong.tenLoai, LoaiPhong.donGia, LoaiPhong.soNguoiToiDa) \
        .join(Phong, Phong.ma_loaiphong.__eq__(LoaiPhong.id)).filter(Phong.id.__eq__(phong_id))

    return query.all()


def get_soluong_loaiphong(phong_id):
    query = db.session.query(LoaiPhong.id, LoaiPhong.tenLoai, LoaiPhong.soNguoiToiDa) \
        .join(Phong, Phong.ma_loaiphong.__eq__(LoaiPhong.id)).filter(Phong.id.__eq__(phong_id)).first()

    soluong = query.soNguoiToiDa

    return soluong


def get_phong_by_id(phong_id):
    return Phong.query.get(phong_id)


# -----kết thúc phần phòng + loại phòng-----


# PHẦN KHÁCH HÀNG
# ----- 1. Kiểm tra đã có KH này chưa
# ----- 2. Lấy KH = id
# ----- 2. Lấy Id của Kh mới để truyền vào PhieuDat & PhieuThue
# ----- 3. Lấy dsach KH
# ----- 4. Tạo KH mới
def get_khachhang_by_cccd(hoten, cccd):
    return KhachHang.query.filter(KhachHang.hoTen.__eq__(hoten.capitalize()),
                                  KhachHang.CCCD.__eq__(cccd.strip())).first()


def get_khachhang_by_id(khachhang_id):
    return KhachHang.query.get(khachhang_id)


def get_id_khachhang(hoten, cccd):
    query = KhachHang.query.filter(KhachHang.hoTen.__eq__(hoten.capitalize()),
                                   KhachHang.CCCD.__eq__(cccd.strip())).first()
    id_kh = query.id
    return id_kh


def load_khachhang():
    return KhachHang.query.all()


def upload_khachhang(hoten, cccd, sodienthoai, quoctich):
    kh = KhachHang(hoTen=hoten.capitalize(), CCCD=cccd.strip(), soDienThoai=sodienthoai.strip(), quocTich=quoctich)
    db.session.add(kh)
    db.session.commit()


# -----kết thúc phần khách hàng-----


# PHẦN LOAD DANH SACH PHÒNG
def load_phongDaDat(ngaynhan=None, ngaytra=None):
    # Lấy các phòng có phiếu đặt nằm trong ngày nhận và ngày trả và có trạng thái là chờ nhận phòng
    query = Phong.query
    if ngaynhan and ngaytra:
        query = db.session.query(Phong.id, Phong.ma_loaiphong, PhieuDatPhong.trangThai, PhieuDatPhong.id) \
            .join(PhieuDatPhong, PhieuDatPhong.ma_phong.__eq__(Phong.id), isouter=True) \
            .filter(PhieuDatPhong.trangThai.__eq__('Chờ nhận phòng')
                    & (PhieuDatPhong.ngayNhan.between(ngaynhan, ngaytra)
                       | PhieuDatPhong.ngayTra.between(ngaynhan, ngaytra)))
        # Chỉnh sửa từ trạng thái phiếu qua trạng thái phòng
        kq = list()
        for q in query:
            q = list(q)
            if q[2] == 'Chờ nhận phòng': q[2] = 'Đã đặt'
            kq.append(q)
        return kq


def load_phongDangThue(ngaynhan=None, ngaytra=None):
    # Lấy các phòng có trong phieuThuePhong nằm trong ngày nhận và ngày trả và có trạng thái không phải là 1 tức là đã thanh toán rồi
    if ngaynhan and ngaytra:
        phongDangThue = db.session.query(PhieuThuePhong.ma_phong) \
            .filter(PhieuThuePhong.trangThai.__eq__(0)) \
            .filter(PhieuThuePhong.ngayNhan.between(ngaynhan, ngaytra)
                    | PhieuThuePhong.ngayTra.between(ngaynhan, ngaytra))

        maLoaiPhong = (db.session.query(Phong.ma_loaiphong))[0][0]
        kq = list()
        for p in phongDangThue:
            p = list(p)
            maP = db.session.query(Phong.ma_loaiphong) \
                .filter(Phong.id == p[0])[0][0]
            p.append(maP)
            p.append('Đang thuê')
            p.append('')
            kq.append(p)
        return kq


def load_phongTrong(ngaynhan=None, ngaytra=None):
    # Không lấy các phòng đang thuê và đã đặt
    dangThue = load_phongDangThue(ngaynhan, ngaytra)
    daDat = load_phongDaDat(ngaynhan, ngaytra)
    khongTrong = list()
    for p in dangThue:
        khongTrong.append(p[0])
    for p in daDat:
        khongTrong.append(p[0])
    query = db.session.query(Phong.id, Phong.ma_loaiphong) \
        .filter(Phong.id.notin_(khongTrong))
    # Thêm trạng thái là phòng trống
    kq = list()
    for q in query:
        q = list(q)
        q.append('Trống')
        kq.append(q)
    return kq


def load_phongTatCa(ngaynhan=None, ngaytra=None):
    # load_phongDangThue => DS phòng đang thuê
    # load_phongDaDat => DS phòng đã đặt
    # load_phongTrong => DS phòng trống
    dangThue = load_phongDangThue(ngaynhan, ngaytra)
    daDat = load_phongDaDat(ngaynhan, ngaytra)
    trong = load_phongTrong(ngaynhan, ngaytra)
    tatCa = dangThue + daDat + trong
    tatCaPhong = sorted(tatCa, key=lambda t: t[0])
    return tatCaPhong


def load_danhsachphong(ngaynhan=None, ngaytra=None, trangthai=None):
    query = Phong.query
    if ngaynhan and ngaytra:
        if trangthai == 'daDat':
            return load_phongDaDat(ngaynhan, ngaytra)
        if trangthai == 'dangThue':
            return load_phongDangThue(ngaynhan, ngaytra)
        if trangthai == 'trong':
            return load_phongTrong(ngaynhan, ngaytra)
        if trangthai == 'tatCa':
            return load_phongTatCa(ngaynhan, ngaytra)


# -----kết thúc phần load danh sách phòng-----


# PHẦN ĐẶT PHÒNG
# ----- 1. Lấy dsach phieuDat (đặt phòng)
# ----- 2. Lấy 1 phiếu đặt phòng
# ----- 3. Tạo phieuDat mới (tạo yêu cầu, phiếu đặt chi tiết rỗng)
# ----- 4. Cập nhật
def load_phieudatphong(kw=None, state=None):
    query = db.session.query(PhieuDatPhong.id, KhachHang.hoTen,
                             PhieuDatPhong.ngayNhan, PhieuDatPhong.ngayTra, PhieuDatPhong.ngayDat,
                             PhieuDatPhong.ma_phong, PhieuDatPhong.trangThai) \
        .join(KhachHang, KhachHang.id.__eq__(PhieuDatPhong.ma_khachhang), isouter=True)

    if kw:
        query = query.filter(KhachHang.hoTen.contains(kw))

    if state:
        query = query.filter(PhieuDatPhong.trangThai.__eq__(state))

    return query.group_by(PhieuDatPhong.id).all()


def get_phieudat_by_id(phieudat_id):
    return PhieuDatPhong.query.get(phieudat_id)


def upload_phieudat(flag, ngaynhan, ngaytra, ngaydat, trangthai, makhachhang, maloaiphong, maphong=None):
    if flag == 1:
        pd = PhieuDatPhong(ngayNhan=ngaynhan, ngayTra=ngaytra, ngayDat=ngaydat, trangThai=trangthai,
                           ma_khachhang=makhachhang, ma_loaiphong=maloaiphong)
    elif flag == 2:
        pd = PhieuDatPhong(ngayNhan=ngaynhan, ngayTra=ngaytra, ngayDat=ngaydat, trangThai=trangthai,
                           ma_khachhang=makhachhang, ma_loaiphong=maloaiphong,
                           ma_taikhoan=current_user.id, ma_phong=maphong)
    db.session.add(pd)
    db.session.commit()


def update_phieudat(idphieudat, trangthai, maphong=None):
    query = get_phieudat_by_id(idphieudat)
    query.ma_taikhoan = current_user.id
    query.trangThai = trangthai
    if maphong:
        query.ma_phong = maphong

    db.session.commit()


# -----kết thúc phần đặt phòng-----


# PHẦN THUÊ PHÒNG
# ----- 1. Lấy dsach phieuThue
# ----- 2. Lấy dsach phieuThueChiTiet
# ----- 3. Tạo phieuThue mới (lấy id phiếu thuê mới tạo + tạo phiếu thuê + phiếu thuê chi tiết)
# ----- 4. Lấy 1 phiếu thuê phòng + ptct
# ----- 5. Cập nhật
# ----- 6. Load dsach tỉ lệ phụ thu
def load_phieuthuephong(kw=None, state=None):
    query = db.session.query(PhieuThuePhong.id, KhachHang.hoTen,
                             PhieuThuePhong.ngayNhan, PhieuThuePhong.ngayTra,
                             PhieuThuePhong.ma_phong, PhieuThuePhong.trangThai, PhieuThuePhong.ngayThanhToan) \
        .join(PhieuThueChiTiet, PhieuThueChiTiet.ma_phieuthue.__eq__(PhieuThuePhong.id)) \
        .join(KhachHang, KhachHang.id.__eq__(PhieuThueChiTiet.ma_khachhang))

    if kw:
        query = query.filter(KhachHang.hoTen.contains(kw))
    if state:
        query = query.filter(PhieuThuePhong.trangThai.__eq__(state))

    return query.group_by(PhieuThuePhong.id).order_by(PhieuThuePhong.id).all()


def load_phieuthuechitiet():
    return PhieuThueChiTiet.query.all()


def get_id_phieuthue_last():
    query = db.session.query(PhieuThuePhong).order_by(PhieuThuePhong.id.desc()).first()
    id_pt = query.id
    return id_pt


def upload_phieuthue(ngaynhan, ngaytra, ngaylap, songay, dongia, tile, matile,
                     maphong, makhachhang):
    # tạo phiếu thuê
    pt = PhieuThuePhong(ngayNhan=ngaynhan, ngayTra=ngaytra, ngayLap=ngaylap,
                        soNgay=songay, donGia=dongia, tiLe=tile,
                        ma_taikhoan=current_user.id, ma_phong=maphong)
    db.session.add(pt)
    id_pt = get_id_phieuthue_last()

    # tạo phiếu thuê chi tiết
    for kh in makhachhang:
        ptct = PhieuThueChiTiet(ma_khachhang=kh, ma_phieuthue=id_pt)
        db.session.add(ptct)

    # tạo phiếu thuê - tỉ lệ
    for idtile in matile:
        pttl = PhieuThueTiLe(ma_tile=idtile, ma_phieuthue=id_pt)
        db.session.add(pttl)

    db.session.commit()


def get_phieuthue_by_id(phieuthue_id):
    return PhieuThuePhong.query.get(phieuthue_id)


def get_chitietphieuthue_by_id(phieuthuephong_id):
    return db.session.query(PhieuThueChiTiet.ma_phieuthue, PhieuThueChiTiet.ma_khachhang) \
        .filter(PhieuThueChiTiet.ma_phieuthue.__eq__(phieuthuephong_id)).all()


def update_thanhtoan(idphieuthue, ngaythanhtoan):
    # cập nhật phiếu thuê
    query = get_phieuthue_by_id(idphieuthue)

    query.ma_taikhoan = current_user.id
    query.trangThai = True
    query.ngayThanhToan = ngaythanhtoan

    db.session.commit()


def load_tilephuthu():
    return TiLePhuThu.query.all()


# -----kết thúc phần thuê phòng-----


# PHẦN THỐNG KÊ
# def thongke_doanhthu(id_loaiphong=None, nam=None, thang=None, tu_ngay=None, den_ngay=None):
def thongke_doanhthu(id_loaiphong=None, nam=None, thang=None):
    query = db.session.query(LoaiPhong.id, LoaiPhong.tenLoai,
                             func.sum(PhieuThuePhong.soNgay * PhieuThuePhong.donGia * PhieuThuePhong.tiLe),
                             func.count(Phong.id)) \
        .join(Phong, Phong.ma_loaiphong.__eq__(LoaiPhong.id), isouter=True) \
        .join(PhieuThuePhong, PhieuThuePhong.ma_phong.__eq__(Phong.id), isouter=True) \
        .filter(PhieuThuePhong.trangThai.__eq__(True))

    date_format = "%Y-%m-%d"

    if id_loaiphong:
        query = query.filter(LoaiPhong.id.__eq__(id_loaiphong))

    if nam:
        query = query.filter(PhieuThuePhong.ngayThanhToan
                             .between(datetime.datetime.strptime('{}-01-01'.format(nam), date_format),
                                      (datetime.datetime.strptime('{}-12-31'.format(nam), date_format))))

    if nam and thang:
        ngay_ket = 0
        if thang == 2:
            if (nam % 400 == 0) or ((nam % 4 == 0) and (nam % 100 != 0)):
                ngay_ket = 29
            else:
                ngay_ket = 28
        elif thang == 1 or thang == 3 or thang == 5 or thang == 7 or thang == 8 or thang == 10 or thang == 12:
            ngay_ket = 31
        else:
            ngay_ket = 30

        query = query.filter(PhieuThuePhong.ngayThanhToan
                             .between(datetime.datetime.strptime('{}-{}-01'.format(nam, thang), date_format),
                                      (datetime.datetime.strptime('{}-{}-{}'.format(nam, thang, ngay_ket),
                                                                  date_format))))

    return query.group_by(LoaiPhong.id).order_by(LoaiPhong.id).all()
    # return db.session.query(PhieuThuePhong.id, PhieuThuePhong.ngayTra, PhieuThuePhong.ngayThanhToan).all()


def thongke_tansuat(nam=None, thang=None):
    query = db.session.query(Phong.id, func.sum(PhieuThuePhong.soNgay)) \
        .join(PhieuThuePhong, PhieuThuePhong.ma_phong.__eq__(Phong.id))

    date_format = "%Y-%m-%d"

    if nam:
        query = query.filter(PhieuThuePhong.ngayThanhToan
                             .between(datetime.datetime.strptime('{}-01-01'.format(nam), date_format),
                                      (datetime.datetime.strptime('{}-12-31'.format(nam), date_format))))

    if nam and thang:
        ngay_ket = 0
        if thang == 2:
            if (nam % 400 == 0) or ((nam % 4 == 0) and (nam % 100 != 0)):
                ngay_ket = 29
            else:
                ngay_ket = 28
        elif thang == 1 or thang == 3 or thang == 5 or thang == 7 or thang == 8 or thang == 10 or thang == 12:
            ngay_ket = 31
        else:
            ngay_ket = 30

        query = query.filter(PhieuThuePhong.ngayThanhToan
                             .between(datetime.datetime.strptime('{}-{}-01'.format(nam, thang), date_format),
                                      (datetime.datetime.strptime('{}-{}-{}'.format(nam, thang, ngay_ket),
                                                                  date_format))))

    return query.group_by(Phong.id).all()


# -----kết thúc phần thống kê-----


if __name__ == '__main__':
    from quanlykhachsan import app

    with app.app_context():
        ds = load_danhsachphong(ngaynhan = date_time.today() + datetime.timedelta(days=-30),
                                ngaytra = date_time.today() + datetime.timedelta(days=30),
                                trangthai='dangThue')
        # print(date_time.today() + datetime.timedelta(days=-30))
        # print(date_time.today() + datetime.timedelta(days=30))

        arr = []
        i = 0
        print(load_phieuthuephong())
        for pt in load_phieuthuephong():
            arr.append([])
            for j in range(0, 2):
                if j == 1:
                    arr[i].append(1)
                else:
                    arr[i].append(2)
            i += 1
        x = 0
        for pt in load_phieuthuephong():
            for y in range(0, 2):
                print(f'{arr[x][y]}')
            x += 1


        print(arr)
        # print(date_time.today() + datetime.timedelta(days=5))
