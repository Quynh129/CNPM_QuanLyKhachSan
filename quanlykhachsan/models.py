from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from quanlykhachsan import db, app
from enum import Enum as UserEnum
from flask_login import UserMixin
from datetime import datetime
import datetime as date_time
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


class KhachHang(BaseModel):
    __tablename__ = 'khachhang'
    hoTen = Column(String(50), nullable=False)
    CCCD = Column(String(50), nullable=False)
    soDienThoai = Column(String(50), nullable=False)
    quocTich = Column(String(50), nullable=False)
    fk_phieudat = relationship('PhieuDatPhong', backref='khachhang', lazy=False)
    fk_phieuthuechitiet = relationship('PhieuThuePhong', secondary='phieuthuechitiet', lazy='subquery',
                                       backref=backref('khachhang', lazy=True))


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
    ngayNhan = Column(DateTime, default=datetime.today())
    ngayTra = Column(DateTime, default=datetime.today())
    ngayDat = Column(DateTime, default=datetime.today())  # now: tạo phiếu đặt
    trangThai = Column(String(50), nullable=False)
    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id), nullable=False)
    ma_khachhang = Column(Integer, ForeignKey(KhachHang.id), nullable=False)
    ma_loaiphong = Column(Integer, ForeignKey(LoaiPhong.id), nullable=False)
    ma_phong = Column(Integer, ForeignKey(Phong.id))


HoaDonChiTiet = db.Table('hoadonchitiet',
                         Column('ma_phieuthue', Integer, ForeignKey('phieuthuephong.id'), primary_key=True),
                         Column('ma_tile', Integer, ForeignKey('tilephuthu.id'), primary_key=True))


class PhieuThuePhong(BaseModel):
    __tablename__ = 'phieuthuephong'
    ngayNhan = Column(DateTime, default=datetime.today())
    ngayTra = Column(DateTime, default=datetime.today())
    ngayLap = Column(DateTime, default=datetime.today())  # now: tạo phiếu thuê
    ngayThanhToan = Column(DateTime)  # now: thanh toán = ngayTrả (thông thường nếu ko trả trước)
    tongTien = Column(Float, default=0)
    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id), nullable=False)
    ma_phong = Column(Integer, ForeignKey(Phong.id), nullable=False)
    fk_phieuthuechitiet = relationship(KhachHang, secondary='phieuthuechitiet', lazy='subquery',
                                       backref=backref('phieuthuephong', lazy=True))
    fk_hoadonchitiet = relationship('TiLePhuThu', secondary='hoadonchitiet', lazy='subquery',
                                    backref=backref('phieuthuephong', lazy=True))
    # secondary: trung gian


class PhieuThueChiTiet(db.Model):
    __tablename__ = 'phieuthuechitiet'
    soNgay = Column(Integer, nullable=False)
    ma_khachhang = Column(Integer, ForeignKey(KhachHang.id), primary_key=True)
    ma_phieuthue = Column(Integer, ForeignKey(PhieuThuePhong.id), primary_key=True)


class TiLePhuThu(BaseModel):
    __tablename__ = 'tilephuthu'
    tenLoai = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    giaTri = Column(Float, default=0)
    # fk_hoadonchitiet: trung gian manyx2 là 2 chiều + ko có dlieu chung khác
    #   nên fk chỉ cần đặt ở 1 bảng parent --> fk ở phiếu thuê


if __name__ == '__main__':
    with app.app_context():
        date_format = "%Y/%m/%d"

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

        # thêm data cho: KhachHang
        kh1 = KhachHang(hoTen='Quý Ngài A', CCCD='079080012345', soDienThoai='0123456789', quocTich='Mỹ')
        kh2 = KhachHang(hoTen='Quý Cô B', CCCD='079190012345', soDienThoai='0123456789', quocTich='Việt Nam')
        kh3 = KhachHang(hoTen='Quý Ông C', CCCD='079050012345', soDienThoai='0123456789', quocTich='Việt Nam')
        kh4 = KhachHang(hoTen='Quý Bà D', CCCD='079155012345', soDienThoai='0123456789', quocTich='Việt Nam')
        kh5 = KhachHang(hoTen='Chàng Trai E', CCCD='079202012345', soDienThoai='0123456789', quocTich='Việt Nam')
        kh6 = KhachHang(hoTen='Cô Gái F', CCCD='079301012345', soDienThoai='0123456789', quocTich='Anh')

        db.session.add_all([kh1, kh2, kh3, kh4, kh5, kh6])
        db.session.commit()

        # thêm data cho: LoaiPhong
        lp1 = LoaiPhong(tenLoai='phòng bình thường', donGia=1000000, soNguoiToiDa=3)
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
        pd1 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/01/05', date_format),
                            ngayTra=date_time.datetime.strptime('2022/01/07', date_format),
                            ngayDat=date_time.datetime.strptime('2021/12/25', date_format),
                            trangThai='Đã nhận phòng', ma_taikhoan=2, ma_khachhang=1, ma_loaiphong=2, ma_phong=25)
        pd2 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/05/01', date_format),
                            ngayTra=date_time.datetime.strptime('2022/05/05', date_format),
                            ngayDat=date_time.datetime.strptime('2022/04/20', date_format),
                            trangThai='Đã hủy', ma_taikhoan=2, ma_khachhang=2, ma_loaiphong=2, ma_phong=39)
        pd3 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/11/01', date_format),
                            ngayTra=date_time.datetime.strptime('2022/11/04', date_format),
                            ngayDat=date_time.datetime.strptime('2022/10/10', date_format),
                            trangThai='Đã nhận phòng', ma_taikhoan=4, ma_khachhang=3, ma_loaiphong=1, ma_phong=1)
        pd4 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/12/07', date_format),
                            ngayTra=date_time.datetime.strptime('2022/12/10', date_format),
                            ngayDat=date_time.datetime.strptime('2022/11/19', date_format),
                            trangThai='Chờ nhận phòng', ma_taikhoan=3, ma_khachhang=1, ma_loaiphong=1, ma_phong=4)
        pd5 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2023/01/01', date_format),
                            ngayTra=date_time.datetime.strptime('2023/01/05', date_format),
                            ngayDat=date_time.datetime.strptime('2022/11/25', date_format),
                            trangThai='Chờ tiếp nhận', ma_taikhoan=4, ma_khachhang=6, ma_loaiphong=1)

        db.session.add_all([pd1, pd2, pd3, pd4, pd5])
        db.session.commit()

        # thêm data cho: PhieuThuePhong
        # -----Quy định ngày: thuê từ 1-3: 2 ngày
        # -----Quy định tiền: số ngày * tiền phòng [*1.5(có khách nước ngoài] [*1.25(>3 người)]
        # phiếu thuê 1 đã được thanh toán
        d_in_11 = date_time.datetime.strptime('2022/01/05', date_format)
        d_out_12 = date_time.datetime.strptime('2022/01/07', date_format)
        d_print_13 = date_time.datetime.strptime('2022/01/05', date_format)
        d_pay_14 = date_time.datetime.strptime('2022/01/07', date_format)
        pt1 = PhieuThuePhong(ngayNhan=d_in_11, ngayTra=d_out_12, ngayLap=d_print_13, ngayThanhToan=d_pay_14,
                             tongTien=abs(d_in_11-d_out_12).days*2000000*1.5,
                             ma_taikhoan=3, ma_phong=25)  # là pd1

        # phiếu thuê 2 đã được thanh toán
        d_in_21 = date_time.datetime.strptime('2022/11/01', date_format)
        d_out_22 = date_time.datetime.strptime('2022/11/04', date_format)
        d_print_23 = date_time.datetime.strptime('2022/01/05', date_format)
        d_pay_24 = date_time.datetime.strptime('2022/01/07', date_format)
        pt2 = PhieuThuePhong(ngayNhan=d_in_21, ngayTra=d_out_22, ngayLap=d_print_23, ngayThanhToan=d_pay_24,
                             tongTien=abs(d_in_21-d_out_22).days*1000000*1.25,
                             ma_taikhoan=2, ma_phong=1)  # là pd3

        # phiếu thuê 3 chưa được thanh toán, cài đặt ngày trả la today để khi khởi tạo csdl sẽ có phiếu cần thanh toán
        d_in_31 = datetime.today()+date_time.timedelta(days=-5)
        d_out_32 = datetime.today()
        d_print_33 = datetime.today()+date_time.timedelta(days=-5)
        pt3 = PhieuThuePhong(ngayNhan=d_in_31, ngayTra=d_out_32, ngayLap=d_print_33,
                             tongTien=abs(d_in_31-d_out_32).days*1000000*1.5,
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
        tlpt1 = TiLePhuThu(tenLoai='Quốc tịch', ten='Có người ngoại quốc', giaTri=1.5)
        tlpt2 = TiLePhuThu(tenLoai='Số người', ten='Trên 2 người', giaTri=1.25)
        db.session.add_all([tlpt1, tlpt2])
        db.session.commit()

        # thêm data cho: HoaDonChiTiet
        # -----Quy định: chỉ tạo khi thanh toán, có 2 phiê thuê đã thanh toán
        # Phiếu thuê 1: có người NN, KH=1 --> 1 hdct
        # Phiếu thuê 2: ko có người NN, KH=3 --> 1 hdct
        db.session.execute(HoaDonChiTiet.insert().values(ma_phieuthue=1, ma_tile=1))
        db.session.execute(HoaDonChiTiet.insert().values(ma_phieuthue=2, ma_tile=2))
        db.session.commit()

        # hiện có phiếu đặt 4 chờ người nhận: phòng 4
        # phiệu đặt 5 chưa xếp phòng
        # phiếu thuê 3 còn người ở: phòng 7
