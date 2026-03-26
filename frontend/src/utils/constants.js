// User Roles
export const UserRole = {
  ADMIN: 'ADMIN',
  MANAGER: 'MANAGER',
  STAFF: 'STAFF',
  CUSTOMER: 'CUSTOMER',
};

// Booking Status
export const BookingStatus = {
  PENDING: 'PENDING',
  CONFIRMED: 'CONFIRMED',
  CHECKED_IN: 'CHECKED_IN',
  CHECKED_OUT: 'CHECKED_OUT',
  CANCELLED: 'CANCELLED',
};

// Room Status
export const RoomStatus = {
  AVAILABLE: 'AVAILABLE',
  BOOKED: 'BOOKED',
  MAINTENANCE: 'MAINTENANCE',
};

// Bed Types
export const BedType = {
  SINGLE: 'SINGLE',
  DOUBLE: 'DOUBLE',
};

// Status Display Config
export const STATUS_COLORS = {
  PENDING: '#E6A23C',
  CONFIRMED: '#409EFF',
  CHECKED_IN: '#67C26A',
  CHECKED_OUT: '#909399',
  CANCELLED: '#F56C6C',
  AVAILABLE: '#67C26A',
  BOOKED: '#E6A23C',
  MAINTENANCE: '#909399',
};

// Status Display Labels (i18n keys)
export const STATUS_LABELS = {
  PENDING: 'admin.booking.pending',
  CONFIRMED: 'admin.booking.confirmed',
  CHECKED_IN: 'admin.booking.checkedIn',
  CHECKED_OUT: 'admin.booking.checkedOut',
  CANCELLED: 'admin.booking.cancelled',
  AVAILABLE: 'admin.room.available',
  BOOKED: 'admin.room.booked',
  MAINTENANCE: 'admin.room.maintenance',
};
