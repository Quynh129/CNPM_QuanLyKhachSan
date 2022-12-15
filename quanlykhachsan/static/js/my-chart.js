function thongKeDoanhThu(labels, data1, data2) {
    const ctx = document.getElementById('thongKe_DoanhThu');
    new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets:
          [
              {
                label: 'Doanh thu',
                data: data1,
                backgroundColor: "tomato",
                borderWidth: 1,
                order: 0
              },
              {
                label: 'Số lượt thuê',
                data: data2,
                backgroundColor: "blue",
                borderWidth: 1,
                type: 'line',
                order: 1
              }
          ]
        },

        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
    });
}

function thongKeTanSuat(labels, data) {
    const ctx = document.getElementById('thongKe_TanSuat');
    new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Tần suất sử dụng phòng',
            data: data,
            borderWidth: 1
          }]
        },

        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
    });
}

