# FT6206 I2C address
FT6206_I2C_ADDR = const(0x38)

# Working mode register map
# Refer to https://github.com/hlf20010508/micropython-ili9341-ft6206/blob/master/FT6206.pdf
# Application Note for FT6x06 CTPM, Page 8
# Main Information
DEV_MODE = const(0x00)
GEST_ID = const(0x01)
TD_STATUS = const(0x02)
P1_XH = const(0x03)
P1_XL = const(0x04)
P1_YH = const(0x05)
P1_YL = const(0x06)
P1_WEIGHT = const(0x07)
P1_MISC = const(0x08)
P2_XH = const(0x09)
P2_XL = const(0x0A)
P2_YH = const(0x0B)
P2_YL = const(0x0C)
P2_WEIGHT = const(0x0D)
P2_MISC = const(0x0E)
# Pro Information
TH_GROUP = const(0x80)
TH_DIFF = const(0x85)
CTRL = const(0x86)
TIME_ENTER_MONITOR = const(0x87)
PERIOD_ACTIVE = const(0x88)
PERIOD_MONITOR = const(0x89)
RADIAN_VALUE = const(0x91)
OFFSET_LEFT_RIGHT = const(0x92)
OFFSET_UP_DOWN = const(0x93)
DISTANCE_LEFT_RIGHT = const(0x94)
DISTANCE_UP_DOWN = const(0x95)
DISTANCE_ZOOM = const(0x96)
LIB_VER_H = const(0xA1)
LIB_VER_L = const(0xA2)
CIPHER = const(0xA3)
G_MODE = const(0xA4)
PWR_MODE = const(0xA5)
FIRMID = const(0xA6)
FOCALTECH_ID = const(0xA8)
RELEASE_CODE_ID = const(0xAF)
STATE = const(0xBC)

ROTATE = [0, 90, 180, 270]

class Touch:
    def __init__(self, i2c, display=None):
        """
        Initialize

        :param i2c -> machine.SoftI2C: I2C object
        :param display -> ili9341.Display:  Display object
        """
        self.i2c = i2c
        self.display = display
        self.rotation = self.display.rotation_num
        self.width = self.display.width
        self.height = self.display.height

    def write_cmd(self, name, value):
        """
        Modify value in device

        :param start -> Const(Int): map name
        :param value -> Bytes: map value

        Example:
        touch.write_cmd(G_MODE, b"\x00")
        """
        self.i2c.writeto_mem(FT6206_I2C_ADDR, name, value)

    @property
    def data(self):
        """
        Return device data from 0x00 to 0xBC (All data)

        :Return: Bytes
        """
        return self.i2c.readfrom_mem(FT6206_I2C_ADDR, 0x00, 0xBD)
    
    @property
    def touched(self):
        """
        Return whether two points are touched

        :Return: Tuple(Boolean, Boolean)
        """
        data = self.data

        xh1 = data[P1_XH]
        xh2 = data[P2_XH]

        flag1 = False
        flag2 = False

        mask = 0xC0

        if (xh1 & mask) >> 6 != 0x03:
            flag1 = True
        if (xh2 & mask) >> 6 != 0x03:
            flag2 = True
        
        return (flag1, flag2)
    
    @property
    def touching(self):
        """
        If device is been touching
        return 1 or 2
        otherwise return 0

        :Return: Int
        """
        return self.data[TD_STATUS]

    def rotate(self, x, y):
        if self.rotation == 0:
            point = (x, y)
        if self.rotation == 90:
            point = (self.height - y, x)
        if self.rotation == 180:
            point = (self.width - x, self.height - y)
        if self.rotation == 270:
            point = (y, self.width - x)
        return point

    @property
    def position(self):
        """
        Return touched position
        If touched, return a tuple with position, otherwise False

        :Return: List[Tuple(Int, Int) | Boolean, Tuple(Int, Int) | Boolean]
        """
        number = self.touching

        data = self.data

        mask = 0x0F

        points = []

        if number > 0:
            xh1 = data[P1_XH]
            xl1 = data[P1_XL]
            yh1 = data[P1_YH]
            yl1 = data[P1_YL]

            x1 = (xh1 & mask) << 8 | xl1
            y1 = (yh1 & mask) << 8 | yl1

            points.append(self.rotate(x1, y1))
        
        if number > 1:
            xh2 = data[P2_XH]
            xl2 = data[P2_XL]
            yh2 = data[P2_YH]
            yl2 = data[P2_YL]

            x2 = (xh2 & mask) << 8 | xl2
            y2 = (yh2 & mask) << 8 | yl2

            points.append(self.rotate(x2, y2))

        return points
