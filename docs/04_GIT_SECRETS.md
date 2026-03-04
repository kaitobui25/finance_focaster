
Để CI/CD chạy thành công, bạn cần cấu hình các biến môi trường ẩn (Secrets) trên GitHub. Dưới đây là hướng dẫn chi tiết từng bước để tạo và thêm `DOCKERHUB_USERNAME` cùng `DOCKERHUB_TOKEN`:

### Phần 1: Tạo Access Token trên Docker Hub

Nên dùng Access Token thay vì mật khẩu gốc của tài khoản Docker Hub để đảm bảo an toàn (có thể dễ dàng thu hồi nếu bị lộ).

1. Truy cập vào [Docker Hub](https://hub.docker.com/) và đăng nhập vào tài khoản của bạn (ví dụ: `kaitobui`).
2. Nhấn vào ảnh đại diện (Avatar) của bạn ở góc trên bên phải, chọn **Account settings**.
3. Ở menu bên trái, chọn phần **Security** (hoặc **Personal Access Tokens** tùy giao diện mới/cũ).
4. Nhấn nút **New Access Token**.
5. Điền thông tin:
* **Access Token Description**: Đặt tên gợi nhớ, ví dụ: `GitHub Actions CI/CD`.
* **Access permissions**: Chọn `Read & Write` (để GitHub Actions có quyền tải lên image mới).


6. Nhấn **Generate**.
7. **QUAN TRỌNG:** Sao chép (Copy) đoạn mã token vừa hiện ra và lưu tạm vào đâu đó. *Lưu ý: Docker Hub chỉ hiển thị token này MỘT LẦN DUY NHẤT. Nếu quên, bạn sẽ phải xóa đi và tạo lại.*

---

### Phần 2: Cấu hình Secrets trên GitHub

Bây giờ, bạn sẽ mang Username và Token vừa tạo lên kho lưu trữ (repository) GitHub của dự án `finance_forecaster`.

1. Truy cập vào trang Repository dự án của bạn trên GitHub.
2. Nhấn vào tab **Settings** (biểu tượng bánh răng ở thanh menu trên cùng của repo).
3. Nhìn sang thanh menu bên trái, cuộn xuống mục **Security**, chọn **Secrets and variables** > **Actions**.
4. Ở trang hiện ra, bạn sẽ thấy phần *Repository secrets*. Nhấn vào nút xanh **New repository secret**.
5. **Thêm biến thứ nhất (Username):**
* **Name**: `DOCKERHUB_USERNAME`
* **Secret**: Nhập tên đăng nhập Docker Hub của bạn (ví dụ: `kaitobui`).
* Nhấn **Add secret**.


6. Nhấn **New repository secret** một lần nữa để **thêm biến thứ hai (Token):**
* **Name**: `DOCKERHUB_TOKEN`
* **Secret**: Dán (Paste) đoạn mã Access Token bạn vừa copy ở Docker Hub (Phần 1) vào đây.
* Nhấn **Add secret**.



---

### Phần 3: Kiểm tra kết quả

Sau khi thêm xong, bạn sẽ thấy 2 biến `DOCKERHUB_USERNAME` và `DOCKERHUB_TOKEN` nằm trong danh sách *Repository secrets*.

* Bắt đầu từ bây giờ, mỗi khi bạn `git push` code mới lên nhánh `main`, hãy chuyển sang tab **Actions** trên GitHub để xem quá trình CI/CD chạy. Nó sẽ tự động đăng nhập, build image và đẩy (push) lên Docker Hub của bạn.
* Khi deploy trên VPS, vì file `docker-compose.yml` của bạn đã sửa thành `image: kaitobui/finance_forecaster:latest`, bạn chỉ cần gõ lệnh sau để cập nhật ứng dụng:
```bash
docker-compose pull
docker-compose up -d

```
