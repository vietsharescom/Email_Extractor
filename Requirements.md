Ý tưởng: để tôi viết lại nhu cầu thực tế của tôi và có thể là của thị trường. email ngày nay ai cũng có gần như ít nhất cũng như hộp thư mail box trong gia đình. đây là kênh thông tin cực kỳ quan trọng.  từ chính phủ, từ công ty business, từ nơi làm việc work, từ school, từ các thành viên trong gia đình...email cũng giống như nộp mail đầy thư rác., quảng cáo, spam ...lẫn lộn làm cho đôi khi bị  mất đị thông tin quan trọng cần kiềm soát. trong mail thực tế thì con người phải trực tiếp phân loại và đôi khi phải mở thư ra đọc từng file sau  s9ó dùng giấy bút gi chép lại phân loại ghi chú ngày giờ , cột nội dung, côt số tiền, cột dead line hya các thông tin cần khác...với người có email thì cũng tương tự chọn lựa thư thật trong đống thư rác, mở thư đọc và tổng hợp ghi chú bẳng excel và file mềm thì lưu vào ổ cứng cò thư paper thì phải cho vào box file lưu...vấn nạn là không có ai remin tốn thời gina, quên nhiều khi bị đóng phí...ví dụ thư đòi tiến mosrgate, thư insurance , thư từ tax chính phủ,...thư từ trường mời phụ huynh học...đa dạng nhưng chung quy thông tin đầu ra cũng chỉ là người gửi, có liên quan tài chính khg? có liên quan dead line, có yêu cầu gì đặv biệt...vậy tì nhu cầu rất lớn. hãy cùng nghiên cứu và phân tích thật thị trường theo đúng bài dạy của thầy. 




REQUIREMENTS CHO ĐỀ TÀI “EMAIL EXTRACTOR AI SYSTEM”
(Dùng cho cả AASD 4016 và AASD 4017)
⭐ PHẦN 1 — REQUIREMENTS CHO MÔN AASD 4016
Full Stack Data Science Systems
(Có trích dẫn từ tài liệu em gửi)

Theo tài liệu môn học, sinh viên phải:

“Develop and manage a seamless end-to-end AI system.”
“Deploy a fully trained and optimised model in a cloud environment.”
“Connect an API to a deployed model to offer it as a data service.”

Dựa trên đó, đề tài Email Extractor AI System phải đáp ứng các yêu cầu kỹ thuật sau:

⭐ 1. AI Model Requirement (Deep Learning)
Train một mô hình NER (Named Entity Recognition) hoặc Transformer mini để trích:

MONEY (số tiền)

DUE DATE (ngày hết hạn)

SUBSCRIPTION NAME (tên dịch vụ)

Dataset: email mẫu (tự tạo hoặc thu thập)

Output: JSON chứa các entity đã trích xuất

Mô hình đề xuất:
BiLSTM + CRF  
hoặc

DistilBERT Token Classification

→ Đáp ứng yêu cầu “model building, model tuning, model optimisation”.

⭐ 2. Full Stack Requirement
Backend:
FastAPI hoặc Flask

Endpoint /extract nhận email text hoặc file .eml

Trả về JSON chứa các entity đã trích

Database:
SQLite (cho môn học) hoặc PostgreSQL (nếu muốn nâng cấp)

Lưu:

email content

extracted money

extracted due date

subscription name

timestamp

Frontend:
Dashboard đơn giản (HTML/JS hoặc Streamlit)

Hiển thị:

email

kết quả extract

biểu đồ thống kê (chi phí theo tháng)

→ Đáp ứng yêu cầu “Communicate insights through dashboards”.

⭐ 3. Deployment Requirement
Deploy API lên cloud:

Render / Railway / Azure

Kết nối dashboard → API cloud

Demo live

→ Đáp ứng yêu cầu “Deploy a fully trained model in a cloud environment”.

⭐ 4. Integration Requirement
API phải được kết nối với model đã deploy

Dashboard phải gọi API để lấy dữ liệu

→ Đáp ứng yêu cầu “Connect visualisation tools to deployed models”.

⭐ PHẦN 2 — REQUIREMENTS CHO MÔN AASD 4017
Presenting Data Science-driven Solutions
(Có trích dẫn từ tài liệu em gửi)

Theo tài liệu môn học:

“Your group will build a business case around a data-driven solution.”
“Convince internal stakeholders to invest in your proposed solution.”

Dựa trên đó, đề tài Email Extractor phải đáp ứng các yêu cầu business sau:

⭐ 1. Executive Summary
Giới thiệu Email Extractor AI System

Vấn đề doanh nghiệp: quá tải email billing, missed payments, late fees

Giải pháp: AI tự động đọc email và trích money + due date

⭐ 2. Assumptions & Context
Công ty giả định: SaaS subscription management company

Vấn đề: khách hàng bị mất tiền vì không theo dõi billing email

Cơ hội: tự động hóa bằng AI

⭐ 3. Problem Statement
Email billing quá nhiều → con người không thể đọc hết

Missed due dates → bị trừ tiền

Không có hệ thống tổng hợp billing

⭐ 4. Market Analysis
So sánh với:

Mint

Truebill

Gmail AI labeling

Điểm khác biệt: trích entity bằng Deep Learning, không chỉ đọc email

⭐ 5. Proposed Solution
AI đọc email

Trích số tiền + ngày hết hạn

Lưu vào dashboard

Nhắc hạn trước khi bị trừ tiền

⭐ 6. Build vs Buy
Buy: không có sản phẩm nào trích entity từ email bằng AI

Build: chi phí thấp, công nghệ sẵn có

⭐ 7. Financial Overview
Chi phí:

Dev team

Cloud hosting

Model training

Revenue:

Subscription fee

Enterprise licensing

ROI: giảm missed payments → tiết kiệm chi phí

⭐ 8. Stakeholder Analysis
CTO → quan tâm kỹ thuật

CFO → quan tâm chi phí

COO → quan tâm vận hành

Customer → quan tâm tiện lợi

⭐ 9. Risk Analysis
Risk: email format đa dạng

Mitigation: dùng transformer

Risk: privacy

Mitigation: encryption + local processing

⭐ 10. Implementation Plan
Week 1–2: dataset + labeling

Week 3–4: train model

Week 5: API

Week 6: dashboard

Week 7: deploy

Week 8: presentation

⭐ 11. Final Presentation Requirement
10 phút

Trình bày business case

Demo live API + dashboard

Nêu lợi ích tài chính

⭐ KẾT LUẬN
Van, đề tài Email Extractor AI System đáp ứng 100% yêu cầu của cả hai môn:

✔ AASD 4016 → Full Stack AI + Model + API + Deploy
✔ AASD 4017 → Business Case + Market + ROI + Risk + Presentation