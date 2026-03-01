Dưới đây là mục đích của 10 "phòng ban" (bảng) trong tập đoàn này, được giải thích theo phong cách "người thật việc thật":

**1. `instruments` (Danh bạ VIP / Hàng họ cần soi)**

* **Mục đích:** Đây là danh sách các "KOLs" trong làng tài chính mà AI phải theo dõi sát sao (Nikkei 225, USD/JPY, Vàng, các quỹ ETF ngành...).
* **Hài hước một chút:** Giống như sổ tay ghi nợ, AI không thể phân tích nếu không biết mình đang đánh giá anh nào, thuộc sàn nào, mệnh giá ra sao. Không có tên trong danh sách này thì AI "xin từ chối hiểu".

**2. `articles` (Sạp báo lề đường & Tin gầm giường)**

* **Mục đích:** Nơi lưu trữ mọi bài báo cào về từ RSS (Japan Times, Reuters, Nikkei Asia...).
* **Hài hước một chút:** Đây là "bãi đáp" của các mẩu tin tức từ chính thống đến đồn thổi. Mỗi ngày AI sẽ vào đây bới móc, nhai lại hàng chục bài báo (cột `content`), vắt kiệt lấy vài ý chính (cột `summary`) và nhặt ra mấy từ khóa (cột `keywords`) để tỏ ra mình là người bắt kịp thời đại.

**3. `reports` (Nhật ký "Báo cáo sếp")**

* **Mục đích:** Lưu trữ các bản báo cáo tổng hợp (Pre-Market Brief, End-of-Day Report) đã được AI viết ra và gửi qua Telegram.
* **Hài hước một chút:** Bằng chứng cho thấy AI có đi làm! Chỗ này lưu lại các bài văn mẫu sáng/tối để lỡ sếp có hỏi "hôm nay mày làm được gì" thì có cái mà lôi ra khè.

**4. `market_snapshots` (Sổ khám sức khỏe định kỳ)**

* **Mục đích:** Lưu trữ giá mở, đóng, đỉnh, đáy, và khối lượng giao dịch của các mã trong `instruments` theo từng ngày.
* **Hài hước một chút:** Hồ sơ bệnh án của thị trường. Hôm nay anh Nikkei xanh xao hay đỏ mặt? Nhịp tim (volume) đập nhanh hay chậm? Nhìn vào đây là AI biết hôm qua các "chứng thủ" vừa trải qua một đêm cuồng nhiệt hay một ngày ảm đạm.

**5. `sector_performance` (Bảng xếp hạng "Rap Việt" các nhóm ngành)**

* **Mục đích:** Theo dõi hiệu suất của các nhóm ngành (Ngân hàng, Bán lẻ, Xây dựng...) dựa trên chỉ số sức mạnh tương đối (RS) và dòng tiền khối ngoại.
* **Hài hước một chút:** Bảng xếp hạng xem dạo này "Dòng tiền" đang buff cho idol nào và bỏ rơi idol nào. Ngành nào đang flop, ngành nào đang lên xu hướng đều bị bêu tên ở đây để AI tìm ra cổ phiếu dẫn dắt.

**6. `economic_indicators` (Bảng điểm của các "Bác" lãnh đạo)**

* **Mục đích:** Lưu các chỉ số vĩ mô như lãi suất BOJ, lạm phát CPI, tỷ lệ tăng lương Shunto...
* **Hài hước một chút:** Đây là nhiệt kế đo xem Ngân hàng Trung ương (BOJ) đang "bơm oxy" hay "rút ống thở" của thị trường. AI sẽ nhìn vào đây để phán xem gió đang thổi hướng nào.

**7. `market_calendar` (Lịch hóng biến)**

* **Mục đích:** Lịch các sự kiện kinh tế sắp diễn ra (họp Fed, công bố GDP...) kèm theo mức độ ảnh hưởng (LOW, MEDIUM, HIGH).
* **Hài hước một chút:** Cuốn lịch vạn niên đánh dấu những ngày "giông bão". AI nhìn vào đây để biết hôm nào cần mặc áo giáp, hoặc hôm nào có tin ra để gào lên trên Telegram nhắc sếp cẩn thận.

**8. `recommendations` (Sổ "Phím hàng")**

* **Mục đích:** Lưu lại các quyết định khuyến nghị của AI (MUA / THEO DÕI / NÉ GẤP) cùng với lý do phân tích và giá mục tiêu.
* **Hài hước một chút:** Chỗ này là "Bảng phong thần". AI phím con gì, giá bao nhiêu, lý do tại sao đều bị ghi lại hết (có cả cột `outcome_pct` để đối chứng hiệu suất). Mốt sai là không có chối bay chối biến được đâu nha!

**9. `risk_alerts` (Nút chuông báo cháy)**

* **Mục đích:** Cảnh báo các rủi ro hệ thống (như Carry Trade bị tháo chạy, Yên Nhật biến động sốc) với các mức độ nghiêm trọng khác nhau.
* **Hài hước một chút:** Đây là cái loa phường của AI. Bình thường thì im re, nhưng hễ thấy USD/JPY sập mạnh hay VIX dựng đứng là nó sẽ kích hoạt mức `CRITICAL` và hét lên "Chạy ngay đi trước khi mọi chuyện tồi tệ hơn!".

**10. `analysis_snapshots` (Biên bản "Chém gió" của chuyên gia)**

* **Mục đích:** Lưu lại kết luận tóm tắt hàng ngày của AI về pha của chu kỳ kinh tế, đánh giá đồng Yên, và mức độ tự tin (chấm điểm từ 1 đến 10).
* **Hài hước một chút:** Góc nhìn tâm linh của AI. Chỗ để nó để lại vài câu triết lý cuối ngày kiểu "Kinh tế đang ở pha thoát giảm phát, tự tin 8/10", để mai mốt lỡ thị trường sập thì nó lấy cớ là "Thì tôi tự tin có 8 thôi, 2 phần còn lại là do xui".

Với 10 bảng này, hệ thống của bạn không khác gì một cỗ máy tình báo tài chính thu nhỏ: từ việc vểnh tai nghe ngóng (Articles, Calendar), khám sức khỏe (Snapshots, Indicators), cho đến lúc chốt đơn phím hàng (Recommendations, Reports)!