from flask import Flask, render_template, request, redirect, session, jsonify
import quanlykhachsan.dao
from quanlykhachsan import app, login
from quanlykhachsan import admin, dao
from flask_login import login_user, logout_user, login_required
from quanlykhachsan.decorators import annonymous_user, block_admin
from datetime import datetime
import datetime as date_time


def index():
    return render_template('trangChu.html')


# # # ----- ĐĂNG NHẬP - PHÂN QUYỀN -----
# gọi trang Đăng nhập
@annonymous_user
def login_my_user():
    err_msg = ''
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
        else:
            if not dao.get_username(username):
                err_msg = 'Không có tên đăng nhập trong hệ thống'
            else:
                err_msg = 'Mật khẩu không khớp'

    return render_template('dangNhap.html', err_msg=err_msg)


# ----- xử lý đăng nhập
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


# ----- xử lý đăng xuất
def logout_my_user():
    logout_user()
    return redirect('/dangNhap')


# # # ----- NGHIỆP VỤ CHỌN PHÒNG -----
# gọi trang Sơ đồ phòng
@login_required
@block_admin
def sodophong():
    ngaynhan = request.args.get('checkin')
    ngaytra = request.args.get('checkout')
    trangthai = request.values.get('activity')
    phong = dao.load_danhsachphong(ngaynhan=ngaynhan, ngaytra=ngaytra, trangthai=trangthai)

    date = date_time.datetime.today()
    pd = dao.load_phieudatphong()
    return render_template('soDoPhong.html', phong=phong, date=date, phieudatphong=pd)


# # # ----- NGHIỆP VỤ ĐẶT PHÒNG -----
# gọi trang Đặt phòng
@login_required
@block_admin
def datphong():
    kw = request.args.get('keyword')  # class's name html
    state = request.args.get('state')
    phieudatphong = dao.load_phieudatphong(kw=kw, state=state)
    khachhang = dao.load_khachhang()

    date_format = "%Y-%m-%d 00:00:00"
    date = date_time.datetime.today().strftime(date_format)
    date_pd = []  # [idphieudat][bool]
    i = 0

    for pdp in phieudatphong:
        date_pd.append([])
        for j in range(0, 2):
            if j == 0:
                date_pd[i].append(pdp.id)
            else:  # j==1
                if str(pdp.ngayNhan).__eq__(date):
                    date_pd[i].append(1)
                else:
                    date_pd[i].append(0)
        # print(date_pd[i])
        i += 1

    count_yc = 0
    count_thue = 0
    for pdp in phieudatphong:
        if pdp.trangThai.__eq__('Chờ tiếp nhận'):
            count_yc += 1
        if pdp.trangThai.__eq__('Chờ nhận phòng') and str(pdp.ngayNhan).__eq__(date):
            count_thue += 1

    return render_template('datPhong.html', phieudatphong=phieudatphong, khachhang=khachhang, date=date_pd,
                           yeucau=count_yc, thue=count_thue)


# gọi trang Yêu cầu đặt phòng (của KH)
# ----- Đặt phòng từ giao diện KH, ko có chọn mã phòng, dữ liệu phiếu đặt sẽ null ở mã phòng, mã tài khoản (nvien)
def yeucau():
    err_msg = ''
    flag = 0
    date_format = "%Y-%m-%d"
    # xử lý khi người dùng chọn tạo yêu cầu đặt phòng
    if request.method.__eq__('POST'):
        ngaynhan = request.form['checkin']
        ngaytra = request.form['checkout']
        d_in = date_time.datetime.strptime(ngaynhan, date_format)
        d_out = date_time.datetime.strptime(ngaytra, date_format)
        d_now = date_time.datetime.today()
        d_in_out = (d_out - d_in).days
        d_in_now = (d_in - d_now).days

        if (d_in_now >= 0) and (d_in_now <= 28):  # ngày nhận >= now, now: ngày 1, nhận: 2 --> d_in_now=0
            if d_in_out >= 0:
                hoten = request.form['cus_name']
                cccd = request.form['cus_cccd']
                sodienthoai = request.form['cus_phone']
                quoctich = request.form['cus_nation']

                kh = dao.get_khachhang_by_cccd(hoten, cccd)  # True: đã có KH này

                ngaydat = d_now
                trangthai = 'Chờ tiếp nhận'
                ma_loaiphong = request.form['type_room']  # trả về value

                try:
                    if kh:
                        ma_khachhang1 = dao.get_id_khachhang(hoten, cccd)
                        dao.upload_phieudat(flag=1, ngaynhan=ngaynhan, ngaydat=ngaydat, ngaytra=ngaytra,
                                            trangthai=trangthai,
                                            makhachhang=ma_khachhang1, maloaiphong=ma_loaiphong)
                    else:
                        dao.upload_khachhang(hoten=hoten, cccd=cccd, sodienthoai=sodienthoai, quoctich=quoctich)
                        ma_khachhang2 = dao.get_id_khachhang(hoten, cccd)
                        dao.upload_phieudat(flag=1, ngaynhan=ngaynhan, ngaydat=ngaydat, ngaytra=ngaytra,
                                            trangthai=trangthai,
                                            makhachhang=ma_khachhang2, maloaiphong=ma_loaiphong)
                    flag = 1
                    # return redirect('/')
                except:
                    err_msg = 'Lỗi hệ thống'
            else:
                err_msg = 'Lỗi! Ngày nhận phòng phải trước ngày trả phòng'
        else:
            err_msg = 'Lỗi! Ngày nhận phòng phải sau ngày hôm nay và không được quá 28 ngày kể từ ngày hôm nay'

    # print(err_msg)
    loaiphong = dao.load_loaiphong()
    return render_template('yeuCauDatPhong.html', loaiphong=loaiphong, err_msg=err_msg, flag=flag)


# gọi trang Chi tiết phiếu đặt
# ----- Đăt phòng từ giao diện Nvien: ko có dữ liệu null
# ----- 1. Phiếu đặt rỗng: chưa có id
@login_required
@block_admin
def chitietphieudat_null(phong_id):
    err_msg = ''
    date_format = "%Y-%m-%d"

    # phong = dao.get_phong_by_id(phong_id)
    loaiphong = dao.get_loaiphong_by_phongid(phong_id)  # tên loại + đơn giá

    # xử lý khi người dùng chọn tạo yêu cầu đặt phòng
    if request.method.__eq__('POST'):
        ngaynhan = request.form['checkin']
        ngaytra = request.form['checkout']
        d_in = date_time.datetime.strptime(ngaynhan, date_format)
        d_out = date_time.datetime.strptime(ngaytra, date_format)
        d_now = date_time.datetime.today()
        d_in_out = (d_out - d_in).days
        d_in_now = (d_in - d_now).days

        if (d_in_now >= 0) and (d_in_now <= 28):  # ngày nhận >= now, now: ngày 1, nhận: 2 --> d_in_now=0
            if d_in_out >= 0:
                hoten = request.form['cus_name']
                cccd = request.form['cus_cccd']
                sodienthoai = request.form['cus_phone']
                quoctich = request.form['cus_nation']

                kh = dao.get_khachhang_by_cccd(hoten, cccd)  # True: đã có KH này

                ngaydat = d_now
                trangthai = 'Chờ nhận phòng'
                ma_loaiphong = request.form['type_room']  # trả về value
                ma_phong = request.form['room']

                try:
                    if kh:
                        ma_khachhang1 = dao.get_id_khachhang(hoten, cccd)
                        dao.upload_phieudat(flag=2, ngaynhan=ngaynhan, ngaydat=ngaydat, ngaytra=ngaytra,
                                            trangthai=trangthai,
                                            makhachhang=ma_khachhang1, maloaiphong=ma_loaiphong, maphong=ma_phong)
                    else:
                        dao.upload_khachhang(hoten=hoten, cccd=cccd, sodienthoai=sodienthoai, quoctich=quoctich)
                        ma_khachhang2 = dao.get_id_khachhang(hoten, cccd)
                        dao.upload_phieudat(flag=2, ngaynhan=ngaynhan, ngaydat=ngaydat, ngaytra=ngaytra,
                                            trangthai=trangthai,
                                            makhachhang=ma_khachhang2, maloaiphong=ma_loaiphong, maphong=ma_phong)

                    return redirect('/datPhong')
                except:
                    err_msg = 'Lỗi hệ thống'
            else:
                err_msg = 'Lỗi! Ngày nhận phòng phải trước ngày trả phòng'
        else:
            err_msg = 'Lỗi! Ngày nhận phòng phải sau ngày hôm nay'

    # loaiphong = dao.load_loaiphong()

    return render_template('chiTietPhieuDatRong.html', loaiphong=loaiphong, err_msg=err_msg,
                           phong_id=phong_id)


# ----- 2. Phiếu đặt đã có id
@login_required
@block_admin
def chitietphieudat_data(phieudatphong_id):
    err_msg = ''
    pd = dao.get_phieudat_by_id(phieudatphong_id)
    khachhang = dao.load_khachhang()
    loaiphong = dao.load_loaiphong()

    query = dao.load_phongTrong(pd.ngayNhan, pd.ngayTra)
    query = sorted(query, key=lambda t: t[0])
    phongtrong = list()
    for q in query:
        if q[1] == pd.ma_loaiphong:
            phongtrong.append(q[0])
    phongtrong = sorted(phongtrong)

    if request.method.__eq__('POST'):
        trangthai = request.form['state']  # trả về value

        if trangthai == 'Chờ nhận phòng':
            ma_phong = request.form['room']

        if trangthai == 'Chờ nhận phòng' and not ma_phong:
            err_msg = "Cần nhập mã phòng"
            return render_template('chiTietPhieuDat.html', phieudatphong=pd, khachhang=khachhang, loaiphong=loaiphong,
                                   err_msg=err_msg)
        else:
            try:
                if trangthai == 'Chờ nhận phòng':
                    dao.update_phieudat(phieudatphong_id, trangthai=trangthai, maphong=ma_phong)
                # if trangthai == 'Đã hủy' and ma_phong:
                #     dao.update_phieudat(phieudatphong_id, trangthai=trangthai, maphong=ma_phong)
                # if trangthai == 'Đã hủy' and not ma_phong:
                #     dao.update_phieudat(phieudatphong_id, trangthai=trangthai)
                # if trangthai == 'Chờ phản hồi':
                else:
                    dao.update_phieudat(phieudatphong_id, trangthai=trangthai)
                return redirect('/datPhong')
            except:
                err_msg = 'Lỗi hệ thống'

    return render_template('chiTietPhieuDat.html', phieudatphong=pd, khachhang=khachhang, loaiphong=loaiphong,
                           phongtrong=phongtrong, err_msg=err_msg)


# # # ----- NGHIỆP VỤ THUÊ PHÒNG - THANH TOÁN -----
# gọi trang Thuê phòng
@login_required
@block_admin
def thuephong():
    kw = request.args.get('keyword')  # class's name html
    state = request.args.get('state')
    phieuthuephong = dao.load_phieuthuephong(kw=kw, state=state)
    phieuthuechitiet = dao.load_phieuthuechitiet()
    khachhang = dao.load_khachhang()

    date_format = "%Y-%m-%d 00:00:00"
    date = date_time.datetime.today().strftime(date_format)
    date_pt = []  # [idphieuthue][bool]
    i = 0

    for ptp in phieuthuephong:
        date_pt.append([])
        for j in range(0,2):
            if j == 0:
                date_pt[i].append(ptp.id)
            else:  # j==1
                if str(ptp.ngayTra).__eq__(date):
                    date_pt[i].append(1)
                else:
                    date_pt[i].append(0)
            # print(date_pt[i][0])
        i += 1

    count_hd = 0
    for ptp in phieuthuephong:
        if not ptp.trangThai and str(ptp.ngayTra).__eq__(date):
            count_hd += 1

    return render_template('thuePhong.html', phieuthuephong=phieuthuephong, phieuthuechitiet=phieuthuechitiet,
                           khachhang=khachhang, date=date_pt, hoadon=count_hd)


# gọi trang Chi tiết phiếu thue
# ----- 1. Từ sơ đồ phòng: rỗng
@login_required
@block_admin
def chitietphieuthue_null(phong_id):
    err_msg = ''
    date_format = "%Y-%m-%d"

    loaiphong = dao.get_loaiphong_by_phongid(phong_id=phong_id)  # tên loại + đơn giá
    soluong = range(loaiphong[0][3])  # lấy slg maxKH để tạo form KH
    tilephuthu = dao.load_tilephuthu()

    if request.method.__eq__('POST'):
        ngaynhan = date_time.datetime.today()
        ngaytra = request.form['checkout']
        d_out = date_time.datetime.strptime(ngaytra, date_format)
        d_in_out = (d_out - ngaynhan).days

        if d_in_out >= 0:
            ngaylap = date_time.datetime.today()
            songay = d_in_out + 1
            dongia = request.form['type_room']

            tile = 1
            matile = []  # lấy id truyền vào phieuthue_tile
            # tlpt = request.form.getlist('multirate')  # lấy list

            ma_phong = int(request.form['room'])

            hoten = []
            cccd = []
            sodienthoai = []
            quoctich = []
            kh = []  # kiểm tra đã có KH trong csdl
            id_kh = []  # lấy id truyền vào phieuthue_chitiet

            count = 0
            ngoaiquoc = 1

            for i in soluong:
                if request.form['cus_name_{}'.format(i)]:  # kiểm tra có nhập thông tin KH đó ko
                    hoten.append(request.form['cus_name_{}'.format(i)])
                    cccd.append(request.form['cus_cccd_{}'.format(i)])
                    sodienthoai.append(request.form['cus_phone_{}'.format(i)])
                    quoctich.append(request.form['cus_nation_{}'.format(i)])
                    # print(quoctich[i])
                    if quoctich[i] == "Việt Nam":
                        ngoaiquoc = 0
                    count += 1

            for i in soluong:
                if request.form['cus_name_{}'.format(i)]:
                    if dao.get_khachhang_by_cccd(hoten[i], cccd[i]):  # kiểm tra KH đã có trong hệ thống / chưa
                        kh.append(1)  # True: đã có KH này
                    else:
                        kh.append(0)

            if ngoaiquoc == 1:
                tile *= 1.5
                matile.append(1)
            if count > 2:  # nhiều hơn 2 KH, phụ thu 25%
                tile *= 1.25
                matile.append(2)

            try:
                for i in soluong:  # thêm KH
                    if request.form['cus_name_{}'.format(i)]:
                        if kh[i] == 0:  # KH i chưa có thì thêm
                            dao.upload_khachhang(hoten=hoten[i], cccd=cccd[i],
                                                 sodienthoai=sodienthoai[i], quoctich=quoctich[i])  # add CSDL
                        id_kh.append(dao.get_id_khachhang(hoten[i], cccd[i]))  # get id

                # tạo phiếu thuê + phiếu thuê chi tiết
                dao.upload_phieuthue(ngaynhan=ngaynhan, ngaytra=ngaytra, ngaylap=ngaylap,
                                     songay=songay, dongia=dongia, tile=tile, matile=matile,
                                     maphong=ma_phong, makhachhang=id_kh)

                return redirect('/thuePhong')
            except:
                err_msg = 'Lỗi hệ thống'
        else:
            err_msg = 'Lỗi! Ngày nhận phòng phải trước ngày trả phòng'

    return render_template('chiTietPhieuthueRong.html', loaiphong=loaiphong, err_msg=err_msg,
                           phong_id=phong_id, soluong=soluong, tilephuthu=tilephuthu)


# ----- 2.Từ dsach đặt
@login_required
@block_admin
def chitietphieudattruoc(phieudatphong_id):
    err_msg = ''
    date_format = "%Y-%m-%d"

    phieudattruoc = dao.get_phieudat_by_id(phieudatphong_id)
    kh = dao.get_khachhang_by_id(phieudattruoc.ma_khachhang)  # lấy KH truyền vào thông tin KH đầu tiên
    # print('ma loai phong: {}'.format(phieudattruoc.ma_loaiphong))

    loaiphong = dao.get_loaiphong_by_phongid(phong_id=phieudattruoc.ma_phong)  # tên loại + đơn giá
    soluong = range(loaiphong[0][3])  # lấy slg maxKH để tạo form KH
    # print('so luong {}'.format(soluong))

    if request.method.__eq__('POST'):
        ngaynhan = phieudattruoc.ngayNhan
        ngaytra = phieudattruoc.ngayTra
        ngaylap = date_time.datetime.today()
        ma_phong = phieudattruoc.ma_phong

        d_in = int(str(phieudattruoc.ngayNhan)[8:10])
        d_out = int(str(phieudattruoc.ngayTra)[8:10])

        songay = (d_out - d_in) + 1
        dongia = int(loaiphong[0][2])

        tile = 1
        matile = []  # lấy id truyền vào phieuthue_tile

        hoten = []
        cccd = []
        sodienthoai = []
        quoctich = []
        kh = []  # kiểm tra đã có KH trong csdl
        id_kh = []  # lấy id truyền vào ptct
        count = 0
        ngoaiquoc = 1

        for i in soluong:
            if request.form['cus_name_{}'.format(i)]:  # kiểm tra có nhập thông tin KH đó ko
                hoten.append(request.form['cus_name_{}'.format(i)])
                cccd.append(request.form['cus_cccd_{}'.format(i)])
                sodienthoai.append(request.form['cus_phone_{}'.format(i)])
                quoctich.append(request.form['cus_nation_{}'.format(i)])
                # print(quoctich[i])
                if quoctich[i] == "Việt Nam":
                    ngoaiquoc = 0
                count += 1

        for i in soluong:
            if request.form['cus_name_{}'.format(i)]:
                if dao.get_khachhang_by_cccd(hoten[i], cccd[i]):  # kiểm tra KH đã có trong hệ thống / chưa
                    kh.append(1)  # True: đã có KH này
                else:
                    kh.append(0)

        if ngoaiquoc == 1:
            tile *= 1.5
            matile.append(1)
        if count > 2:  # nhiều hơn 2 KH, phụ thu 25%
            tile *= 1.25
            matile.append(2)

        try:
            for i in soluong:  # thêm KH
                if request.form['cus_name_{}'.format(i)]:
                    if kh[i] == 0:  # KH i chưa có thì thêm
                        dao.upload_khachhang(hoten=hoten[i], cccd=cccd[i],
                                             sodienthoai=sodienthoai[i], quoctich=quoctich[i])  # add CSDL
                    id_kh.append(dao.get_id_khachhang(hoten[i], cccd[i]))  # get id

            # tạo phiếu thuê + phiếu thuê chi tiết
            dao.upload_phieuthue(ngaynhan=ngaynhan, ngaytra=ngaytra, ngaylap=ngaylap,
                                 songay=songay, dongia=dongia, tile=tile, matile=matile,
                                 maphong=ma_phong, makhachhang=id_kh)
            trangthai = 'Đã nhận phòng'
            dao.update_phieudat(idphieudat=phieudatphong_id, trangthai=trangthai)

            return redirect('/thuePhong')
        except:
            err_msg = 'Lỗi hệ thống'

    return render_template('chiTietPhieuthueDatTruoc.html', idPhieuDat=phieudatphong_id, phieudattruoc=phieudattruoc,
                           khachhang=kh, loaiphong=loaiphong, soluong=soluong, err_msg=err_msg)


# ----- 3.Từ dsach phiếu thuê (chi tiết / thanh toán)
@login_required
@block_admin
def chitietphieuthue(phieuthuephong_id):
    err_msg = ''
    pt = dao.get_phieuthue_by_id(phieuthuephong_id)
    khpt = dao.get_chitietphieuthue_by_id(phieuthuephong_id)
    khachhang = dao.load_khachhang()
    loaiphong = dao.get_loaiphong_by_phongid(phong_id=pt.ma_phong)

    ngaythanhtoan = date_time.datetime.today()

    if request.method.__eq__('POST'):
        try:
            # print("thử lưu")
            dao.update_thanhtoan(idphieuthue=phieuthuephong_id, ngaythanhtoan=ngaythanhtoan)
            return redirect('/thuePhong')
        except:
            err_msg = 'Lỗi hệ thống'

    # print(err_msg)
    return render_template('chiTietPhieuThue_HD.html', phieuthuephong=pt, loaiphong=loaiphong,
                           khachhangphieuthue=khpt, khachhang=khachhang,
                           ngaythanhtoan=ngaythanhtoan,
                           err_msg=err_msg)

