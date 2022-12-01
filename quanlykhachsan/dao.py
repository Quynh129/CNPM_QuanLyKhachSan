import json
from quanlykhachsan import app
from quanlykhachsan.models import TaiKhoan, KhachHang, LoaiPhong, Phong, \
    PhieuDatPhong, PhieuThuePhong, PhieuThueChiTiet, TiLePhuThu
import hashlib


# PHẦN LOGIN
def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return TaiKhoan.query.filter(TaiKhoan.tenTaiKhoan.__eq__(username.strip()),
                                 TaiKhoan.matKhau.__eq__(password)).first()


def get_user_by_id(user_id):
    return TaiKhoan.query.get(user_id)
# -----kết thúc phần login-----
