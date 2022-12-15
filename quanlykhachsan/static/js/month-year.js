// gọi tới bởi trang thống kê
$(function thang_nam() {
    var nam = $('#year');
    var date = new Date();
    var cur = date.getFullYear();

    nam.append('<option value="">Năm</option>');
    for (i = cur; i >= 1900; i--) {
        nam.append('<option value="'+i+'">'+i+'</option>');
    };

    //Tháng tự động điền vào select
    var thang = $('#month');
    var date = new Date();

    var month=new Array();
    month[1]="Tháng 1";
    month[2]="Tháng 2";
    month[3]="Tháng 3";
    month[4]="Tháng 4";
    month[5]="Tháng 5";
    month[6]="Tháng 6";
    month[7]="Tháng 7";
    month[8]="Tháng 8";
    month[9]="Tháng 9";
    month[10]="Tháng 10";
    month[11]="Tháng 11";
    month[12]="Tháng 12";

    thang.append('<option value="">Tháng</option>');
    for (i = 1; i <= 12; i++) {
        thang.append('<option value="'+i+'">'+month[i]+'</option>');
    };

    $('#year, #month').change(function(){
        var y = document.getElementById('year');
        var m = document.getElementById('month');

        var year = y.options[y.selectedIndex].value;
        var month = m.options[m.selectedIndex].value;
    });
});