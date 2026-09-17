"""Vietnamese teaching content; community-reviewable, no automatic translation service."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
# question, body, worked example, misconception, exercise, quiz question, options, explanation
V={
'dikwp':[
'Vì sao cùng một số “30” có thể dẫn đến những quyết định khác nhau?',
'DIKWP phân biệt dữ liệu (D), thông tin theo ngữ cảnh (I), tri thức có thể tái sử dụng (K), sự cân nhắc giá trị và hệ quả (W), cùng mục đích (P). Đây là năm loại tài nguyên ngữ nghĩa tương tác, không phải năm bậc xếp hạng. Một quan sát có thể được diễn giải khác nhau khi người thụ hưởng hoặc mục đích thay đổi. Hãy làm rõ phép chuyển đổi giữa các loại tài nguyên thay vì chỉ gắn nhãn.',
'D: cảm biến lớp học ghi 30 °C. I: nhiệt độ cao hơn mức mục tiêu 4 °C. K: thông gió ảnh hưởng đến cả nhiệt độ và tiếng ồn. W: cân nhắc sự thoải mái, năng lượng và lớp bên cạnh. P: cải thiện điều kiện học tập, không phải giảm nhiệt độ bằng mọi giá.',
'Thêm năm nhãn D/I/K/W/P không tự tạo ra khả năng hiểu. Cần giải thích ngữ cảnh, phép biến đổi và hệ quả.',
'Chọn một vấn đề học tập của bạn. Viết năm trường D/I/K/W/P, sau đó thay đổi người thụ hưởng và chỉ ra trường nào phải được sửa.',
'Mục nào thể hiện Purpose trực tiếp nhất?',
['Một giá trị cảm biến','Một quy tắc chuyển đổi','Thay đổi mong muốn và người được hưởng lợi'],
'Purpose xác định thay đổi mong muốn và đối tượng được phục vụ. Giá trị cảm biến là dữ liệu; quy tắc chuyển đổi là một dạng tri thức.'],
'context':[
'Vì sao một bản dịch có vẻ đúng vẫn có thể gây ra hành động sai?',
'Ý nghĩa của một bản ghi phụ thuộc vào thực thể, đơn vị, tiền tệ, thời điểm và mục đích sử dụng. Cầu nối đa ngôn ngữ dùng mã khái niệm chung để nối các cách diễn đạt, nhưng phải giữ lại các điều kiện này. Thí nghiệm trong nền tảng so sánh các trường ngữ nghĩa có cấu trúc; nó không tự hiểu mọi văn bản tự do.',
'1000 kg và 1 tấn tương đương về khối lượng; 1000 kg và 1000 g thì không. 100 CNY và 100 VND không tương đương nếu chưa có tỷ giá cụ thể kèm thời điểm.',
'Chuỗi ký tự giống nhau chưa chắc có cùng nghĩa. Chuỗi khác nhau cũng chưa chắc mâu thuẫn.',
'Trong phòng thí nghiệm đối chiếu ngữ nghĩa, đổi kg thành tonne và giữ đúng số lượng. Sau đó chỉ đổi tiền tệ hoặc mục đích để quan sát kết quả.',
'Nên xử lý 1000 kg và 1 tonne như thế nào?',
['Luôn coi là mâu thuẫn','Tương đương sau khi chuẩn hóa khối lượng','Chỉ so khớp chuỗi mới quyết định được'],
'Sau chuẩn hóa, cả hai đều là 1000 kg. Kết luận còn phụ thuộc việc các trường thực thể, mục đích và tiền tệ có phù hợp hay không.'],
 'three-no':[
'Hệ thống có thể tiếp tục hỗ trợ khi dữ liệu thiếu hoặc mâu thuẫn như thế nào?',
'3-No phân biệt tính không đầy đủ, không nhất quán và không chính xác. Thiếu một quan sát khác với hai quan sát xung đột. Một khoảng giá trị thể hiện độ không chính xác; không nên tự biến nó thành một giá trị chắc chắn. Thí nghiệm dùng giao các khoảng để kiểm tra sự nhất quán và giữ lại bao khoảng để cho thấy toàn bộ độ phân tán.',
'Hai cảm biến chuỗi lạnh báo [2,4] và [6,8] °C. Hai khoảng không giao nhau nên không hỗ trợ một nhiệt độ nhất quán chung. Nếu cảm biến thứ hai không gửi dữ liệu thì đó là thiếu dữ liệu, không phải mâu thuẫn.',
'Lấy trung bình có thể che giấu xung đột. Điền số 0 vào trường thiếu có thể tạo ra một quan sát không tồn tại.',
'Chạy ba trường hợp: khoảng giao nhau, khoảng rời nhau và quan sát bị thiếu. So sánh kết quả trung bình với kết quả giữ nguyên các loại bất định.',
'Nên xử lý quan sát thiếu và quan sát mâu thuẫn ra sao?',
['Thay cả hai bằng số 0','Ghi lý do riêng và câu hỏi cần làm rõ','Lấy trung bình cho cả hai'],
'Phân biệt nguyên nhân giúp xác định thông tin còn cần thu thập và phần kết luận vẫn có thể sử dụng.'],
'purpose':[
'Vì sao một câu trả lời trông đúng vẫn có thể không giải quyết được vấn đề của sinh viên?',
'Mục đích phải gắn với người học, thay đổi họ muốn đạt được và các điều kiện thực tế. Hệ thống có thể đề xuất cách làm nhưng không nên âm thầm thay mục tiêu học hiểu bằng mục tiêu tạo ra một sản phẩm hoàn chỉnh. Trong thí nghiệm đường đi ngữ nghĩa, hãy so sánh mục tiêu tốc độ với mục tiêu hiểu và kiểm chứng; các trọng số là giả định phục vụ giảng dạy.',
'Một sinh viên muốn hiểu thuật toán, không chỉ nhận đáp án. Đường đi phù hợp có thể bao gồm giải thích, phản ví dụ và thí nghiệm sửa được thay vì chỉ cung cấp mã cuối cùng.',
'Mục đích không đồng nghĩa với quyền thực hiện mọi hành động. Một kết quả có ích cũng không tự cho phép hệ thống thay đổi quyết định của người học.',
'Viết mục tiêu bằng một câu, nêu người thụ hưởng và một điều không nên tự quyết thay họ. Thay mục tiêu trong phòng thí nghiệm đường đi và so sánh các lựa chọn.',
'Ai nên sửa mục tiêu thực chất của sinh viên?',
['Hệ thống tự sửa mà không thông báo','Sinh viên hoặc bên được ủy quyền rõ ràng','Bảng xếp hạng độ phổ biến của kho mã'],
'Hệ thống hỗ trợ làm rõ và đề xuất; thay đổi mục tiêu thực chất phải thuộc về người học hoặc người có thẩm quyền phù hợp.'],
'pact':[
'Làm thế nào xác định bước mà một tác tử đi chệch mục đích?',
'PACT cung cấp một hướng nghiên cứu liên kết mục đích, phạm vi cho phép, bằng chứng và dấu vết hành động. Trong nền tảng này, bộ kiểm tra giảng dạy so sánh mục đích đã nêu, mục đích quan sát được, hành động được phép và số bằng chứng. Đây là cách luyện thiết kế kiểm tra có thể giải thích; không phải dịch vụ gửi thư thật hay bản sao đầy đủ của PACT.',
'Quyền sắp xếp dữ liệu sản phẩm xuyên biên giới không tự bao gồm quyền gửi báo giá. Hệ thống vẫn có thể soạn bản nháp và để người được phép quyết định việc gửi.',
'Chỉ biết hệ thống trả lời đúng chưa đủ để biết nó có giữ mục đích và phạm vi được giao hay không. Ngược lại, từ chối mọi hành động cũng làm mất hỗ trợ hữu ích.',
'Thử gửi khi chỉ được soạn nháp, rồi cho phép gửi và giữ nguyên các điều kiện khác. Tìm trường hợp bộ lọc từ khóa chặn quá mức.',
'Khi chưa được phép gửi, việc hữu ích nào vẫn có thể tiếp tục?',
['Không làm gì cả','Chuẩn bị bản nháp để xem xét','Bỏ qua quyền và gửi luôn'],
'Có thể tiếp tục phần việc nằm trong phạm vi được giao. Bản nháp và hành động gửi là hai việc khác nhau.'],
'evidence':[
'Mười trang sao chép nhau có phải là mười nguồn bằng chứng độc lập?',
'Mỗi phát biểu cần có quan hệ rõ với nguồn, ngày, bối cảnh và loại hỗ trợ. Một nghiên cứu, bản tin giới thiệu nghiên cứu và báo cáo tái lập có vai trò khác nhau. Ghi nguồn gốc chung giúp tránh đếm bản sao như thí nghiệm độc lập, đồng thời vẫn ghi nhận giá trị phổ biến kiến thức của chúng.',
'Ba trang tin cùng dẫn một bài báo vẫn có một nguồn nghiên cứu gốc. Một nhóm khác tái lập thành công thí nghiệm bổ sung một loại bằng chứng khác.',
'Nhiều đường dẫn không tự đồng nghĩa với nhiều phép kiểm chứng độc lập; nhưng điều đó cũng không làm các kênh phổ biến mất mọi giá trị.',
'Chọn một khẳng định từ bài giảng, nối nó với nguồn gốc và ghi rõ đang dùng trích dẫn, áp dụng phương pháp hay kết quả thực nghiệm.',
'Nên biểu diễn ba bản đăng lại một nghiên cứu như thế nào?',
['Ba thí nghiệm độc lập','Ba liên kết phổ biến, một nhóm nguồn gốc','Hoàn toàn không có giá trị'],
'Giữ cả số kênh phổ biến và nguồn nghiên cứu gốc, thay vì đánh đồng hai loại ảnh hưởng.'],
 'triz':[
'Tăng độ chính xác với chi phí cao hơn có nhất thiết là lựa chọn một mất một còn?',
'DIKWP-TRIZ gợi ý diễn đạt mâu thuẫn thiết kế theo dữ liệu, tri thức, hệ quả và mục đích. Hãy hỏi có thể tách tình huống, thay biểu diễn hay phân bổ xử lý khác nhau hay không. Một ý tưởng chỉ trở thành giả thuyết nghiên cứu khi nêu rõ thay đổi, đầu vào giữ nguyên và kết quả cần so sánh.',
'Kiểm tra sản phẩm đa ngôn ngữ phải nhanh và đáng tin cậy: kiểm tra đơn vị và mã thực thể nhẹ trước, chuyển trường hợp mơ hồ cho con người thay vì xử lý mọi mục với cùng độ phức tạp.',
'Gắn tên “sáng tạo” hoặc bổ sung nhiều chức năng chưa chứng minh cải tiến. Cần giữ mốc so sánh và tìm trường hợp mới giải quyết tốt hơn.',
'Viết một mâu thuẫn trong vấn đề của bạn, đề xuất hai cơ chế khác nhau, rồi chọn đầu vào có thể phân biệt kết quả của chúng.',
'Làm thế nào để một tuyên bố đổi mới có thể kiểm tra được?',
['Đổi tên hệ thống','Giữ đường cơ sở, nêu thay đổi và so sánh kết quả','Chỉ thêm nhiều tính năng'],
'Đường cơ sở và điều kiện so sánh giúp xác định tác dụng của thay đổi thay vì chỉ thể hiện khác biệt về tên.'],
'repo':[
'Làm sao chọn tổ hợp phù hợp trong 483 mục kho mã?',
'Bắt đầu từ vấn đề và năng lực hiện tại, sau đó tìm phương pháp, vai trò thành phần, giấy phép và cách tái lập. La bàn kho mã giải thích điểm phù hợp dựa trên thẻ khái niệm, văn bản và mục tuyển chọn. Điểm này không phải xếp hạng giá trị khoa học hay xác suất thành công. Hãy so sánh vài lựa chọn và ghi lý do chọn từng thành phần.',
'Một bài toán xuyên ngôn ngữ có thể kết hợp tổ chức ngữ nghĩa của MESH², kiểm tra mục đích của PACT và cấu trúc nguồn gốc của VerityWeave. Đây là đề xuất thiết kế; giao diện thực tế phải được kiểm tra.',
'Nhiều sao không đảm bảo kho mã phù hợp với vấn đề. Tên kho mã hoặc bản giới thiệu cũng không thay thế việc đọc mã và thử nghiệm.',
'Dùng cùng một vấn đề để tìm bằng tiếng Việt và tiếng Anh. Chọn tối đa sáu thành phần, giải thích vai trò và phần bạn cần tự bổ sung.',
'Điểm đề xuất trong nền tảng thể hiện điều gì?',
['Xếp hạng đóng góp khoa học','Mức phù hợp giữa vấn đề hiện tại và thẻ trong danh mục','Xác suất thành công thương mại'],
'Đây là công cụ điều hướng minh bạch theo ngữ cảnh học tập, không phải kết quả đánh giá khoa học các kho mã.'],
'inherit':[
'Làm sao để người khác biết chính xác bạn đã kế thừa gì?',
'Ghi tên kho mã, nguồn, commit bất biến, giấy phép, dữ liệu đầu vào và vai trò của thành phần. Giữ mã gốc tách khỏi bộ điều hợp mới. Tệp khóa upstream và biên nhận tải về giúp truy vết phiên bản và hàm băm. Script của nền tảng tải và kiểm tra gói mã, không tự chạy mã tải về.',
'Nhánh main thuận tiện để đọc, nhưng thí nghiệm cần chốt commit vì hành vi có thể thay đổi giữa các phiên bản.',
'Có thể xem mã công khai không có nghĩa mọi điều kiện tái sử dụng đều giống nhau. Giấy phép của nền tảng mới không thay giấy phép của thành phần kế thừa.',
'Xuất một gói dự án, đọc upstream.lock.json và ADAPTATION.md. Chỉ rõ ý tưởng kế thừa, phần mã dự định dùng và thay đổi mới của bạn.',
'Định danh nào phù hợp cho thí nghiệm có thể tái lập?',
['Nhánh main luôn thay đổi','Commit SHA bất biến cùng đầu vào đã ghi','Số lượt xem trang'],
'Commit cố định xác định phiên bản; đầu vào và cách chạy xác định điều kiện tái lập.'],
'evaluate':[
'Làm sao biết cơ chế bổ sung thực sự giúp ích?',
'So sánh có ý nghĩa giữ nguyên đầu vào và thay đổi một cơ chế có chủ đích. Thí nghiệm loại bỏ thành phần giúp xem cơ chế nào tạo ra khác biệt; phản ví dụ chỉ ra giới hạn còn lại. Ghi cả trường hợp được cải thiện lẫn trường hợp thất bại. Không diễn giải kết quả của ví dụ tổng hợp thành hiệu quả ngoài thực tế.',
'Bỏ chuẩn hóa đơn vị sẽ từ chối sai 1000 kg so với 1 tonne; bỏ kiểm tra tiền tệ có thể chấp nhận sai hai khoản tiền khác đồng tiền.',
'Điểm cao trên các ví dụ đi kèm chưa chứng minh hiệu quả với mọi dữ liệu mới. Che giấu lỗi làm mất khả năng học và cải tiến.',
'Chạy bản đầy đủ, loại bỏ một kiểm tra, rồi tạo phản ví dụ. Lưu đầu vào, hai kết quả và giải thích của bạn vào hồ sơ dự án.',
'Nên thiết kế thí nghiệm loại bỏ thành phần như thế nào?',
['Thay tất cả thành phần','Bỏ một cơ chế và giữ đầu vào cố định','Xóa những ví dụ thất bại'],
'Chỉ thay một cơ chế giúp liên hệ khác biệt quan sát được với thay đổi đó trong điều kiện thí nghiệm.'],
'consciousness':[
'Làm sao nghiên cứu trí nhớ, mục đích và tính liên tục thay vì chỉ dùng nhãn?',
'Có thể chuyển lý thuyết về ý thức nhân tạo thành các câu hỏi thao tác được: mục đích có được giữ qua nhiều bước không, bằng chứng mới có sửa kết luận không, ký ức nào được giữ hoặc điều chỉnh? Các chỉ báo như vậy tạo ra thí nghiệm về chức năng. Chúng không tự xác nhận trải nghiệm chủ quan.',
'Một tác tử giữ mục đích của dự án qua nhiều cuộc trao đổi nhưng sửa kết luận khi nhận bằng chứng mới. Đây là một nhiệm vụ để nghiên cứu tính liên tục và khả năng điều chỉnh.',
'Đặt tên “ý thức” cho một chương trình không chứng minh nó có trải nghiệm. Cần phân biệt giả thuyết lý thuyết, chức năng quan sát được và kết luận thực nghiệm.',
'Viết một chuỗi ba tình huống có thông tin mới. Nêu điều gì phải được giữ, điều gì cần sửa và quan sát nào sẽ bác bỏ giả thuyết của bạn.',
'Câu nào là một câu hỏi nghiên cứu có thể thao tác?',
['Tuyên bố ý thức từ tên chương trình','Giải thích việc giữ mục đích và sửa kết luận sau bằng chứng mới','Chỉ so sánh hình thức giao diện'],
'Câu hỏi thao tác xác định hành vi và điều kiện quan sát, thay vì chỉ gắn một tên gọi.'],
'create':[
'Giải quyết vấn đề của bạn có thể giúp người học tiếp theo như thế nào?',
'Một đóng góp có thể là bộ điều hợp nhỏ, bản dịch thuật ngữ tốt hơn, ví dụ thất bại tái lập được, bài hướng dẫn hoặc một phương pháp mới. Hồ sơ đóng góp cần tách phần kế thừa khỏi phần thay đổi, giữ nguồn và phiên bản, trình bày bằng chứng và giới hạn. Người học tự chọn khi nào và ở đâu chia sẻ.',
'Một sinh viên tìm thấy đơn vị mơ hồ trong hồ sơ sản phẩm tiếng Việt, bổ sung quy tắc theo ngữ cảnh và một ca kiểm thử thất bại trước khi sửa, đồng thời giữ ví dụ gốc và ghi công tác giả.',
'Không cần tuyên bố đã giải quyết toàn bộ một lĩnh vực mới có đóng góp. Một phản ví dụ rõ ràng có thể giúp cộng đồng cải tiến phương pháp.',
'Hoàn thành vấn đề, phần kế thừa, thay đổi, giả thuyết và suy ngẫm. Xuất gói có mã, dữ liệu, kiểm thử và ghi chú đóng góp để người khác đọc và chạy.',
'Điều nào có thể là một đóng góp có giá trị?',
['Một phản ví dụ kèm đầu vào và cách tái lập','Chỉ đổi tên dự án','Ẩn toàn bộ nguồn gốc'],
'Phản ví dụ có thể tái lập tạo tri thức hữu ích và mở đường cho sửa đổi có thể kiểm tra.']}
def apply():
    p=ROOT/'data/lessons.json';lessons=json.loads(p.read_text(encoding='utf-8'))
    for l in lessons:
        q,b,e,m,pr,qq,opts,ex=V[l['id']]
        for k,v in [('question',q),('body',b),('example',e),('misconception',m),('practice',pr)]:l[k]['vi']=v
        l['quiz']['question']['vi']=qq;l['quiz']['options']['vi']=opts;l['quiz']['explanation']['vi']=ex
    p.write_text(json.dumps(lessons,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':apply()
