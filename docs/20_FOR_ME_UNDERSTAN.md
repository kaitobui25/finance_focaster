# 📖 SỔ TAY Q&A: GIẢI MÃ SIÊU CÒ HIỂU BIẾT "FINANCE FORECASTER"
*(Phiên bản tóm tắt siêu tốc, súc tích và chống buồn ngủ)*

## 1. 🏗️ Chuyện xây nhà (Kiến trúc & Tổng quan)
* **Q: Repo này nhìn chung thế nào?**
  * **A:** Xịn xò, chuẩn kỹ sư! Code chia 4 lớp Clean Architecture rành mạch. Có hẳn "kịch bản" điều đào cho AI. Điểm trừ duy nhất là nhà xây to nhưng... mới dọn vào ở tầng trệt (Phase 1).

## 2. 🗄️ Chuyện cái Kho (Database)
* **Q: Có 10 bảng Database mà sao không có dây nhợ (Foreign Keys) link với nhau vậy? Ngộ ha?**
  * **A:** Ngộ nhưng hợp lý! Đây là hệ thống kho dữ liệu (Data Warehouse). Các dữ liệu không dính nhau bằng khóa ngoại mà hẹn hò nhau qua mốc **Thời gian**. AI sẽ làm "bộ não" tự chắp vá chúng lại.
* **Q: 10 bảng đó dùng làm gì?**
  * **A:** Tưởng tượng đây là 10 phòng ban của tập đoàn:
    * `instruments`: Danh bạ VIP (KOLs cần soi).
    * `articles`: Sạp báo lề đường (cào từ RSS).
    * `reports`: Nhật ký báo cáo Sếp.
    * `market_snapshots`, `sector_performance`, `economic_indicators`: Hồ sơ bệnh án, Bảng xếp hạng idol ngành, và Nhiệt kế đo lường các "Bác" lãnh đạo.
    * `market_calendar`: Lịch hóng biến.
    * `recommendations`, `risk_alerts`, `analysis_snapshots`: Sổ phím hàng, Chuông báo cháy, và Góc tâm linh chém gió của AI.
* **Q: Thế sao tui cào 200 bài báo rồi mà 8/10 bảng vẫn trống không?**
  * **A:** Tại Sếp mới tuyển được mỗi anh văn thư cắt dán báo (`articles`), còn các phòng "Hút data giá cổ phiếu" (Phase 2) vẫn đang tắt điện khóa cửa chờ Sếp code tiếp!

## 3. 🕷️ Chuyện đi cào (Crawler)
* **Q: Bao lâu nó cào một lần? Lấy bao nhiêu bài?**
  * **A:** Mặc định 2 tiếng cào 1 lần. Châm ngôn cào là "Có bao nhiêu vét bấy nhiêu", nhưng hệ thống rất khôn: nó soi trùng lặp và chỉ đem về những bài báo "mới xuất xưởng" chưa có trong kho.
* **Q: Cấu hình 2 tiếng/lần sao phải ghi ở 2 nơi (`.env` và `config.py`) cho cực?**
  * **A:** Lấy le chuẩn 12-Factor App đấy! `.env` là Tờ order cho Sếp điền (không cần biết code). Còn `config.py` là anh bồi bàn dịch cái order đó sang ngôn ngữ máy tính và tự động bù vào nếu Sếp lỡ quên ghi.

## 4. 🧠 Chuyện con AI (Google Gemini)
* **Q: Đang thuê "Chuyên gia" nào phân tích đấy? Giọng điệu lo đời ở đâu ra?**
  * **A:** Đang xài `gemini-2.5-flash`. Việc AI tự xưng là KAI-FINA, phím hàng sành sỏi là do bị Sếp "tẩy não" qua 3 luồng Prompt (`SUMMARIZE_PROMPT`, `KEYWORDS_PROMPT`, `DIGEST_PROMPT`) ghim cứng trong code.
* **Q: Cào một đống 30.000 chữ nhét cho AI đọc thì có "cháy túi" tiền API không?**
  * **A:** Rẻ như cho, thậm chí miễn phí! Code đã được "gọt" sẵn: bài báo dài mấy thì cũng chỉ cắt đúng 3.000 ký tự đầu (`text[:3000]`) đưa cho AI. Kết hợp với gói Free Tier hào phóng của Flash, Sếp cứ cắm máy 24/7 khỏi lo hóa đơn.

## 5. 🔭 Chuyện tương lai (Next Steps)
* **Q: Tui muốn làm sếp lớn (Kiến trúc sư trưởng) thì phải hỏi gì tiếp?**
  * **A:** Cần trăn trở 5 câu sau:
    1. Làm sao code gọi API giá chứng khoán để lấp đầy 8 bảng DB đang ế?
    2. Đổi "khẩu vị" AI sang đánh Crypto hay VNI thì sửa Prompt thế nào?
    3. Hết thích RSS, đổi sang cào tin Twitter/Youtube thì gắn Adapter mới vào đâu?
    4. Xây Web Dashboard (Phase 4) thì có phải đập đi làm lại không?
    5. Lúc AI "ngáo" hoặc Google sập mạng thì làm sao gắn loa báo động (Alert) qua Telegram?