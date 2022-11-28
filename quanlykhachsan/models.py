from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from quanlykhachsan import db, app
from enum import Enum as UserEnum
from flask_login import UserMixin
import hashlib


class PhanQuyen(UserEnum):
    ADMIN = 0
    USER = 1


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class TaiKhoan(BaseModel, UserMixin):
    __tablename__ = 'taikhoan'
    tenTaiKhoan = Column(String(50), nullable=False)
    matKhau = Column(String(50), nullable=False)
    phanQuyen = Column(Enum(PhanQuyen), default=PhanQuyen.USER)
    trangThai = Column(Boolean, default=True)
    hoTen = Column(String(50), nullable=False)
    soDienThoai = Column(String(50), nullable=False)
    fk_phieudat = relationship('PhieuDatPhong', backref='taikhoan', lazy=False)
    fk_phieuthue = relationship('PhieuThuePhong', backref='taikhoan', lazy=False)
    fk_hoadon = relationship('HoaDon', backref='taikhoan', lazy=False)


class LoaiKhachHang(BaseModel):
    __tablename__ = 'loaikhachhang'
    tenLoaiKH = Column(String(50), nullable=False)
    heSo = Column(Float, default=0)
    fk_khachhang = relationship('KhachHang', backref='loaikhachhang', lazy=False)


class KhachHang(BaseModel):
    __tablename__ = 'khachhang'
    hoTen = Column(String(50), nullable=False)
    CCCD = Column(String(50), nullable=False)
    soDienThoai = Column(String(50), nullable=False)
    ma_loaiKH = Column(Integer, ForeignKey(LoaiKhachHang.id), nullable=False)
    fk_phieudat = relationship('PhieuDatPhong', backref='khachhang', lazy=False)
    fk_phieuthuechitiet = relationship('PhieuThuePhong', secondary='phieuthuechitiet', backref='khachhang', lazy=False)


class LoaiPhong(BaseModel):
    __tablename__ = 'loaiphong'
    tenLoai = Column(String(50), nullable=False)
    donGia = Column(Float, default=0)
    soNguoiToiDa = Column(Integer, nullable=False)
    trangThaiLoaiPhong = Column(Boolean, default=True)
    fk_phong = relationship('Phong', backref='loaiphong', lazy=False)
    fk_phieudat = relationship('PhieuDatPhong', backref='loaiphong', lazy=False)

    def __str__(self):
        return self.tenLoai


class Phong(BaseModel):
    __tablename__ = 'phong'
    trangThaiPhong = Column(Boolean, default=True)
    ma_loaiphong = Column(Integer, ForeignKey(LoaiPhong.id), nullable=False)
    fk_phieudat = relationship('PhieuDatPhong', backref='phong', lazy=False)
    fk_phieuthue = relationship('PhieuThuePhong', backref='phong', lazy=False)


class PhieuDatPhong(BaseModel):
    __tablename__ = 'phieudatphong'
    ngayNhan = Column(Date, nullable=False)
    ngayTra = Column(Date, nullable=False)
    ngayDat = Column(Date, nullable=False)
    trangThai = Column(String(50), nullable=False)
    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id), nullable=False)
    ma_khachhang = Column(Integer, ForeignKey(KhachHang.id), nullable=False)
    ma_loaiphong = Column(Integer, ForeignKey(LoaiPhong.id), nullable=False)
    ma_phong = Column(Integer, ForeignKey(Phong.id))


class PhieuThuePhong(BaseModel):
    __tablename__ = 'phieuthuephong'
    ngayNhan = Column(Date, nullable=False)
    ngayTra = Column(Date, nullable=False)
    ngayLap = Column(Date, nullable=False)  # = ngayNhan
    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id), nullable=False)
    ma_phong = Column(Integer, ForeignKey(Phong.id), nullable=False)
    fk_hoadon = relationship('HoaDon', backref='phieuthuephong', lazy=False)
    fk_phieuthuechitiet = relationship(KhachHang, secondary='phieuthuechitiet', backref='phieuthuephong', lazy=False)


class PhieuThueChiTiet(db.Model):
    __tablename__ = 'phieuthuechitiet'
    soNgay = Column(Integer, nullable=False)
    ma_khachhang = Column(Integer, ForeignKey(KhachHang.id), primary_key=True)
    ma_phieuthue = Column(Integer, ForeignKey(PhieuThuePhong.id), primary_key=True)


class TiLePhuThu(BaseModel):
    __tablename__ = 'tilephuthu'
    mucTiLe = Column(Float, default=0)
    soNguoi = Column(Integer, nullable=False)
    fk_hoadon = relationship('HoaDon', backref='tilephuthu', lazy=False)


class HoaDon(BaseModel):
    __tablename__ = 'hoadon'
    ngayNhan = Column(Date, nullable=False)
    ngayTra = Column(Date, nullable=False)
    ngayLap = Column(Date, nullable=False)  # = ngayTra
    tongTien = Column(Float, default=0)
    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id), nullable=False)
    ma_phieuthue = Column(Integer, ForeignKey(PhieuThuePhong.id), nullable=False)
    ma_phuthu = Column(Integer, ForeignKey(TiLePhuThu.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():

        # tạo toàn bộ bảng
        db.create_all()

        # thêm data cho: TaiKhoan
        password_0 = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        u1 = TaiKhoan(tenTaiKhoan='admin', matKhau=password_0, phanQuyen=PhanQuyen.ADMIN,
                      hoTen='Quản trị viên', soDienThoai='0123456789')
        password_1 = str(hashlib.md5('1954052077'.encode('utf-8')).hexdigest())
        u2 = TaiKhoan(tenTaiKhoan='HP', matKhau=password_1,
                      hoTen='Cao Hoàng Phượng', soDienThoai='0123456789')
        password_2 = str(hashlib.md5('1954052080'.encode('utf-8')).hexdigest())
        u3 = TaiKhoan(tenTaiKhoan='HQ', matKhau=password_2,
                      hoTen='Hứa Lê Như Quỳnh', soDienThoai='0123456789')
        password_3 = str(hashlib.md5('1954052081'.encode('utf-8')).hexdigest())
        u4 = TaiKhoan(tenTaiKhoan='NQ', matKhau=password_3,
                      hoTen='Nguyễn Thị Như Quỳnh', soDienThoai='0123456789')

        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        # thêm data cho: loaiKhachHang
        lkh0 = LoaiKhachHang(tenLoaiKH='Nội địa', heSo=1)
        lkh1 = LoaiKhachHang(tenLoaiKH='Nước ngoài', heSo=1.5)

        db.session.add_all([lkh0, lkh1])
        db.session.commit()

        # thêm data cho: KhachHang
        kh1 = KhachHang(hoTen='Quý Ngài A', CCCD='079080012345', soDienThoai='0123456789', ma_loaiKH=2)
        kh2 = KhachHang(hoTen='Quý Cô B', CCCD='079190012345', soDienThoai='0123456789', ma_loaiKH=1)
        kh3 = KhachHang(hoTen='Quý Ông C', CCCD='079050012345', soDienThoai='0123456789', ma_loaiKH=1)
        kh4 = KhachHang(hoTen='Quý Bà D', CCCD='079155012345', soDienThoai='0123456789', ma_loaiKH=1)
        kh5 = KhachHang(hoTen='Chàng Trai E', CCCD='079202012345', soDienThoai='0123456789', ma_loaiKH=1)
        kh6 = KhachHang(hoTen='Cô Gái F', CCCD='079301012345', soDienThoai='0123456789', ma_loaiKH=2)

        db.session.add_all([kh1, kh2, kh3, kh4, kh5, kh6])
        db.session.commit()

        # thêm data cho: LoaiPhong
        lp1 = LoaiPhong(tenLoai='phòng bình thường', donGia=500000, soNguoiToiDa=3)
        lp2 = LoaiPhong(tenLoai='phòng VIP', donGia=2000000, soNguoiToiDa=3)

        db.session.add_all([lp1, lp2])
        db.session.commit()

        # thêm data cho: Phong
        for i in range(0, 20):
            p = Phong(ma_loaiphong=1)
            db.session.add(p)
            db.session.commit()
        for i in range(0, 20):
            p = Phong(ma_loaiphong=2)
            db.session.add(p)
            db.session.commit()

        # thêm data cho: PhieuDatPhong
        pd1 = PhieuDatPhong(ngayNhan='2022-01-05', ngayTra='2022-01-07', ngayDat='2021-12-25',
                            trangThai='Đã nhận phòng', ma_taikhoan=2, ma_khachhang=1, ma_loaiphong=2, ma_phong=25)
        pd2 = PhieuDatPhong(ngayNhan='2022-05-01', ngayTra='2022-05-05', ngayDat='2022-04-20',
                            trangThai='Đã hủy', ma_taikhoan=2, ma_khachhang=2, ma_loaiphong=2, ma_phong=39)
        pd3 = PhieuDatPhong(ngayNhan='2022-11-01', ngayTra='2022-11-04', ngayDat='2022-10-10',
                            trangThai='Đã nhận phòng', ma_taikhoan=4, ma_khachhang=3, ma_loaiphong=1, ma_phong=1)
        pd4 = PhieuDatPhong(ngayNhan='2022-12-07', ngayTra='2022-12-10', ngayDat='2022-11-19',
                            trangThai='Chờ nhận phòng', ma_taikhoan=3, ma_khachhang=1, ma_loaiphong=1, ma_phong=4)
        pd5 = PhieuDatPhong(ngayNhan='2023-01-01', ngayTra='2023-01-05', ngayDat='2022-11-25',
                            trangThai='Chờ tiếp nhận', ma_taikhoan=4, ma_khachhang=6, ma_loaiphong=1)

        db.session.add_all([pd1, pd2, pd3, pd4, pd5])
        db.session.commit()

        # thêm data cho: PhieuThuePhong
        pt1 = PhieuThuePhong(ngayNhan='2022-01-05', ngayTra='2022-01-07', ngayLap='2022-01-05',
                             ma_taikhoan=3, ma_phong=25)  # là pd1
        pt2 = PhieuThuePhong(ngayNhan='2022-11-01', ngayTra='2022-11-04', ngayLap='2022-11-01',
                             ma_taikhoan=2, ma_phong=1)  # là pd3
        pt3 = PhieuThuePhong(ngayNhan='2022-11-20', ngayTra='2022-12-20', ngayLap='2022-11-20',
                             ma_taikhoan=4, ma_phong=7)  # thuê trực tiếp, ko đặt trc

        db.session.add_all([pt1, pt2, pt3])
        db.session.commit()

        # thêm data cho: PhieuThueChiTiet
        # pt1 có 1 ptct: ptct1 of KH1
        ptct1 = PhieuThueChiTiet(soNgay=3, ma_khachhang=1, ma_phieuthue=1)
        # pt2 có 3 ptct: ptct2,3,4 of KH3,2,4
        ptct2 = PhieuThueChiTiet(soNgay=4, ma_khachhang=3, ma_phieuthue=2)
        ptct3 = PhieuThueChiTiet(soNgay=4, ma_khachhang=2, ma_phieuthue=2)
        ptct4 = PhieuThueChiTiet(soNgay=4, ma_khachhang=4, ma_phieuthue=2)
        # pt3 có 2 ptct: ptct5,6 of KH5,6
        ptct5 = PhieuThueChiTiet(soNgay=31, ma_khachhang=5, ma_phieuthue=3)
        ptct6 = PhieuThueChiTiet(soNgay=31, ma_khachhang=6, ma_phieuthue=3)

        db.session.add_all([ptct1, ptct2, ptct3, ptct4, ptct5, ptct6])
        db.session.commit()

        # thêm data cho: TiLePhuThu
        tlpt1 = TiLePhuThu(mucTiLe=0, soNguoi=2)
        tlpt2 = TiLePhuThu(mucTiLe=0.25, soNguoi=3)
        db.session.add_all([tlpt1, tlpt2])
        db.session.commit()

        # thêm data cho: HoaDon
        hd1 = HoaDon(ngayNhan='2022-01-05', ngayTra='2022-01-07', ngayLap='2022-01-07', tongTien=9000000,
                     ma_taikhoan=4, ma_phieuthue=1, ma_phuthu=1)
        # hd1 of pt1; phòng 1 người, người nước ngoài: 3 * 2,000,000 * 1.5
        hd2 = HoaDon(ngayNhan='2022-11-01', ngayTra='2022-11-04', ngayLap='2022-11-04', tongTien=2500000,
                     ma_taikhoan=3, ma_phieuthue=2, ma_phuthu=2)
        # hd2 of pt2; phòng 3 người: 4 * 500,000 (1 + 0.25)

        db.session.add_all([hd1, hd2])
        db.session.commit()

        # hiện có phiếu đặt 4 chờ người nhận: phòng 4
        # phiệu đặt 5 chưa xếp phòng
        # phiếu thuê 3 còn người ở: phòng 7
