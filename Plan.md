# KẾ HOẠCH NGHIÊN CỨU & LỘ TRÌNH PHÁT TRIỂN (RESEARCH & IMPLEMENTATION PLAN)

> **Đề tài:** Machine Learning trong Phát Hiện URL Phishing  
> **Tài liệu tham chiếu:** [`Document/NCKH.md`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Document/NCKH.md), [`Architecture.md`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Architecture.md)  
> **Cập nhật lần cuối:** 2026-11-22  

---

## 1. Bản Chất Quy Trình Dữ Liệu & Bài Toán Machine Learning

1. **Bảo toàn Nhãn gốc ($y$ - Ground Truth):**
   * Nhãn phân loại (`label`: 0 - Lành tính, 1 - Phishing) được **bảo toàn nguyên vẹn 100% từ tập dữ liệu thô (Raw Dataset)** như PhiUSIIL hoặc Kaggle.
   * Tuyệt đối không sử dụng bất kỳ luật cứng (heuristic rule/port check) nào để tự ý thay đổi hoặc gán lại nhãn dữ liệu.
2. **Bản chất của Trích xuất Đặc trưng ($X$):**
   * Các thuật toán Machine Learning dạng bảng (Random Forest, XGBoost, LightGBM) chỉ làm việc trên ma trận số học.
   * Khâu trích xuất đặc trưng có nhiệm vụ đo đạc các thuộc tính toán học, cấu trúc và ngữ nghĩa trên chuỗi văn bản `url` thô để sinh ra vector số học $X$.
   * Ma trận đầu ra tại `Data/Processed/` sẽ ghép nối các cột đặc trưng $X$ với cột `label` gốc làm cơ sở huấn luyện.
3. **Vai trò của `Src/Core/constants.py`:**
   * Là điểm lưu trữ tập trung các tập hợp hằng số đối chiếu toán học được định nghĩa trong `NCKH.md`:
     * $\mathcal{D}_{\text{ports}} = \{80, 443\}$: Nhận diện cổng dịch vụ chuẩn.
     * $\mathcal{D}_{\text{risky}}$: Danh sách ~105 Top-Level Domains (TLDs) có nguy cơ cao dựa trên thống kê chính thức từ **The Spamhaus Project** ([`https://www.spamhaus.org/statistics/tlds/`](https://www.spamhaus.org/statistics/tlds/)):
       * *Cơ sở lựa chọn:* Chọn lọc các TLDs có chỉ số lạm dụng (**Badness Index > 0**) và tỷ lệ tên miền độc hại cao (như `.top`, `.cfd`, `.sbs`, `.icu`, `.bond`, `.cam`, `.buzz`, `.rest`, `.lat`, `.fit`, `.skin`, ...).
       * *Quy tắc loại trừ:* Không đưa các TLD phổ thông khổng lồ (`.com`, `.net`, `.org`) vào tập rủi ro dù có số lượng vi phạm tuyệt đối cao, nhằm tránh gây báo động nhầm (False Positive) cho các URL lành tính.
       * *Tính học thuật & pháp lý:* Có trích dẫn nguồn uy tín toàn cầu, đảm bảo độ tin cậy tuyệt đối khi báo cáo đề tài NCKH.
     * $\mathcal{D}_{\text{shortener}}$: Danh sách các tên miền dịch vụ rút gọn link (`bit.ly`, `tinyurl.com`, `t.co`, `cutt.ly`, ...):
       * *Nguồn tham chiếu chuẩn:* Dự án mã nguồn mở bảo mật uy tín [**PeterDaveHello/url-shorteners**](https://github.com/PeterDaveHello/url-shorteners) (được tin dùng bởi NextDNS, AdGuard, ControlD) kết hợp với danh mục `Shortining_Service` chuẩn từ nghiên cứu của APWG và UCI Machine Learning Repository.
       * *Mục đích học máy:* Đánh dấu cờ nhị phân `is_shortened = 1` để mô hình nhận diện hành vi ngụy trang / giấu tên miền đích (theo kỹ thuật T1027 của MITRE ATT&CK).
     * $\mathcal{D}_{\text{brand}}$: Danh sách các thương hiệu có nguy cơ cao bị mạo danh:
       * *Nguồn tham chiếu học thuật & thực nghiệm:* Bộ dữ liệu chuẩn mở gồm **181 Target Brands** từ công trình nghiên cứu hệ thống Phishpedia công bố tại hội thảo bảo mật top-1 thế giới [**USENIX Security 2021**](https://www.usenix.org/conference/usenixsecurity21) ([`lindsey98/Phishpedia`](https://github.com/lindsey98/Phishpedia)), kết hợp báo cáo định lượng *Brand Phishing Report* hàng quý của **Check Point Research (CPR)**. Bổ sung các thương hiệu ngân hàng & ví điện tử phổ biến tại Việt Nam (Local context: `vietcombank`, `techcombank`, `momo`, `zalo`, ...).
       * *Mục đích học máy & Cơ chế Combosquatting:* So khớp sự xuất hiện của chuỗi thương hiệu với `registered_domain` (eTLD+1). Nếu thương hiệu xuất hiện ở Subdomain hoặc Path nhưng `registered_domain` không phải là tên miền chính thống $\rightarrow$ kích hoạt cờ mạo danh thương hiệu `is_brand_spoofed = 1` (loại bỏ hoàn toàn nguy cơ phạt nhầm website chính chủ).
     * $\mathcal{D}_{\text{sensitive}}$: Danh sách các từ khóa tâm lý lừa đảo (Social Engineering Keywords):
       * *Nguồn tham chiếu & Phương pháp luận toán học:* Được trích xuất hoàn toàn khách quan bằng các thuật toán Lý thuyết Thông tin: **Information Gain (IG - Độ thu nhận thông tin qua Entropy)** và kiểm định **Chi-Square ($\chi^2$)** với mức ý nghĩa thống kê $p$-value $< 0.001$ trên các tập dữ liệu lớn từ PhishTank và tập dữ liệu chuẩn **PhiUSIIL (UCI 2024)**.
       * *Phân loại theo hành vi thao túng tâm lý (ENISA & CISA):* Chia thành 4 nhóm kích hoạt hành vi: Xác thực (`login`, `signin`, `auth`), Bảo mật tài khoản (`verify`, `security`, `restore`), Đe dọa khẩn cấp (`suspended`, `locked`, `alert`), và Tài chính/Quà tặng (`banking`, `payment`, `bonus`, `gift`).
       * *Mục đích học máy:* Sinh ra 2 đặc trưng số học: `sensitive_keyword_count` (tổng số lượng từ khóa xuất hiện) và `has_sensitive_keyword` (cờ nhị phân 0/1).
   * **Nguyên lý Tách biệt Mã nguồn & Dữ liệu (Separation of Code & Data):**
     * Để tránh làm file Python bị dài dòng (hàng trăm dòng chuỗi tĩnh), toàn bộ 4 danh mục đối chiếu được lưu thành các file văn bản sạch tại thư mục `Data/External/`:
       * `Data/External/risky_tlds.txt`: 105 TLDs lạm dụng từ Spamhaus.
       * `Data/External/shorteners.txt`: Danh sách tên miền rút gọn từ PeterDaveHello/url-shorteners.
       * `Data/External/target_brands.txt`: Danh sách 181+ thương hiệu từ USENIX Security 2021 Phishpedia + Ngân hàng VN.
       * `Data/External/sensitive_keywords.txt`: Danh sách từ khóa nhạy cảm lọc từ Information Gain / Chi-Square.
     * `Src/Core/helpers.py`: Cung cấp hàm tiện ích `load_set_from_file()` đọc các tệp text từ `Data/External/` và tự động làm sạch (loại bỏ comment `#`, chuẩn hóa chữ thường).
     * `Src/Core/constants.py`: Nạp dữ liệu một lần duy nhất lúc khởi động hệ thống vào bộ nhớ dưới dạng `frozenset` với tốc độ tìm kiếm tức thì $O(1)$ (~50-80 nanoseconds), đảm bảo code siêu tinh gọn và dễ dàng bảo trì, cập nhật.
     * *Cơ chế nhận diện Cloud Free Hosting:* Không cần hardcode danh sách thủ công mà được nhận diện tự động và khách quan 100% thông qua cơ chế phân tách Private Suffix của **Mozilla Public Suffix List** bằng thư viện `tldextract` trong `Src/Core/url_parser.py`.

---

## 2. Phân Tích So Sánh Các Hướng Tiếp Cận Trích Xuất Đặc Trưng

| Hướng tiếp cận | Cơ chế hoạt động | Ưu điểm cốt lõi | Nhược điểm & Hạn chế | Khả thi tài nguyên (Hardware) |
| :--- | :--- | :--- | :--- | :--- |
| **Hướng 1: Đặc trưng Toán học & Cấu trúc (Handcrafted Lexical & Structural)** | Đo độ dài, đếm tần suất ký tự, tính Shannon Entropy, phân tích RFC 3986 + PSL (40+ đặc trưng trong `NCKH.md`). | • Tốc độ siêu nhanh ($< 0.1$ ms / URL).<br>• Rất nhạy với dị thường cấu trúc: IP thô, cổng lạ, Punycode `xn--`, chuỗi DGA ngẫu nhiên. | • **Mù ngữ nghĩa (Semantic Blindness):** Dễ bị qua mặt bởi URL có cấu trúc đẹp nhưng ghép từ mạo danh tinh vi (`secure-login-vietcombank-verify.com`). | Rất nhẹ, chạy hoàn toàn trên CPU thông thường. |
| **Hướng 2: Character N-grams kết hợp TF-IDF** | Băm nhỏ URL thành các cụm $N$ ký tự liên tiếp ($N \in [3, 5]$). Tính trọng số TF-IDF cho từng n-gram. | • **Bắt cực chuẩn Typosquatting:** Dù đổi `paypal` thành `paypa1`, các n-gram con (`pay`, `ayp`, `ypa`) vẫn khớp.<br>• Kháng lỗi từ ngoài từ điển (OOV). | • Tạo ma trận số chiều lớn (cần kiểm soát bằng `max_features = 300 - 500`).<br>• Chưa hiểu sâu ngữ cảnh thứ tự xa. | Nhẹ, xử lý nhanh trên CPU bằng `scikit-learn`. |
| **Hướng 3: Mô hình Ngôn ngữ & Transformer (NLP / Embeddings)** | Xem URL như câu văn, dùng FastText hoặc Transformer (DistilBERT, MiniLM / URLBERT) với cơ chế Self-Attention. | • **Hiểu sâu ngữ cảnh và ý định:** Nhận diện mối liên kết giữa Brand + Action Keyword (`bank` + `verify`).<br>• Không cần kỹ nghệ đặc trưng thủ công. | • Độ trễ suy luận cao ($10 - 50$ ms / URL).<br>• Đòi hỏi GPU để huấn luyện.<br>• Dễ bị rối trước các mã hóa cấu trúc mạng (IP số nguyên, Hex). | Nặng, bắt buộc cần GPU (Google Colab / Dedicated GPU). |

---

## 3. Chiến Lược Thực Nghiệm Đề Tài NCKH (Ablation Study)

Để bài nghiên cứu đạt giá trị khoa học cao và thuyết phục tuyệt đối trước hội đồng thẩm định, dự án sẽ triển khai kịch bản thực nghiệm đối chứng theo 3 cấu hình:

```mermaid
flowchart TD
    classDef baseStyle fill:#1e293b,stroke:#0284c7,stroke-width:1.5px,color:#f8fafc;
    classDef hybridStyle fill:#14342b,stroke:#059669,stroke-width:1.5px,color:#f8fafc;
    classDef nlpStyle fill:#2e1065,stroke:#9333ea,stroke-width:1.5px,color:#f8fafc;

    URL["Tập URL Thô (Raw Dataset)"]

    M1["Cấu hình 1: Baseline<br>40+ Đặc trưng Toán học & Cấu trúc"]:::baseStyle
    M2["Cấu hình 2: Đề xuất Chính (Hybrid)<br>[40+ Toán học] ⊕ [300 TF-IDF N-grams]"]:::hybridStyle
    M3["Cấu hình 3: Mở rộng Đối chứng<br>Deep Transformer Embeddings (DistilBERT/MiniLM)"]:::nlpStyle

    URL --> M1
    URL --> M2
    URL --> M3

    Eval1["Đánh giá: F1-Score, Accuracy, Độ trễ (ms)"]
    Eval2["Đánh giá: F1-Score, Accuracy, Độ trễ (ms)"]
    Eval3["Đánh giá: F1-Score, Accuracy, Độ trễ (ms)"]

    M1 --> Eval1
    M2 --> Eval2
    M3 --> Eval3
```

1. **Mô hình 1 (Baseline - Nền tảng):**
   * Chỉ sử dụng 40+ đặc trưng toán học và cấu trúc theo `NCKH.md`.
   * Mục tiêu: Đạt baseline tốc độ cao, tái lập các kết quả benchmark truyền thống.
2. **Mô hình 2 (Đề xuất chính - Kiến trúc Lai Hybrid):**
   * Kết hợp: **[40+ Đặc trưng Toán học]** $\oplus$ **[300 Đặc trưng TF-IDF Character N-grams]** $= \mathbf{340\text{ chiều số}}$.
   * Thuật toán phân loại: **XGBoost / LightGBM**.
   * Mục tiêu: Bù đắp hoàn hảo điểm mù ngữ nghĩa của Mô hình 1, bắt triệt để lỗi chính tả typosquatting trong khi vẫn giữ tốc độ xử lý nhanh ($< 0.5$ ms) trên CPU.
3. **Mô hình 3 (Mở rộng đối chứng - Deep Learning / Transformer):**
   * Trích xuất vector đặc trưng bằng Transformer rút gọn (DistilBERT / MiniLM) trên môi trường Google Colab GPU.
   * Mục tiêu: Cung cấp số liệu so sánh toàn diện trong bài báo khoa học: chứng minh mô hình Hybrid (Mô hình 2) đạt sự cân bằng tối ưu nhất giữa độ chính xác và chi phí tài nguyên tính toán thực tế.

---

## 4. Lộ Trình Triển Khai Kỹ Thuật (Implementation Roadmap)

### Giai đoạn 1: Chuẩn hóa Nền tảng & Tiền Xử Lý Dữ Liệu
- [x] Thiết lập tệp [requirements.txt](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/requirements.txt) (`pandas`, `numpy`, `tldextract`, `scikit-learn`, `joblib`, `matplotlib`, `seaborn`).
- [x] Làm sạch dữ liệu thô tại [`Notebooks/CleanRawData.ipynb`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Notebooks/CleanRawData.ipynb), xuất 235.370 URL sạch sang [`Data/Interim/urls_cleaned.csv`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Data/Interim/urls_cleaned.csv).
- [x] Khởi tạo 4 tệp từ điển đối chiếu chuẩn hóa tại [`Data/External/`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Data/External/) (`risky_tlds.txt`, `shorteners.txt`, `target_brands.txt`, `sensitive_keywords.txt`).
- [x] Xây dựng [`Src/Core/config.py`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Src/Core/config.py) cấu hình đường dẫn thư mục `Data/` (Raw, Interim, Processed, External) tối giản.
- [x] Xây dựng [`Src/Core/helpers.py`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Src/Core/helpers.py) (hàm tiện ích nạp `load_set_from_file`).
- [x] Xây dựng [`Src/Core/constants.py`](file:///d:/ML%20trong%20ph%C3%A1t%20hi%E1%BB%87n%20URL%20Phishing/Src/Core/constants.py) định nghĩa các tập hợp hằng số $\mathcal{D}$ (đọc tự động từ `Data/External/` vào `frozenset` $O(1)$).
- [ ] Xây dựng `Src/Core/url_parser.py` (Hàm `parse_url()` trả về Dataclass `ParsedURL` chuẩn RFC 3986 + PSL).
- [ ] Xây dựng `Src/Data/loader.py` (`URLDataLoader`) nạp và chuẩn hóa dữ liệu thô.
- [ ] Xây dựng `Src/Data/splitter.py` (`DomainGroupSplitter`) phân chia Train/Test theo Registered Domain chống rò rỉ dữ liệu.

### Giai đoạn 2: Hệ Thống Trích Xuất Đặc Trưng Hướng Đối Tượng (OOP)
- [ ] Xây dựng `Src/Features/base.py` (Lớp trừu tượng `BaseFeatureExtractor(ABC)`).
- [ ] Xây dựng `Src/Features/lexical.py` (`LexicalFeatureExtractor` - 20+ đặc trưng từ vựng).
- [ ] Xây dựng `Src/Features/hosting.py` (`HostingFeatureExtractor` - 20+ đặc trưng máy chủ).
- [ ] Xây dựng `Src/Features/ngram_tfidf.py` (`NGramTfidfExtractor` - 300 đặc trưng N-gram ký tự).
- [ ] Xây dựng `Src/Features/pipeline.py` (`FeaturePipeline` - Composite điều phối đơn lẻ và chạy song song đa tiến trình).

### Giai đoạn 3: Thực Thi Pipeline & Xuất Ma Trận Số Học
- [ ] Hoàn thiện `Scripts/run.py` đọc dữ liệu từ `Data/Raw/`, thực thi pipeline và xuất ra:
  * `Data/Processed/train_features.csv`
  * `Data/Processed/test_features.csv`
- [ ] Kiểm thử tính đúng đắn của ma trận đặc trưng (không có giá trị NaN/Inf, đúng kiểu dữ liệu số học).

### Giai đoạn 4: Huấn Luyện, Đánh Giá & Báo Cáo Khoa Học (Giai đoạn tiếp theo)
- [ ] Huấn luyện các mô hình Machine Learning (Random Forest, XGBoost, LightGBM).
- [ ] Đánh giá các chỉ số: Precision, Recall, F1-Score, ROC-AUC và Độ trễ suy luận (Inference Latency).
- [ ] Lập bảng so sánh đối chứng (Ablation Study) hoàn thiện báo cáo đề tài.
