# 01_cover

Trong bài báo cáo này, em trình bày SmartNoteCloud như một hệ thống học tập triển khai trên cloud, không chỉ là một ứng dụng web đơn lẻ. Điểm quan trọng là hệ thống đã có domain công khai, chạy qua HTTPS, đóng gói bằng Docker và dùng database thật. Từ đó, bài sẽ phân tích cách dự án thể hiện ba mô hình dịch vụ cloud: IaaS, PaaS và SaaS.

# 02_problem_motivation

Vấn đề xuất phát từ nhu cầu học tập: người dùng có ghi chú, nhưng cần một công cụ giúp biến ghi chú thành tài liệu ôn tập có cấu trúc hơn. Đồng thời, với môn Cloud, nhóm cần một ví dụ có thể chứng minh bằng deployment thật. Vì vậy SmartNoteCloud được chọn làm case study: vừa có sản phẩm, vừa có hạ tầng, vừa có dữ liệu để quan sát.

# 03_product_overview

SmartNoteCloud hay MindDeckNote Lite gồm bốn nhóm chức năng chính. Người dùng đăng nhập, tạo workspace và ghi chú; sau đó backend có thể gọi AI để tóm tắt hoặc sinh flashcard. Các flashcard này được lưu lại để người dùng ôn tập. Nhìn từ góc cloud, đây là một ứng dụng nhiều tầng: frontend, backend, database và dịch vụ AI bên ngoài.

# 04_feature_workflow

Luồng sử dụng chính bắt đầu từ việc người học tạo note. Nội dung note đi qua backend, backend xử lý hoặc gửi sang AI API, sau đó tạo ra summary hoặc flashcard. Khi người dùng ôn tập, kết quả review tiếp tục được lưu vào database. Quy trình này cho thấy cloud không chỉ là nơi host website, mà còn là nơi điều phối dữ liệu và dịch vụ.

# 05_architecture_overview

Kiến trúc tổng quan gồm browser ở phía người dùng, Nginx làm gateway, React phục vụ giao diện, FastAPI xử lý nghiệp vụ và PostgreSQL lưu dữ liệu. Bên ngoài hệ thống còn có Mimo AI API, được gọi qua HTTPS. Điểm cần nhấn mạnh là toàn bộ stack ứng dụng chạy trong Docker trên EC2, còn database không mở trực tiếp ra Internet.

# 06_request_flow

Ở cấp request, cùng một domain nhưng có hai nhánh xử lý. Nếu người dùng truy cập giao diện, Nginx trả về React static build. Nếu request đi vào đường dẫn API, Nginx chuyển tiếp sang FastAPI backend. Backend kiểm tra JWT, đọc ghi PostgreSQL và khi cần thì gọi AI API. Cách tách route này giúp kiến trúc rõ ràng và dễ mở rộng.

# 07_aws_deployment_flow

Quy trình triển khai bắt đầu từ DNS trỏ domain pkiresearch.id.vn về public IP của EC2. Trên EC2, Security Group chỉ mở các cổng cần thiết, sau đó Nginx nhận request và chuyển tiếp vào các container. Chứng chỉ HTTPS được cấp bằng Let's Encrypt Certbot. Kết quả là website có thể truy cập công khai qua HTTPS và health check backend trả về trạng thái ok.

# 08_containerization_design

Docker Compose giúp tách từng thành phần thành container riêng. Nginx là cổng public duy nhất, frontend và backend nằm trong network nội bộ, còn PostgreSQL chạy trong container database có volume để giữ dữ liệu. Cách đóng gói này giúp triển khai nhất quán hơn giữa máy local và EC2, đồng thời giảm lỗi do khác môi trường.

# 09_iaas_ec2

Phần IaaS thể hiện rõ nhất ở EC2. AWS cung cấp máy ảo, public IP, network và Security Group, nhưng nhóm vẫn phải tự quản hệ điều hành, Docker, Nginx, SSL, log và backup. Vì vậy EC2 cho quyền kiểm soát cao, nhưng trách nhiệm vận hành cũng cao. Đây là ví dụ điển hình của Infrastructure as a Service.

# 10_paas_comparison

Nếu chuyển sang PaaS, một phần trách nhiệm vận hành sẽ được nền tảng đảm nhiệm. Ví dụ App Runner hoặc Elastic Beanstalk có thể hỗ trợ runtime, health check, scaling và deployment flow tốt hơn. Trong dự án hiện tại, nhóm đang dùng IaaS là chính; PaaS được đưa vào để so sánh và chỉ ra hướng giảm tải vận hành trong tương lai.

# 11_saas_api

Phần SaaS nằm ở dịch vụ AI bên ngoài. Thay vì tự triển khai model, GPU và inference server, backend gọi Mimo AI API qua HTTPS bằng API key. Hệ thống chỉ cần chuẩn hóa prompt, gửi request và lưu kết quả. Đây là cách dùng Software as a Service: tận dụng năng lực đã được nhà cung cấp vận hành sẵn.

# 12_cloud_model_mapping

Slide này tổng hợp ba mô hình cloud trong cùng một hệ thống. EC2 là IaaS vì cung cấp hạ tầng máy chủ. PaaS là hướng nâng cấp có thể dùng để giảm công việc vận hành. SaaS là dịch vụ AI API được tích hợp vào tính năng sản phẩm. Như vậy, một dự án thực tế có thể không chỉ thuộc một mô hình duy nhất, mà kết hợp nhiều tầng khác nhau.

# 13_database_data_flow

Database lưu các thực thể học tập như users, workspaces, pages, blocks, decks, cards và card reviews. Các bảng này cho thấy hệ thống đã có dữ liệu thật chứ không chỉ là giao diện demo. Về bảo mật, PostgreSQL không public ra ngoài; khi cần xem bằng DBeaver, ta đi qua SSH tunnel vào EC2. Cách này phù hợp hơn so với mở thẳng cổng 5432 ra Internet.

# 14_security_operations

Khi chạy cloud, các điểm bảo mật tối thiểu gồm kiểm soát cổng bằng Security Group, dùng HTTPS cho domain, giữ secret trong biến môi trường và theo dõi container bằng docker ps, logs hoặc health endpoint. Với môi trường production, cần nâng cấp thêm bằng giới hạn SSH theo IP, Secrets Manager, backup tự động, monitoring và rate limit ở gateway.

# 15_results_future_work

Kết quả cuối cùng là SmartNoteCloud đã có domain HTTPS, stack Docker chạy ổn định, database có dữ liệu và backend tích hợp AI API. Dự án chứng minh được IaaS qua EC2, SaaS qua AI API và chỉ ra hướng PaaS để tối ưu vận hành. Nếu phát triển tiếp, nên tách database sang RDS, đưa secret vào Secrets Manager, bổ sung CI/CD, monitoring và cơ chế backup rõ ràng.
