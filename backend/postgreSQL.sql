-- Bật extension UUID (bắt buộc)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- table guests chỉ tạo khi có giao dịch lưu trú
-- lưu thông tin khách hàng chỉ là khách vãng lai (không có tài khoản)
-- nếu user role CUSTOMER, STAFF tự book phòng thì lưu trong gusets
-- nếu user role CUSTOMER, STAFF book phòng hộ thì lưu người được book hộ trong gusets
CREATE TABLE IF NOT EXISTS guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NULL, -- nếu guest có tài khoản
    full_name VARCHAR(255) NOT NULL,
    id_type VARCHAR(20) NOT NULL,      -- CCCD / Passport
    id_number VARCHAR(50) UNIQUE NOT NULL,    -- số CCCD / Passport
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    nationality VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_guests_user_id ON guests(user_id); -- Tìm guest theo user_id
CREATE UNIQUE INDEX idx_guests_id_number ON guests(id_number); -- Tìm guest theo số CCCD / Passport
CREATE INDEX idx_guests_phone ON guests(phone);
CREATE INDEX idx_guests_email ON guests(email);

-- table users
CREATE TYPE user_role AS ENUM (
    'CUSTOMER',
    'STAFF',
    'ADMIN'
);

CREATE TYPE user_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'BANNED'
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,

    full_name VARCHAR(255),
    role user_role NOT NULL DEFAULT 'CUSTOMER',
    status user_status NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_name ON users(full_name);

-- table hotels
CREATE TYPE hotel_status AS ENUM ('ACTIVE', 'INACTIVE');

CREATE TABLE IF NOT EXISTS hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,

    status hotel_status NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- table hotel_staffs (xem users role STAFF anh làm việc ở đâu & quyền gì tại đó)
-- Mỗi nhân viên 1-n khách sạn
-- Mỗi khách sạn có thể có quyền khác nhau
-- sau này scale thêm role booking để trả tiền hoa hồng cho nhân viên
CREATE TYPE hotel_staff_role AS ENUM ('STAFF', 'MANAGER');

CREATE TABLE IF NOT EXISTS hotel_staffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hotel_id UUID NOT NULL,
    user_id UUID NOT NULL,

    role hotel_staff_role NOT NULL DEFAULT 'STAFF',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_hotel_staffs_hotel_id ON hotel_staffs(hotel_id); -- Tìm nhân viên theo khách sạn
CREATE INDEX idx_hotel_staffs_user_id ON hotel_staffs(user_id); -- Tìm khách sạn theo nhân viên

-- table rooms lưu thông tin phòng của khách sạn
CREATE TYPE room_status AS ENUM (
    'AVAILABLE',
    'MAINTENANCE'
);

CREATE TYPE bed_type AS ENUM (
    'SINGLE',
    'DOUBLE'
);

CREATE TABLE IF NOT EXISTS rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID NOT NULL,

    room_number VARCHAR(10) NOT NULL,    -- 101, 201
    floor INT,

    bed_type bed_type NOT NULL DEFAULT 'SINGLE',
    base_price NUMERIC(15,0) NOT NULL CHECK (base_price >= 0),

    status room_status DEFAULT 'AVAILABLE',
    description TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_rooms_hotel_id ON rooms (hotel_id); -- Tìm phòng theo khách sạn
CREATE INDEX idx_rooms_hotel_status ON rooms (hotel_id, status); -- Phòng trống theo khách sạn
CREATE INDEX idx_rooms_hotel_bed_type ON rooms (hotel_id, bed_type); -- Phòng theo loại giường
CREATE INDEX idx_rooms_hotel_price ON rooms (hotel_id, base_price); -- Phòng theo giá

-- table bookings lưu thông tin đặt phòng
CREATE TYPE booking_status AS ENUM (
    'PENDING', -- chờ xác nhận -- UPDATE ngay khi tạo booking
    'CONFIRMED', -- đã xác nhận -- UPDATE sau khi khách sạn duyệt
    'CHECKED_IN', -- đã nhận phòng -- UPDATE sau khi khách đến nhận phòng
    'CHECKED_OUT', -- đã trả phòng -- UPDATE sau khi khách trả phòng
    'CANCELLED', -- đã hủy -- UPDATE khách hoặc khách sạn hủy
    'NO_SHOW' -- khách không đến -- UPDATE sau ngày checkin mà khách không đến
);

CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hotel_id UUID NOT NULL,
    room_id UUID NOT NULL,

    guest_id UUID NOT NULL,        -- khách lưu trú
    user_id UUID NULL,             -- nếu booking do staff/customer book hộ, giữ để audit

    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,

    checkin_at TIMESTAMP WITH TIME ZONE,
    checkout_at TIMESTAMP WITH TIME ZONE,

    status booking_status NOT NULL DEFAULT 'PENDING',

    total_price NUMERIC(15,0) NOT NULL CHECK (total_price >= 0), -- VND,

    checkin_source VARCHAR(20), -- nguồn checkin: FRONT_DESK, MOBILE_APP, KIOSK

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_bookings_hotel_id ON bookings(hotel_id); -- Tìm booking theo khách sạn
CREATE INDEX idx_bookings_room_id ON bookings(room_id); -- Tìm booking theo phòng
CREATE INDEX idx_bookings_guest_id ON bookings(guest_id); -- Tìm booking theo khách hàng
CREATE INDEX idx_bookings_status ON bookings(status); -- Tìm booking theo trạng thái
CREATE INDEX idx_bookings_checkin_checkout ON bookings(checkin_date, checkout_date); -- Tìm booking theo ngày

-- table checkin_tokens
-- lưu token checkin & checkout
CREATE TYPE checkin_token_type AS ENUM ('CHECKIN', 'CHECKOUT');

CREATE TABLE IF NOT EXISTS checkin_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    booking_id UUID NOT NULL,

    token VARCHAR(255) NOT NULL UNIQUE,

    type checkin_token_type NOT NULL,

    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    used_at TIMESTAMP WITH TIME ZONE NULL,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX idx_checkin_tokens_token_active
ON checkin_tokens(token)
WHERE used_at IS NULL; -- Tìm token còn hiệu lực

CREATE UNIQUE INDEX uq_checkin_tokens_booking_type
ON checkin_tokens(booking_id, type); -- Đảm bảo không tạo trùng token checkin/checkout cho 1 booking

CREATE INDEX idx_checkin_tokens_expires_at
ON checkin_tokens(expires_at); -- Xoá token hết hạn định kỳ

-- table checkin_logs
-- lưu lịch sử checkin & checkout
CREATE TABLE IF NOT EXISTS checkin_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    booking_id UUID NOT NULL,

    action VARCHAR(20) NOT NULL,
    method VARCHAR(20) NOT NULL,

    performed_by UUID NULL, -- user_id của nhân viên nếu checkin/checkout bởi nhân viên // NULL nếu khách tự checkin/checkout
    source VARCHAR(50),     -- ứng dụng hoặc thiết bị thực hiện checkin/checkout (như "MOBILE_APP", "FRONT_DESK_KIOSK")

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_checkin_logs_booking ON checkin_logs(booking_id); -- Tìm log theo booking
CREATE INDEX idx_checkin_logs_booking_action ON checkin_logs(booking_id, action); -- Tìm log theo booking & action
CREATE INDEX idx_checkin_logs_created_at ON checkin_logs(created_at DESC); -- Tìm log theo thời gian tạo mới nhất

-- table payments lưu thông tin thanh toán
CREATE TYPE payment_method AS ENUM (
    'CREDIT_CARD',
    'CASH',
    'MOBILE_PAYMENT',
    'BANK_TRANSFER'
);
CREATE TYPE payment_status AS ENUM (
    'PENDING',
    'COMPLETED',
    'FAILED',
    'REFUNDED'
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    booking_id UUID NOT NULL,
    amount NUMERIC(12,2) NOT NULL,

    method payment_method NOT NULL,
    status payment_status NOT NULL DEFAULT 'PENDING',
    transaction_ref VARCHAR(100) UNIQUE, -- Mã giao dịch từ cổng thanh toán

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_payments_booking_id ON payments(booking_id); -- Tìm payment theo booking
CREATE INDEX idx_payments_status ON payments(status); -- Tìm payment theo trạng thái

-- table booking_daily_stats lưu thông tin thống kê đặt phòng hàng ngày cho mỗi khách sạn
CREATE TABLE IF NOT EXISTS booking_daily_stats (
    hotel_id UUID NOT NULL DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    total_bookings INT DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (hotel_id, date)
);

-- table system_events lưu thông tin sự kiện hệ thống để xử lý bất đồng bộ
CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    payload JSONB,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_system_events_processed ON system_events(processed);
CREATE INDEX idx_system_events_event_type ON system_events(event_type);

-- table refresh_tokens lưu thông tin refresh token cho user
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token VARCHAR(500) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- TODO: Thêm bảng reviews
-- TODO: Thêm bảng notifications