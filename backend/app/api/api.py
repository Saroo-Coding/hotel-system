from fastapi import APIRouter
from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.hotels import router as hotels_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.guests import router as guests_router
from app.api.v1.booking import router as booking_router
from app.api.v1.payments import router as payments_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["Auth"], prefix="/auth")
api_router.include_router(users_router, tags=["Users"], prefix="/users")
api_router.include_router(guests_router, tags=["Guests"], prefix=("/guests"))
api_router.include_router(hotels_router, tags=["Hotels"], prefix="/hotels")
api_router.include_router(rooms_router, tags=["Rooms"], prefix="/rooms")
api_router.include_router(booking_router, tags=["Bookings"], prefix="/bookings")
api_router.include_router(payments_router, tags=["Payments"], prefix="/payments")

# TODO: validate lại hết các schemas
# TODO: gửi email thông báo mật khẩu tạm thời
# TODO: thêm chức năng avatar
# TODO: Xóa BASE_PASSWORD sau khi hoàn thành chức năng gửi email
# TODO: Chuẩn hoá error response format
# TODO: Khi 1 guest booking thì hỏi guest đã từng booking chưa, nếu rồi thì lấy thông tin cũ, nếu chưa thì tạo mới guest sau đó tạo booking vs id guest mới tạo
# sau làm page room sẽ show status phòng theo ngày, và bấm detail sẽ show lịch sử booking của phòng đó, 
