from machine import Pin, SPI


class XPT2046:
    def __init__(self, spi, cs=None, irq=None, width=480, height=320):
        assert None not in [cs, irq], "cs, irq can't be None"
        self.spi = spi
        self.cs = cs
        self.irq = irq
        self.irq_cnt = 0
        self.ready = False
        self.width = width
        self.height = height
        self.cali_enable = False

        self.cs.init(Pin.OUT, value=1)
        # self.irq.init(Pin.IN, Pin.PULL_UP)

        # Dane kalibracyjne (odczytane z rogów panelu)
        self.x_min, self.x_max = 260, 3820
        self.y_min, self.y_max = 360, 3680

        self.irq.irq(trigger=Pin.IRQ_FALLING, handler=self.irq_handler)  # opada,, a  | Pin.IRQ_RISING narasta

    def calibrate(self, x_raw, y_raw):
        if self.cali_enable:
            if self.x_min > x_raw: 
                self.x_min = x_raw
            if self.x_max < x_raw: 
                self.x_max = x_raw
            if self.y_min > y_raw: 
                self.y_min = y_raw
            if self.y_max < y_raw: 
                self.y_max = y_raw
            
        x_screen = (x_raw - self.x_min) * self.width // (self.x_max - self.x_min)
        y_screen = (y_raw - self.y_min) * self.height // (self.y_max - self.y_min)
        return x_screen, y_screen
    
    def read_touch(self):
        # print(':18')
        self.cs.value(0)  # Aktywacja CS (niski stan)
        self.spi.write(bytearray([0x90]))  # Odczyt X
        x = self.spi.read(2)
        self.spi.write(bytearray([0xD0]))  # Odczyt Y
        y = self.spi.read(2)

        # self.spi.write(bytearray([0xA0]))  # Odczyt Z1
        # z1 = self.spi.read(2)
        # self.spi.write(bytearray([0xC0]))  # Odczyt Z2
        # z2 = spi.read(2)
        
        
        # spi.write(bytearray([0xB0]))  # Odczyt T1
        # t1 = spi.read(2)
        # spi.write(bytearray([0xF0]))  # Odczyt T2
        # t2 = spi.read(2)
        
        self.cs.value(1)  # Dezaktywacja CS

        x_raw = ((x[0] << 8) | x[1]) >> 3
        y_raw = ((y[0] << 8) | y[1]) >> 3
        # z_1 = ((z1[0] << 8) | z1[1])
        # z_2 = ((z2[0] << 8) | z2[1])
        # t_1 = ((t1[0] << 8) | t1[1])
        # t_2 = ((t2[0] << 8) | t2[1])
        # print(z_1, z_2, t_1, t_2)
        
        return self.calibrate(x_raw, y_raw)

    def irq_handler(self, pin):
        self.irq_cnt += 1
        self.ready = True
        # print('irq_handler:63', self.irq_cnt)

    def get_pos(self):
        # print(':30', self.irq_cnt, self.irq.value())
        x, y = -1, -1
        if not self.irq.value():  # Sprawdzenie, czy IRQ jest niskie
            x, y = self.read_touch()
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            print(f"X,Y: [{x}, {y}]  {self.x_min} {self.x_max} {self.y_min} {self.y_max}")
        self.ready = False
        return x, self.height - y

# end.