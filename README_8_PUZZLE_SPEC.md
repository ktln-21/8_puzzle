# ĐẶC TẢ & TÀI LIỆU HỆ THỐNG GAME 8 PUZZLE — URSINA + PYTHON

> **Mục đích tài liệu:** Mô tả đầy đủ luật chơi, kiến trúc mã nguồn, dữ liệu 60 màn chơi, chế độ chơi ngẫu nhiên tuần tự 60 bàn, giao diện Liquid Glass tím, hiệu ứng, âm thanh, các lớp/hàm đã triển khai, cơ chế lưu tiến trình an toàn và hệ thống AI tự động giải (`A*` & `BFS`). Đây là **tài liệu đặc tả kỹ thuật cho phiên bản hoàn chỉnh hiện tại của trò chơi**.

## 1. Tổng quan dự án

- **Tên trò chơi:** `Neon Clockwork 8 Puzzle`.
- **Ngôn ngữ:** Python.
- **Engine giao diện/game:** Ursina.
- **Lưu dữ liệu:** JSON bằng thư viện chuẩn `json` (cơ chế ghi nguyên tử atomic write).
- **Thể loại:** Trò chơi xếp hình trượt ô $3 \times 3$, một người chơi, gồm **60 màn chơi cố định** tăng dần độ khó, **Chế độ Ngẫu nhiên tuần tự 60 bàn**, và **Chế độ AI Tự động giải (`A*` & `BFS`)**.
- **Phong cách hình ảnh:** Liquid Glass màu tím mờ trong suốt trên nền tím than; panel kính nhiều lớp, viền sáng mảnh, phản chiếu nhẹ, bóng đổ mềm và glow tím/lavender có kiểm soát. Cyan là màu phụ cho hành động chính và bảng AI. Giao diện tách lớp Z rõ ràng, không chồng đè pop-up, mượt mà và dễ thao tác.
- **Điều khiển chính:** Nhấp chuột vào ô số hợp lệ hoặc dùng phím tắt (`Esc` tạm dừng, `U`/`Z` hoàn tác, `R` làm lại). Các nút trên giao diện dùng để đổi màn, phân trang chọn màn, làm lại, hoàn tác, tạm dừng, cài đặt và điều khiển AI tự giải.

### 1.1. Mục tiêu hệ thống (Đã hoàn thiện)

1. Bàn chơi luôn là lưới $3 \times 3$ gồm các số `1` đến `8` và một ô trống (`0`).
2. Luật chỉ cho phép trượt một ô số kề cạnh ô trống theo chiều ngang hoặc chiều dọc.
3. Có đúng **60 màn chơi được định nghĩa sẵn** và kiểm chứng bằng duyệt trạng thái BFS, độ khó tăng dần từ `2` bước đến `30` bước tối ưu.
4. Có **Chế độ Ngẫu nhiên tuần tự 60 bàn**, xáo trộn không trùng lặp toàn bộ 60 bàn để người chơi chinh phục liên tiếp từ bàn `01/60` đến `60/60`.
5. Lưu tiến trình chơi theo màn, chuỗi ngẫu nhiên, kỷ lục và tùy chọn cài đặt bằng JSON; khi mở lại game, người chơi có thể tiếp tục ngay.
6. Tích hợp đầy đủ **AI Solver (`A*` và `BFS`)** trong module độc lập, cho phép tìm lời giải tối ưu, chạy tự động theo 3 mức tốc độ hoặc đi từng bước ngay trên mọi màn chơi.
7. Các thành phần giao diện (`ui/`), logic bàn cờ (`core/`) và thuật toán tìm kiếm (`solver/`) tách biệt hoàn toàn theo mô hình MVC.

## 2. Trạng thái đích — quy ước quan trọng nhất

**Trạng thái đích không phải cách sắp xếp chuẩn phổ biến `1 2 3 / 4 5 6 / 7 8 0`.** Dự án này dùng ô trống ở chính giữa, các số chạy theo chiều kim đồng hồ quanh viền và số `1` ở góc trên bên trái.

```text
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
| 8 |   | 4 |
+---+---+---+
| 7 | 6 | 5 |
+---+---+---+
```

Biểu diễn nội bộ bằng tuple/list một chiều theo thứ tự hàng từ trái sang phải, từ trên xuống dưới:

```python
GOAL_STATE = (1, 2, 3, 8, 0, 4, 7, 6, 5)
```

- `0` luôn biểu thị ô trống; không hiển thị chữ số `0` lên màn hình.
- `1` nằm ở ô góc trên trái (chỉ số `0`).
- Đọc theo chiều kim đồng hồ quanh viền: `1 → 2 → 3 → 4 → 5 → 6 → 7 → 8`.
- Ô chính giữa (chỉ số `4`) là ô trống.
- Mọi hàm kiểm tra thắng, kiểm tra tính giải được (`is_solvable`), dữ liệu 60 màn, giải AI (`A*` / `BFS`) và kiểm thử tự động đều dùng thống nhất `GOAL_STATE` này.

## 3. Luật chơi và hành vi trò chơi

### 3.1. Một nước đi hợp lệ

Một ô số có thể được trượt vào ô trống nếu hai ô kề cạnh theo hàng hoặc cột. Không được di chuyển chéo, không được nhấc ô lên, không được đổi chỗ hai ô số bất kỳ.

Với vị trí dạng chỉ số `i` trong trạng thái 1 chiều (`0..8`):

```python
row = i // 3
col = i % 3
```

Hai ô kề cạnh khi khoảng cách Manhattan giữa tọa độ của chúng bằng `1`:

```text
abs(row_a - row_b) + abs(col_a - col_b) == 1
```

**Chú ý:** Không chỉ kiểm tra `abs(i - j) == 1`, để tránh lỗi nối nhầm vị trí cuối một hàng (chỉ số `2`, `5`) với đầu hàng kế tiếp (chỉ số `3`, `6`).

### 3.2. Kết quả của thao tác

- **Nhấp vào ô không kề ô trống:** Không đổi trạng thái; phát âm thanh báo lỗi nhẹ (`invalid.wav`), hiệu ứng rung ngang ngắn trên ô đó,閃 viền đỏ dịu và hiện thông báo `"Ô không kề ô trống!"` trên HUD.
- **Nhấp vào ô hợp lệ:** Thực hiện đổi chỗ giữa ô số và ô trống, phát âm thanh trượt (`move.wav`), tăng bộ đếm nước đi, lưu trạng thái trước đó vào lịch sử hoàn tác (`move_history`), trượt mượt bằng hoạt ảnh và tự động lưu tiến trình.
- **Khi trạng thái mới bằng `GOAL_STATE`:** Khóa thao tác bàn cờ, phát âm thanh chiến thắng (`win.wav`), chạy hiệu ứng viền phát sáng tuần tự theo chiều kim đồng hồ quanh 8 ô số (`[0, 1, 2, 5, 8, 7, 6, 3]`), ghi nhận hoàn thành màn, cập nhật kỷ lục (nếu chơi tay), mở khóa màn tiếp theo và hiển thị bảng kết quả (`ResultPanel`).
- **Khóa thao tác an toàn:** Không cho xử lý hai lệnh di chuyển chồng nhau khi hoạt ảnh trượt trước đó chưa kết thúc (`is_animating_move`) hoặc khi AI đang trình diễn.

### 3.3. Nút chức năng khi chơi

- **Màn trước / Màn tiếp theo:** Chuyển màn trong danh sách đã mở khóa (ở chế độ thường) hoặc chuyển giữa các bàn trong chuỗi 60 bàn (ở chế độ ngẫu nhiên).
- **Làm lại (`R`):** Đưa bàn về `start_state` của màn hiện tại; đặt lại bộ đếm nước đi và thời gian của lượt hiện tại về `0`.
- **Hoàn tác (`U` / `Z`):** Quay lại trạng thái ngay trước đó trong `move_history`. Thao tác hoàn tác vẫn cộng vào bộ đếm thao tác để đảm bảo tính công bằng của kỷ lục.
- **Tạm dừng (`Esc`):** Tạm dừng đồng hồ, tạm dừng AI (nếu đang chạy) và hiển thị bảng modal `PauseMenu` phủ mờ toàn màn hình.
- **Tự động giải (AI):** Ẩn bảng điều khiển tay bên phải của HUD và mở bảng điều khiển AI (`AutoSolvePanel`) ngay tại vị trí đó (không đè giao diện), tự động tìm lời giải tối ưu từ trạng thái hiện tại.
- **Chọn màn chơi:** Mở bảng chọn 60 màn chơi chia thành 3 trang (20 màn/trang).
- **Menu:** Lưu tiến trình hiện tại và quay về Menu chính.

## 4. Cấu trúc thư mục dự án

```text
8_puzzle/
├── main.py
├── config.py
├── requirements.txt
├── README_8_PUZZLE_SPEC.md
│
├── assets/
│   ├── fonts/
│   │   └── README.txt
│   ├── textures/
│   │   └── README.txt
│   └── sounds/
│       ├── README.txt
│       ├── move.wav
│       ├── invalid.wav
│       ├── win.wav
│       └── click.wav
│
├── core/
│   ├── __init__.py
│   ├── game_manager.py
│   ├── board.py
│   ├── tile_view.py
│   ├── level_manager.py
│   ├── input_controller.py
│   ├── save_manager.py
│   └── sound_manager.py
│
├── ui/
│   ├── __init__.py
│   ├── main_menu.py
│   ├── level_select.py
│   ├── hud.py
│   ├── button_factory.py
│   ├── liquid_glass.py
│   ├── pause_menu.py
│   ├── result_panel.py
│   ├── auto_solve_panel.py
│   └── settings_menu.py
│
├── solver/
│   ├── __init__.py
│   ├── solver_interface.py
│   ├── astar_solver.py
│   └── bfs_solver.py
│
├── data/
│   ├── levels.json
│   ├── save.json
│   └── settings.json
│
└── tests/
    ├── test_board.py
    ├── test_levels.py
    └── test_solver.py
```

### 4.1. Trách nhiệm của từng tệp

| Tệp / thư mục | Trách nhiệm |
|---|---|
| `main.py` | Khởi tạo Ursina, thiết lập cửa sổ/camera, tạo hiệu ứng hạt bụi nền vũ trụ, khởi chạy `GameManager` và vòng lặp chính. |
| `config.py` | Chứa hằng số kích thước lưới, `TOTAL_LEVELS = 60`, `GOAL_STATE`, hàm chuẩn hóa màu `rgba()`, bảng màu Liquid Glass và đường dẫn. |
| `core/board.py` | Logic thuần của bàn cờ (`BoardModel`): trạng thái, ô trống, kiểm tra kề cạnh, di chuyển, sinh hàng xóm, kiểm tra thắng và tính giải được (`is_solvable`). |
| `core/tile_view.py` | Tạo và cập nhật `TileView` thể hiện từng ô kính; xử lý màu, hover scale, viền gợi ý, trượt mượt, rung khi đi sai và phát sáng chiều kim đồng hồ khi thắng. |
| `core/game_manager.py` | Bộ điều phối trung tâm (`GameManager`): quản lý trạng thái game, chế độ 60 màn & chế độ ngẫu nhiên 60 bàn, đồng hồ, lịch sử hoàn tác, âm thanh và chuyển đổi UI không chồng lấn. |
| `core/level_manager.py` | Đọc và xác thực 60 màn từ `levels.json`, kiểm tra tính giải được, mở khóa màn mới và sinh chuỗi hoán vị 60 bàn cho chế độ ngẫu nhiên. |
| `core/input_controller.py` | Chuyển thao tác chuột và phím tắt (`Esc`, `U`, `Z`, `R`) thành lệnh điều khiển; khóa input khi đang chạy animation hoặc AI. |
| `core/save_manager.py` | Đọc/ghi an toàn (atomic write qua file tạm) cho `save.json` và `settings.json`, tự động phục hồi nếu file thiếu hoặc hỏng. |
| `core/sound_manager.py` | Quản lý nạp và phát hiệu ứng âm thanh (`click`, `move`, `invalid`, `win`) theo cài đặt bật/tắt và âm lượng. |
| `ui/liquid_glass.py` | Cung cấp lớp `GlassPanel` (5 lớp: shadow, border, body, highlight, content) và `create_glass_button` chuẩn hóa phong cách kính tím. |
| `ui/button_factory.py` | Factory tạo nút bấm đồng nhất và điều khiển trạng thái bật/tắt (`set_button_enabled`). |
| `ui/main_menu.py` | Giao diện Menu chính: Chơi theo màn, Chế độ Ngẫu nhiên 60 bàn, Chọn màn chơi (60 màn), Cài đặt, Thoát. |
| `ui/level_select.py` | Giao diện chọn 60 màn chơi phân thành 3 trang (20 màn/trang, lưới $5 \times 4$), hiển thị trạng thái Mở/Khóa/Đã xong và kỷ lục số bước. |
| `ui/hud.py` | Thanh trạng thái trên cùng và bảng điều khiển bên phải khi chơi; tự động ẩn bảng phải khi nhường chỗ cho bảng AI. |
| `ui/auto_solve_panel.py` | Bảng điều khiển AI: chọn thuật toán (`A*` / `BFS`), chọn tốc độ (`0.5x`, `1.0x`, `2.0x`), Tìm lời giải, Chạy/Tạm dừng, Bước tiếp, Dừng. |
| `ui/pause_menu.py` | Bảng tạm dừng dạng modal phủ mờ toàn màn hình (`z = -0.15`), chặn click nền phía sau. |
| `ui/result_panel.py` | Bảng kết quả chiến thắng dạng modal (`z = -0.15`), hiển thị số bước, so sánh tối ưu, thời gian, kỷ lục mới và nút chuyển bàn tiếp theo. |
| `ui/settings_menu.py` | Bảng cài đặt dạng modal (`z = -0.18`): bật/tắt âm thanh, gợi ý nước đi hợp lệ, đổi tốc độ hoạt ảnh (`0.5x`, `1.0x`, `2.0x`), đặt lại tiến trình. |
| `solver/solver_interface.py` | Hợp đồng giao tiếp chung `SolverInterface` độc lập với UI. |
| `solver/astar_solver.py` | Thuật toán `AStarSolver` sử dụng khoảng cách Manhattan tùy biến theo tọa độ đích của `GOAL_STATE`. |
| `solver/bfs_solver.py` | Thuật toán `BFSSolver` duyệt chiều rộng tìm đường đi ngắn nhất tối ưu. |
| `data/levels.json` | Dữ liệu tĩnh đã kiểm chứng của 60 màn chơi. |
| `data/save.json` | Lưu tiến trình mở khóa, các màn đã hoàn thành, kỷ lục từng màn và trạng thái chuỗi 60 bàn ngẫu nhiên. |
| `data/settings.json` | Lưu cấu hình âm thanh, tốc độ hoạt ảnh và tùy chọn hiển thị. |
| `tests/` | Bộ 16 kiểm thử tự động (`unittest`) kiểm tra `BoardModel`, 60 màn chơi và thuật toán `A*`/`BFS`. |

## 5. Công nghệ và cài đặt

### 5.1. Thư viện

- Thư viện đồ họa/engine: `ursina`.
- Thư viện chuẩn Python: `json`, `pathlib`, `time`, `os`, `math`, `random`, `heapq`, `collections`, `enum`, `wave`, `struct`, `unittest`.

`requirements.txt`:

```text
ursina
```

Cài đặt và chạy chương trình:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## 6. Thiết kế giao diện

### 6.1. Cửa sổ

- Kích thước mặc định: `1280 × 720`.
- Tiêu đề cửa sổ: `Neon Clockwork 8 Puzzle`.
- Bảng cờ $3 \times 3$ đặt tại khung kính bên trái (`x = -0.20, y = -0.04`), bảng điều khiển HUD hoặc bảng AI đặt bên phải (`x = +0.42, y = -0.04`).
- Sử dụng hệ tọa độ UI 2D (`camera.ui`) của Ursina kết hợp phân tầng trục Z rõ ràng để thao tác chuột chính xác tuyệt đối.

### 6.2. Bố cục màn chơi

```text
┌────────────────────────────────────────────────────────────────────────┐
│ NEON CLOCKWORK 8 PUZZLE          MÀN 07 / 60          [TẠM DỪNG] [MENU]│
├───────────────────────────────────┬────────────────────────────────────┤
│                                   │  ĐỘ KHÓ: DỄ                        │
│           BÀN CỜ 3 × 3            │  ┌──────────────────────────────┐  │
│                                   │  │ Nước đi: 000                 │  │
│        [ 1 ] [ 2 ] [ 3 ]          │  │ Thời gian: 00:00             │  │
│        [ 8 ] [   ] [ 4 ]          │  └──────────────────────────────┘  │
│        [ 7 ] [ 6 ] [ 5 ]          │  [ LÀM LẠI ]      [ HOÀN TÁC ]     │
│                                   │  [     TỰ ĐỘNG GIẢI (AI)     ]     │
│                                   │  [ MÀN TRƯỚC ]    [ MÀN TIẾP ]     │
│                                   │  [       CHỌN MÀN CHƠI       ]     │
│                                   │  Thông báo trạng thái / gợi ý      │
└───────────────────────────────────┴────────────────────────────────────┘
```

Khi bật **Tự động giải (AI)**, khung bên phải chuyển đổi mượt sang **Bảng điều khiển AI Solver** (ẩn bảng nút tay để không bao giờ đè lên nhau):

```text
                                    ├────────────────────────────────────┤
                                    │      BẢNG ĐIỀU KHIỂN AI SOLVER     │
                                    │  ┌──────────────────────────────┐  │
                                    │  │ Lời giải A*: 08 bước (2ms)   │  │
                                    │  │ Tiến độ: 0 / 8 bước          │  │
                                    │  └──────────────────────────────┘  │
                                    │  [THUẬT TOÁN: A*] [THUẬT TOÁN: BFS]│
                                    │  [CHẬM 0.5x] [VỪA 1.0x] [NHANH 2x] │
                                    │  [     TÌM LỜI GIẢI TỐI ƯU    ]    │
                                    │  [        CHẠY TỰ ĐỘNG        ]    │
                                    │  [ BƯỚC TIẾP (+1) ]  [ DỪNG LẠI ]  │
                                    │  [    ĐÓNG BẢNG AI (CHƠI TAY) ]    │
                                    └────────────────────────────────────┘
```

### 6.3. Hệ màu Liquid Glass tím (`config.py`)

Mọi màu sắc được chuẩn hóa qua hàm `rgba(r, g, b, a)` trong `config.py` (tự động quy đổi kênh màu `0..255` sang dải `0.0..1.0` của Panda3D/Ursina):

| Thành phần | Giá trị màu | Cách sử dụng |
|---|---|---|
| Nền chính (`BACKGROUND_COLOR`) | `#100B1C` | Nền tím than sâu làm nổi bật các lớp kính. |
| Nền phụ (`BACKGROUND_SECONDARY`) | `#1A1230` | Vùng sáng dịu phía sau bàn cờ và các hạt bụi vũ trụ. |
| Thân kính (`GLASS_BASE_COLOR`) | `rgba(36, 22, 60, alpha=0.28)` | Panel kính chính bán trong suốt. |
| Thẻ kính (`GLASS_CARD_COLOR`) | `rgba(50, 32, 85, alpha=0.40)` | Thẻ thống kê, thẻ trạng thái bên trong panel. |
| Viền kính (`GLASS_BORDER_COLOR`) | `rgba(231, 222, 255, alpha=0.45)` | Đường viền trắng-lavender sắc nét quanh panel. |
| Phản quang (`GLASS_HIGHLIGHT_COLOR`) | `rgba(255, 255, 255, 35)` | Dải glint phản chiếu ở mép trên của mặt kính. |
| Nhấn chính (`ACCENT_LAVENDER`) | `#BCA7FF` | Tiêu đề, viền nhấn và thông báo. |
| Nhấn phụ (`ACCENT_PURPLE`) | `#9672F5` | Hiệu ứng tương tác và glow. |
| Nhấn hành động (`ACCENT_CYAN`) | `#8DEBFF` | Nút Chế độ ngẫu nhiên 60 bàn, nút AI Solver và thông báo kỷ lục. |
| Chữ chính (`TEXT_PRIMARY_COLOR`) | `#F8F5FF` | Chữ số trên ô cờ, tiêu đề và nhãn nút bấm. |
| Chữ phụ (`TEXT_SECONDARY_COLOR`) | `#C4BBD9` | Bộ đếm thời gian và thông tin phụ. |
| Ô trống (`TILE_EMPTY_COLOR`) | `#171024` | Tạo cảm giác hốc lõm tối ở vị trí trống. |
| Hoàn thành (`SUCCESS_COLOR`) | `#6EE7B7` | Xanh mint cho màn đã qua và hiệu ứng chiến thắng. |
| Cảnh báo (`ERROR_COLOR`) | `#F87171` | Hồng đỏ dịu khi nhấp vào ô không hợp lệ hoặc nút nguy hiểm. |

### 6.4. Phân tầng độ sâu Z (Tránh chồng đè giao diện)

Hệ thống UI tuân thủ nghiêm ngặt thứ tự trục Z trong `camera.ui` (giá trị Z âm hơn nằm gần camera hơn):

1. **Lớp nền (`z = +0.09` đến `+0.08`):** Nền phụ và 18 hạt bụi ánh sáng trôi chậm.
2. **Lớp bàn cờ & HUD (`z = 0.0` đến `-0.02`):** Khung kính bàn cờ, 9 ô `TileView`, thanh HUD trên và bảng điều khiển bên phải (`HUD.side_panel` hoặc `AutoSolvePanel`).
3. **Lớp Modal Pop-up (`z = -0.15`):** `PauseMenu` và `ResultPanel` kèm lớp phủ tối toàn màn hình (`dimmer` có `collider="box"`) che mờ lớp dưới và chặn click nhầm vào bàn cờ.
4. **Lớp Cài đặt (`z = -0.18`):** `SettingsMenu` nằm ở tầng cao nhất; khi mở từ `PauseMenu` sẽ tạm ẩn `PauseMenu` và tự khôi phục lại khi đóng.

## 7. Hiệu ứng và âm thanh

### 7.1. Hiệu ứng thị giác

1. **Hover ô số & nút bấm:** Phóng nhẹ theo `HOVER_SCALE = 1.03` trong `0.10s` với đường cong `curve.out_quad` và làm sáng viền kính.
2. **Gợi ý nước đi hợp lệ (`show_valid_move_hint`):** Các ô kề cạnh ô trống có viền sáng màu cyan/lavender (`TILE_BORDER_VALID_COLOR`), có thể bật/tắt trong Cài đặt.
3. **Trượt ô (`MOVE_ANIMATION_DURATION = 0.14s`):** Ô số trượt mượt sang vị trí ô trống; tốc độ trượt có thể chỉnh nhanh/chậm (`0.5x`, `1.0x`, `2.0x`) trong Cài đặt.
4. **Nước đi không hợp lệ:** Ô rung ngang nhẹ (`±0.012` đơn vị) và nháy viền `ERROR_COLOR` trong `0.14s`.
5. **Chiến thắng màn:** Viền 8 ô xung quanh sáng lên và phóng nhẹ lần lượt theo chiều kim đồng hồ (`WIN_STEP_DELAY = 0.08s`), sau đó mở bảng `ResultPanel`.

### 7.2. Hệ thống âm thanh (`assets/sounds/`)

Các tệp âm thanh synth chuẩn `.wav` được nạp qua đường dẫn tương đối trong `SoundManager` (tránh lỗi ký tự Unicode trên đường dẫn Windows):
- `click.wav`: Âm nhấn nút giao diện ngắn, trong.
- `move.wav`: Âm trượt ô cơ học êm.
- `invalid.wav`: Âm trầm ngắn báo nước đi không hợp lệ.
- `win.wav`: Chuỗi hợp âm C5–E5–G5–C6 ngân vang khi thắng màn.

## 8. Dữ liệu 60 màn chơi & Chế độ Ngẫu nhiên 60 bàn

### 8.1. Bộ 60 màn chơi chuẩn (`data/levels.json`)

- Toàn bộ **60 màn chơi** (ID từ `1` đến `60`) được trích xuất từ đồ thị trạng thái 181.440 đỉnh có thể đi tới `GOAL_STATE = (1, 2, 3, 8, 0, 4, 7, 6, 5)`.
- Tất cả 60 màn có trạng thái khởi đầu (`start_state`) hoàn toàn khác nhau và khác `GOAL_STATE`.
- Chỉ số `optimal_moves` (độ dài lời giải tối ưu ngắn nhất kiểm chứng bằng BFS) tăng dần đều từ **2 nước** (Màn 01) đến **30 nước** (Màn 60 — độ sâu tối đa của không gian trạng thái):
  - **Màn 01 – 17 (`Rất dễ`):** `2` đến `6` bước tối ưu.
  - **Màn 18 – 35 (`Dễ`):** `7` đến `12` bước tối ưu.
  - **Màn 36 – 43 (`Trung bình`):** `13` đến `18` bước tối ưu.
  - **Màn 44 – 51 (`Khó`):** `19` đến `24` bước tối ưu.
  - **Màn 52 – 60 (`Rất khó`):** `25` đến `30` bước tối ưu.

### 8.2. Quy tắc tiến trình Chế độ Theo màn (Campaign Mode)

- Mở khóa Màn 01 khi bắt đầu game lần đầu.
- Khi hoàn thành màn `n`, đánh dấu `n` vào `completed_levels` và mở khóa màn `n + 1` (tối đa đến màn `60`).
- Chơi lại màn cũ không làm mất tiến trình các màn đã mở khóa.
- Giao diện Chọn màn (`LevelSelectMenu`) hiển thị 60 màn chia thành **3 trang** (20 màn/trang, lưới $5 \times 4$), tự động mở đúng trang chứa màn người chơi đang dừng lại.

### 8.3. Chế độ Ngẫu nhiên tuần tự 60 bàn (Random Sequential 60 Mode)

- Khi chọn **`CHẾ ĐỘ NGẪU NHIÊN (60 BÀN)`** ở Menu chính, `LevelManager.generate_random_sequence()` tạo một hoán vị ngẫu nhiên gồm đủ 60 ID màn chơi (`1..60`) không trùng lặp.
- Người chơi sẽ chơi tuần tự qua đủ 60 bàn theo thứ tự ngẫu nhiên đó: `NGẪU NHIÊN 01/60` → `02/60` → ... → `60/60`.
- Chuỗi hoán vị `random_sequence` và vị trí bàn hiện tại `random_index` được lưu tự động vào `data/save.json` để có thể thoát ra và chơi tiếp bất cứ lúc nào.

## 9. Mẫu schema JSON

### 9.1. `data/levels.json`

```json
{
  "schema_version": 1,
  "goal_state": [1, 2, 3, 8, 0, 4, 7, 6, 5],
  "goal_board": [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
  ],
  "goal_definition": "Các số xếp theo chiều kim đồng hồ quanh viền, bắt đầu từ góc trên trái; ô trống ở giữa. Giá trị 0 biểu thị ô trống.",
  "levels": [
    {
      "id": 1,
      "name": "Màn 01",
      "difficulty": "Rất dễ",
      "start_board": [[1, 2, 3], [8, 4, 5], [7, 6, 0]],
      "start_state": [1, 2, 3, 8, 4, 5, 7, 6, 0],
      "optimal_moves": 2
    }
  ]
}
```

### 9.2. `data/save.json`

```json
{
  "schema_version": 1,
  "unlocked_level": 1,
  "completed_levels": [],
  "current_level": 1,
  "current_state": [1, 2, 3, 8, 0, 4, 7, 6, 5],
  "current_moves": 0,
  "elapsed_seconds": 0.0,
  "best_records": [],
  "game_completed": false,
  "random_sequence": [],
  "random_index": 0
}
```

### 9.3. `data/settings.json`

```json
{
  "schema_version": 1,
  "sound_enabled": true,
  "music_enabled": true,
  "sound_volume": 0.7,
  "music_volume": 0.4,
  "animation_speed": 1.0,
  "panel_alpha": 0.28,
  "glass_glow_enabled": true,
  "background_particles_enabled": true,
  "reduced_motion": false,
  "show_valid_move_hint": true,
  "window_width": 1280,
  "window_height": 720
}
```

### 9.4. Ghi file nguyên tử (Atomic Save)

`SaveManager.save_json_atomic()` luôn ghi dữ liệu ra file tạm `.tmp.json` trước, sau đó dùng `Path.replace()` để thay thế file đích. Nếu file JSON bị hỏng, hệ thống tự động sao lưu sang `.corrupt.bak` và khôi phục dữ liệu mặc định, đảm bảo game không bao giờ bị crash khi khởi động.

## 10. Các lớp và phương thức chính đã triển khai

### 10.1. `core/board.py` — `BoardModel`
- `validate_state(state)`: Kiểm tra đủ 9 phần tử và là hoán vị của `0..8`.
- `get_state()` / `set_state(state)` / `reset()`.
- `find_empty(state=None)`: Trả về chỉ số của ô `0`.
- `are_adjacent(index_a, index_b)`: Kiểm tra khoảng cách Manhattan bằng `1`.
- `can_move(tile_index)` / `move_tile(tile_index)`.
- `get_valid_moves(state=None)`: Trả về danh sách các chỉ số ô có thể trượt vào ô trống.
- `get_neighbors(state=None)`: Sinh danh sách các tuple trạng thái kế tiếp hợp lệ mà không làm biến đổi trạng thái gốc.
- `is_goal(state=None)`: So sánh với `GOAL_STATE`.
- `count_inversions(state)` & `check_solvability(state, goal_state=GOAL_STATE)`: Kiểm tra tính giải được bằng tính bất biến chẵn/lẻ của số nghịch thế (loại trừ `0`) trong lưới $3 \times 3$.

### 10.2. `core/level_manager.py` — `LevelManager`
- `load_levels(path)` & `validate_levels(data)`: Kiểm tra nghiêm ngặt đủ 60 màn (`config.TOTAL_LEVELS`), không trùng ID, không trùng `start_state`, khớp `start_board`, giải được tới `GOAL_STATE` và `optimal_moves` tăng dần.
- `get_level(level_id)` / `get_start_state(level_id)` / `get_level_count()`.
- `generate_random_sequence()`: Sinh danh sách 60 ID màn chơi xáo trộn ngẫu nhiên.
- `unlock_next_level(completed_level_id, current_unlocked)`.

### 10.3. `core/game_manager.py` — `GameManager`
- Điều phối trạng thái `GameState`: `MENU`, `LEVEL_SELECT`, `PLAYING`, `PAUSED`, `ANIMATING`, `SOLVING`, `LEVEL_COMPLETE`, `GAME_COMPLETE`.
- `start_level(level_id, resume_state=None, is_random_mode=None)`: Khởi tạo bàn cờ cho cả chế độ thường và chế độ ngẫu nhiên 60 bàn.
- `start_random_60_mode()` / `advance_after_win()` / `next_level()` / `prev_level()`.
- `request_move(tile_index, source="player")` / `apply_ai_step(next_state, anim_duration=...)`.
- `undo_move()` / `restart_level()` / `toggle_pause()` / `complete_level(is_ai=False)`.
- `open_auto_solve()` / `close_auto_solve()`: Chuyển đổi mượt giữa `HUD.side_panel` và `AutoSolvePanel`.

## 11. Chế độ tự động giải (AI Solver: A* & BFS)

### 11.1. Kiến trúc tách biệt
- `solver/solver_interface.py` định nghĩa lớp cơ sở `SolverInterface` với phương thức `solve(start_state, goal_state)` và `cancel()`.
- Thuật toán hoàn toàn độc lập với Ursina, nhận vào tuple trạng thái và trả về `list[tuple[int, ...]]` là chuỗi trạng thái sau từng bước đi dẫn tới `GOAL_STATE`.

### 11.2. Hai thuật toán tìm kiếm tối ưu
1. **`AStarSolver` (`solver/astar_solver.py`):**
   - Sử dụng hàng đợi ưu tiên `heapq` với hàm đánh giá $f(n) = g(n) + h(n)$.
   - Hàm heuristic $h(n)$ là tổng khoảng cách Manhattan của 8 ô số (`1..8`) từ vị trí hiện tại tới đúng tọa độ đích của chúng trong `GOAL_STATE = (1, 2, 3, 8, 0, 4, 7, 6, 5)`.
   - Vì Manhattan distance là heuristic chấp nhận được (admissible) và nhất quán (consistent), `A*` luôn tìm ra lời giải ngắn nhất tối ưu chỉ trong vài mili-giây trên cả 60 màn.
2. **`BFSSolver` (`solver/bfs_solver.py`):**
   - Sử dụng hàng đợi hai đầu `collections.deque` duyệt theo từng tầng độ sâu, đảm bảo tìm ra đường đi ít bước nhất để đối chiếu trực tiếp với `A*`.

### 11.3. Chế độ trình diễn trực quan
- Ngay khi mở bảng AI hoặc đổi thuật toán (`A*` / `BFS`), solver lập tức tính toán lời giải từ trạng thái hiện tại của bàn cờ và hiển thị tổng số bước cùng thời gian chạy (`ms`).
- Người chơi có thể:
  - Nhấn **`CHẠY TỰ ĐỘNG`** để AI tự trượt từng ô trên bàn cờ theo tốc độ đã chọn (`0.5x`, `1.0x`, `2.0x`).
  - Nhấn **`TẠM DỪNG CHẠY`** hoặc **`DỪNG LẠI`** bất kỳ lúc nào để lấy lại quyền điều khiển tay ngay tại trạng thái đó.
  - Nhấn **`BƯỚC TIẾP (+1)`** để quan sát từng nước đi tối ưu một.
- Khi AI giải xong màn chơi, màn đó vẫn được mở khóa, nhưng thành tích của AI không ghi đè vào kỷ lục chơi tay (`best_records`) của người chơi.

## 12. Kiểm thử tự động (`tests/`)

Chạy toàn bộ 16 bài kiểm thử đơn vị bằng lệnh:

```bash
python -m unittest discover tests
```

- `tests/test_board.py`: Kiểm tra nhận diện `GOAL_STATE`, kiểm tra luật kề cạnh, chặn lỗi nối mép hàng, tính bất biến của tập giá trị `0..8`, tính bất biến của `get_neighbors()`, và hàm kiểm tra tính giải được `check_solvability()`.
- `tests/test_levels.py`: Kiểm tra đủ 60 màn chơi (`ID 1..60`), không trùng lặp trạng thái, khớp ma trận $3 \times 3$, cả 60 màn đều giải được tới `GOAL_STATE`, `optimal_moves` tăng dần và kiểm tra hàm sinh chuỗi 60 bàn ngẫu nhiên.
- `tests/test_solver.py`: Kiểm tra `A*` và `BFS` khi trạng thái đầu là đích, khi trạng thái không giải được, đối chiếu kết quả giữa `A*` và `BFS`, và **chạy `A*` giải thử toàn bộ 60 màn chơi** để xác nhận độ dài đường đi tìm được khớp 100% với `optimal_moves`.

## 13. Tài liệu Ursina tham khảo

- **Documentation:** <https://www.ursinaengine.org/documentation.html>
- **API Reference:** <https://www.ursinaengine.org/api_reference.html>
- **Entity Basics:** <https://www.ursinaengine.org/entity_basics.html>
- **GitHub Ursina:** <https://github.com/pokepetter/ursina>
