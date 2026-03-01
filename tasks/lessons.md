# Lessons Learned

## 2026-03-01: Không ghi đè file tài liệu của user
- **Sai lầm:** Ghi đè toàn bộ nội dung `01_Workflow_Orchestration.md` bằng nội dung tự viết, mất hết workflow rules gốc của user.
- **Nguyên nhân:** Không kiểm tra kỹ file đang trống hay user đang chuẩn bị paste nội dung vào.
- **Quy tắc:** Khi file của user đã có nội dung hoặc user đề cập có nội dung riêng → **KHÔNG BAO GIỜ** ghi đè. Phải hỏi trước hoặc chỉ append/bổ sung.
