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

    def __str__(self):
        return self.hoTen


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
    ngayDat = Column(DateTime, default=datetime.today())  # now: t???o phi???u ?????t
    trangThai = Column(String(50), nullable=False)
    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id))
    ma_khachhang = Column(Integer, ForeignKey(KhachHang.id), nullable=False)
    ma_loaiphong = Column(Integer, ForeignKey(LoaiPhong.id), nullable=False)
    ma_phong = Column(Integer, ForeignKey(Phong.id))


class PhieuThuePhong(BaseModel):
    __tablename__ = 'phieuthuephong'
    ngayNhan = Column(DateTime, default=datetime.today())
    ngayTra = Column(DateTime, default=datetime.today())
    ngayLap = Column(DateTime, default=datetime.today())  # now: t???o phi???u thu??
    ngayThanhToan = Column(DateTime)  # now: thanh to??n = ngayTr??? (th??ng th?????ng n???u ko tr??? tr?????c)
    trangThai = Column(Boolean, default=False)

    soNgay = Column(Integer, nullable=False)
    donGia = Column(Float, default=0)
    tiLe = Column(Float, default=1)  # l?? t??ch c??c t??? l???
    # T???ng ti???n = soNgay * donGia * tiLe

    ma_taikhoan = Column(Integer, ForeignKey(TaiKhoan.id), nullable=False)
    ma_phong = Column(Integer, ForeignKey(Phong.id), nullable=False)

    fk_phieuthuechitiet = relationship('KhachHang', secondary='phieuthuechitiet', lazy='subquery',
                                       backref=backref('phieuthuephong', lazy=True))
    fk_phieuthuetile = relationship('TiLePhuThu', secondary='phieuthuetile', lazy='subquery',
                                    backref=backref('phieuthuephong', lazy=True))
    # secondary: trung gian


class PhieuThueChiTiet(db.Model):
    __tablename__ = 'phieuthuechitiet'
    ma_khachhang = Column(Integer, ForeignKey(KhachHang.id), primary_key=True)
    ma_phieuthue = Column(Integer, ForeignKey(PhieuThuePhong.id), primary_key=True)


class TiLePhuThu(BaseModel):
    __tablename__ = 'tilephuthu'
    tenLoai = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    giaTri = Column(Float, default=0)


class PhieuThueTiLe(db.Model):
    __tablename__ = 'phieuthuetile'
    ma_tile = Column(Integer, ForeignKey(TiLePhuThu.id), primary_key=True)
    ma_phieuthue = Column(Integer, ForeignKey(PhieuThuePhong.id), primary_key=True)


if __name__ == '__main__':
    with app.app_context():
        date_format = "%Y/%m/%d"

        # t???o to??n b??? b???ng
        db.create_all()

        # th??m data cho: TaiKhoan
        password_0 = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        u1 = TaiKhoan(tenTaiKhoan='admin', matKhau=password_0, phanQuyen=PhanQuyen.ADMIN,
                      hoTen='Qu???n tr??? vi??n', soDienThoai='0123456789')
        password_1 = str(hashlib.md5('1954052077'.encode('utf-8')).hexdigest())
        u2 = TaiKhoan(tenTaiKhoan='HP', matKhau=password_1,
                      hoTen='Cao Ho??ng Ph?????ng', soDienThoai='0123456789')
        password_2 = str(hashlib.md5('1954052080'.encode('utf-8')).hexdigest())
        u3 = TaiKhoan(tenTaiKhoan='HQ', matKhau=password_2,
                      hoTen='H???a L?? Nh?? Qu???nh', soDienThoai='0123456789')
        password_3 = str(hashlib.md5('1954052081'.encode('utf-8')).hexdigest())
        u4 = TaiKhoan(tenTaiKhoan='NQ', matKhau=password_3,
                      hoTen='Nguy???n Th??? Nh?? Qu???nh', soDienThoai='0123456789')

        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        # th??m data cho: KhachHang
        kh1 = KhachHang(hoTen='Qu?? Ng??i A', CCCD='079080012345', soDienThoai='0123456789', quocTich='United States')
        kh2 = KhachHang(hoTen='Qu?? C?? B', CCCD='079190012345', soDienThoai='0123456789', quocTich='Vi???t Nam')
        kh3 = KhachHang(hoTen='Qu?? ??ng C', CCCD='079050012345', soDienThoai='0123456789', quocTich='Vi???t Nam')
        kh4 = KhachHang(hoTen='Qu?? B?? D', CCCD='079155012345', soDienThoai='0123456789', quocTich='Vi???t Nam')
        kh5 = KhachHang(hoTen='Ch??ng Trai E', CCCD='079202012345', soDienThoai='0123456789', quocTich='Vi???t Nam')
        kh6 = KhachHang(hoTen='C?? G??i F', CCCD='079301012345', soDienThoai='0123456789', quocTich='United Kingdom')

        db.session.add_all([kh1, kh2, kh3, kh4, kh5, kh6])
        db.session.commit()

        # th??m data cho: LoaiPhong
        lp1 = LoaiPhong(tenLoai='Ph??ng b??nh th?????ng', donGia=1000000, soNguoiToiDa=3)
        lp2 = LoaiPhong(tenLoai='Ph??ng VIP', donGia=2000000, soNguoiToiDa=3)

        db.session.add_all([lp1, lp2])
        db.session.commit()

        # th??m data cho: Phong
        for i in range(0, 20):
            p = Phong(ma_loaiphong=1)
            db.session.add(p)
            db.session.commit()
        for i in range(0, 20):
            p = Phong(ma_loaiphong=2)
            db.session.add(p)
            db.session.commit()

        # th??m data cho: PhieuDatPhong
        pd1 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/01/05', date_format),
                            ngayTra=date_time.datetime.strptime('2022/01/07', date_format),
                            ngayDat=date_time.datetime.strptime('2021/12/25', date_format),
                            trangThai='???? nh???n ph??ng', ma_taikhoan=2, ma_khachhang=1, ma_loaiphong=2, ma_phong=25)
        pd2 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/05/01', date_format),
                            ngayTra=date_time.datetime.strptime('2022/05/05', date_format),
                            ngayDat=date_time.datetime.strptime('2022/04/20', date_format),
                            trangThai='???? h???y', ma_taikhoan=2, ma_khachhang=2, ma_loaiphong=2, ma_phong=39)
        pd3 = PhieuDatPhong(ngayNhan=date_time.datetime.strptime('2022/11/01', date_format),
                            ngayTra=date_time.datetime.strptime('2022/11/04', date_format),
                            ngayDat=date_time.datetime.strptime('2022/10/10', date_format),
                            trangThai='???? nh???n ph??ng', ma_taikhoan=4, ma_khachhang=3, ma_loaiphong=1, ma_phong=1)
        # phi???u ?????t trc, ???? ???????c ch???n ph??ng, ng??y nh???n l?? now, tr??? sau 5 ng??y, ?????t t??? 5 ng??y tr?????c
        # test l???p phi???u thu??
        pd4 = PhieuDatPhong(ngayNhan=date_time.datetime.today().strftime("%Y-%m-%d 00:00:00"),
                            ngayTra=datetime.today() + date_time.timedelta(days=5),
                            ngayDat=datetime.today() + date_time.timedelta(days=-5),
                            trangThai='Ch??? nh???n ph??ng', ma_taikhoan=3, ma_khachhang=1, ma_loaiphong=1, ma_phong=4)
        # phi???u m???i ?????t h??m nay
        # test c???p nh???t phi???u ?????t
        pd5 = PhieuDatPhong(ngayNhan=datetime.today() + date_time.timedelta(days=5),
                            ngayTra=datetime.today() + date_time.timedelta(days=10),
                            ngayDat=datetime.today(),
                            trangThai='Ch??? ti???p nh???n', ma_khachhang=6, ma_loaiphong=1)

        db.session.add_all([pd1, pd2, pd3, pd4, pd5])
        db.session.commit()

        # th??m data cho: PhieuThuePhong
        # -----Quy ?????nh ng??y: thu?? t??? 1-3: 2 ng??y
        # -----Quy ?????nh ti???n: s??? ng??y * ti???n ph??ng [*1.5(c?? kh??ch n?????c ngo??i] [*1.25(>3 ng?????i)]
        # phi???u thu?? 1 ???? ???????c thanh to??n
        d_in_11 = date_time.datetime.strptime('2022/01/05', date_format)
        d_out_12 = date_time.datetime.strptime('2022/01/07', date_format)
        d_print_13 = date_time.datetime.strptime('2022/01/05', date_format)  # = d_in
        d_pay_14 = date_time.datetime.strptime('2022/01/07', date_format)  # = d_out
        pt1 = PhieuThuePhong(ngayNhan=d_in_11, ngayTra=d_out_12, ngayLap=d_print_13, ngayThanhToan=d_pay_14,
                             soNgay=abs(d_in_11 - d_out_12).days, donGia=2000000, tiLe=1 * 1.5,
                             trangThai=True, ma_taikhoan=3, ma_phong=25)  # l?? pd1

        # phi???u thu?? 2 ???? ???????c thanh to??n
        d_in_21 = date_time.datetime.strptime('2022/11/01', date_format)
        d_out_22 = date_time.datetime.strptime('2022/11/04', date_format)
        d_print_23 = date_time.datetime.strptime('2022/11/01', date_format)
        d_pay_24 = date_time.datetime.strptime('2022/11/04', date_format)
        pt2 = PhieuThuePhong(ngayNhan=d_in_21, ngayTra=d_out_22, ngayLap=d_print_23, ngayThanhToan=d_pay_24,
                             soNgay=abs(d_in_21 - d_out_22).days, donGia=1000000, tiLe=1.25 * 1,
                             trangThai=True, ma_taikhoan=2, ma_phong=1)  # l?? pd3

        # phi???u thu?? 3 ch??a ???????c thanh to??n, c??i ?????t ng??y tr??? la today ????? khi kh???i t???o csdl s??? c?? phi???u c???n thanh to??n
        # test l???p h??a ????n
        d_in_31 = datetime.today() + date_time.timedelta(days=-5)
        d_out_32 = date_time.datetime.today().strftime("%Y-%m-%d 00:00:00")
        d_print_33 = datetime.today() + date_time.timedelta(days=-5)
        pt3 = PhieuThuePhong(ngayNhan=d_in_31, ngayTra=d_out_32, ngayLap=d_print_33,
                             soNgay=5, donGia=1000000, tiLe=1 * 1.5,
                             ma_taikhoan=4, ma_phong=7)  # thu?? tr???c ti???p, ko ?????t trc

        # 1 lo???t phi???u ???? thanh to??n (test th???ng k??) (ko c?? phi???u ?????t)
        # pt4, 5: c?? KH NN; pt 6,7: =3KH
        d_in_41 = date_time.datetime.strptime('2022/02/05', date_format)
        d_out_42 = date_time.datetime.strptime('2022/02/07', date_format)
        d_print_43 = date_time.datetime.strptime('2022/02/05', date_format)  # = d_in
        d_pay_44 = date_time.datetime.strptime('2022/02/07', date_format)  # = d_out
        pt4 = PhieuThuePhong(ngayNhan=d_in_41, ngayTra=d_out_42, ngayLap=d_print_43, ngayThanhToan=d_pay_44,
                             soNgay=abs(d_in_41 - d_out_42).days, donGia=1000000, tiLe=1 * 1.5,
                             trangThai=True, ma_taikhoan=3, ma_phong=19)

        d_in_51 = date_time.datetime.strptime('2022/05/05', date_format)
        d_out_52 = date_time.datetime.strptime('2022/05/07', date_format)
        d_print_53 = date_time.datetime.strptime('2022/05/05', date_format)  # = d_in
        d_pay_54 = date_time.datetime.strptime('2022/05/07', date_format)  # = d_out
        pt5 = PhieuThuePhong(ngayNhan=d_in_51, ngayTra=d_out_52, ngayLap=d_print_53, ngayThanhToan=d_pay_54,
                             soNgay=abs(d_in_51 - d_out_52).days, donGia=2000000, tiLe=1 * 1.5,
                             trangThai=True, ma_taikhoan=3, ma_phong=35)

        d_in_61 = date_time.datetime.strptime('2022/09/01', date_format)
        d_out_62 = date_time.datetime.strptime('2022/09/04', date_format)
        d_print_63 = date_time.datetime.strptime('2022/09/01', date_format)
        d_pay_64 = date_time.datetime.strptime('2022/09/04', date_format)
        pt6 = PhieuThuePhong(ngayNhan=d_in_61, ngayTra=d_out_62, ngayLap=d_print_63, ngayThanhToan=d_pay_64,
                             soNgay=abs(d_in_61 - d_out_62).days, donGia=2000000, tiLe=1.25 * 1,
                             trangThai=True, ma_taikhoan=2, ma_phong=31)

        d_in_71 = date_time.datetime.strptime('2022/08/11', date_format)
        d_out_72 = date_time.datetime.strptime('2022/08/14', date_format)
        d_print_73 = date_time.datetime.strptime('2022/08/11', date_format)
        d_pay_74 = date_time.datetime.strptime('2022/08/14', date_format)
        pt7 = PhieuThuePhong(ngayNhan=d_in_71, ngayTra=d_out_72, ngayLap=d_print_73, ngayThanhToan=d_pay_74,
                             soNgay=abs(d_in_71 - d_out_72).days, donGia=1000000, tiLe=1.25 * 1,
                             trangThai=True, ma_taikhoan=2, ma_phong=12)

        db.session.add_all([pt1, pt2, pt4, pt5, pt6, pt7, pt3])
        db.session.commit()

        # th??m data cho: PhieuThueChiTiet
        # pt1 c?? 1 ptct: ptct1 of KH1
        ptct1 = PhieuThueChiTiet(ma_khachhang=1, ma_phieuthue=1)
        # pt2 c?? 3 ptct: ptct2,3,4 of KH3,2,4
        ptct2 = PhieuThueChiTiet(ma_khachhang=3, ma_phieuthue=2)
        ptct3 = PhieuThueChiTiet(ma_khachhang=2, ma_phieuthue=2)
        ptct4 = PhieuThueChiTiet(ma_khachhang=4, ma_phieuthue=2)
        # pt3 c?? 2 ptct: ptct5,6 of KH5,6
        ptct5 = PhieuThueChiTiet(ma_khachhang=5, ma_phieuthue=3)
        ptct6 = PhieuThueChiTiet(ma_khachhang=6, ma_phieuthue=3)
        # pt4
        ptct7 = PhieuThueChiTiet(ma_khachhang=1, ma_phieuthue=4)
        ptct8 = PhieuThueChiTiet(ma_khachhang=2, ma_phieuthue=4)
        # pt5
        ptct9 = PhieuThueChiTiet(ma_khachhang=1, ma_phieuthue=5)
        # pt6
        ptct10 = PhieuThueChiTiet(ma_khachhang=3, ma_phieuthue=6)
        ptct11 = PhieuThueChiTiet(ma_khachhang=2, ma_phieuthue=6)
        ptct12 = PhieuThueChiTiet(ma_khachhang=4, ma_phieuthue=6)
        # pt7
        ptct13 = PhieuThueChiTiet(ma_khachhang=3, ma_phieuthue=7)
        ptct14 = PhieuThueChiTiet(ma_khachhang=2, ma_phieuthue=7)
        ptct15 = PhieuThueChiTiet(ma_khachhang=4, ma_phieuthue=7)

        db.session.add_all(
            [ptct1, ptct2, ptct3, ptct4, ptct5, ptct6, ptct7, ptct8, ptct9, ptct10, ptct11, ptct12, ptct13, ptct14,
             ptct15])
        db.session.commit()

        # th??m data cho: TiLePhuThu
        tlpt1 = TiLePhuThu(tenLoai='Qu???c t???ch', ten='C?? ng?????i ngo???i qu???c', giaTri=1.5)
        tlpt2 = TiLePhuThu(tenLoai='S??? ng?????i', ten='Tr??n 2 ng?????i', giaTri=1.25)
        db.session.add_all([tlpt1, tlpt2])
        db.session.commit()

        # th??m data cho: phieuthuetile
        # Phi???u thu?? 1: c?? ng?????i NN, KH=1 --> 1 hdct
        # Phi???u thu?? 2: ko c?? ng?????i NN, KH=3 --> 1 hdct
        # Phi???u thu?? 3: c?? ng?????i NN, KH=2 --> 1 hdct
        pttl1 = PhieuThueTiLe(ma_phieuthue=1, ma_tile=1)
        pttl2 = PhieuThueTiLe(ma_phieuthue=2, ma_tile=2)
        pttl3 = PhieuThueTiLe(ma_phieuthue=3, ma_tile=1)
        pttl4 = PhieuThueTiLe(ma_phieuthue=4, ma_tile=1)
        pttl5 = PhieuThueTiLe(ma_phieuthue=5, ma_tile=1)
        pttl6 = PhieuThueTiLe(ma_phieuthue=6, ma_tile=2)
        pttl7 = PhieuThueTiLe(ma_phieuthue=7, ma_tile=2)
        db.session.add_all([pttl1, pttl2, pttl3, pttl4, pttl5, pttl6, pttl7])
        db.session.commit()

        # hi???n c?? phi???u ?????t 4 ch??? ng?????i nh???n: ph??ng 4
        # phi???u ?????t 5 ch??a x???p ph??ng
        # phi???u thu?? 3 c??n ng?????i ???: ph??ng 7
