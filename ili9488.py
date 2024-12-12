
__version__ = "0.0.0"

from machine import Pin
import time
from framebuf import FrameBuffer, MONO_VLSB

# import framebuf
# import random

# Stałe dla komend ILI9488
# CMD_SWRESET = 0x01
# CMD_SLPOUT = 0x11
# CMD_DISPON = 0x29
# CMD_CASET = 0x2A
# CMD_PASET = 0x2B
# CMD_RAMWR = 0x2C
# CMD_COLMOD = 0x3A

# 5.2.30. Memory Access Control (36h)
MAC36H_MY = const(0)  # D7 MY Row Address Order
MAC36H_MX = const(0)  # D6 MX Column Address Order
MAC36H_MV = const(1)  # D5 MV Row/Column Exchange
MAC36H_ML = const(0)  # D4 ML Vertical Refresh Order LCD vertical refresh direction control.
MAC36H_BRG = const(0)  # RGB-BGR Order
MAC36H_MH = const(0)  # Horizontal Refresh Order


class ILI9488:
    def __init__(self, spi, cs=None, dc=None, rst=None):
        assert None not in [cs, dc, rst], "cs, dc, rst can't be None"
        self.spi = spi
        self.cs = cs
        self.dc = dc  # dc (data: 1; command: 0)
        self.rst = rst

        self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=1)  # dc (data: 1; command: 0)
        self.rst.init(Pin.OUT, value=1)

        self.mac36h_my = MAC36H_MY
        self.mac36h_mx = MAC36H_MX
        self.mac36h_mv = MAC36H_MV
        self.mac36h_ml = MAC36H_ML
        self.mac36h_brg = MAC36H_BRG
        self.mac36h_mh = MAC36H_MH
        
        self.reset()
        # self.init_display()
        self.init_display()

    def reset(self):  # 13.4. Reset Timing
        self.rst.value(0)
        time.sleep_ms(120)
        self.rst.value(1)
        time.sleep_ms(120)

    def write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)  # dc (data: 1; command: 0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)  # dc (data: 1; command: 0)
        self.spi.write(data)
        self.cs.value(1)

    def read_data(self, cmd, num_bytes):
        self.cs.value(0)
        self.dc.value(0)  # dc (data: 1; command: 0)
        self.spi.write(bytearray([cmd]))  # Wysłanie komendy odczytu
        self.dc.value(1)  # dc (data: 1; command: 0)
        
        # Odczyt danych z MISO
        result = self.spi.read(num_bytes)
        
        self.cs.value(1)
        return result

    def init_display(self):
        # nie jest oficjalnie udokumentowana w standardowych specyfikacjach sterownika ILI9488
        self.write_cmd(0x7F)
        self.write_data(bytearray([0xA9, 0x51, 0x2C, 0x82]))
        
        
        self.write_cmd(0xC0)  # 5.3.12. Power Control 1 (C0h)
        # Halt (Vreg1out = Hiz  5’h11 1.25 x 3.70 = 4.6250
        # Halt (Vreg2out = Hiz)   -1.25 x 3.60 = -4.5000
        self.write_data(bytearray([0x11, 0x09]))
        
        self.write_cmd(0xC1)  # 5.3.13. Power Control 2 (C1h)
        self.write_data(bytearray([0x41]))
        
        self.write_cmd(0xC5)  # 5.3.17. VCOM Control (C5h)
        # nVM: When the NV memory is programmed, the nVM will be set to 1 automatically.
            # 0: NV memory is not programmed
        self.write_data(bytearray([0x00, 0x0A, 0x80]))
        
        self.write_cmd(0xB1)  # 5.3.2. Frame Rate Control (In Normal Mode/Full Colors) (B1h)
        self.write_data(bytearray([0xB0, 0x11]))
        
        self.write_cmd(0xB4)  # 5.3.5. Display Inversion Control (B4h)
        self.write_data(bytearray([0x02]))  # 2 dot inversion
        
        self.write_cmd(0xB6)  # 5.3.7. Display Function Control (B6h)
        self.write_data(bytearray([0x02, 0x42]))
        
        self.write_cmd(0xB7)  # 5.3.8. Entry Mode Set (B7h)
        # GON/DTE: Set the output level of the gate driver G1 ~ G480 as follows:
            # Normal display
        # EPF [1:0]: Set the data format when 16bbp (R, G, B) to 18 bbp (R, G, B) is stored in the internal GRAM
        self.write_data(bytearray([0xC6]))
        
        self.write_cmd(0xBE)  # 5.3.11. HS Lanes Control (BEh)
        self.write_data(bytearray([0x00, 0x04]))
        
        self.write_cmd(0xE9)  # 5.3.37. Set Image Function (E9h)
        self.write_data(bytearray([0x00]))  # DB_EN: Enable 24-bits Data Bus; users can use DB23~DB0 as 24-bits data input.
        
        self.mem_access_ctrl()  # 5.2.30. Memory Access Control (36h)
        # self.write_cmd(0x36)  # 5.2.30. Memory Access Control (36h)
        # D7 MY Row Address Order
        # D6 MX Column Address Order
        # D5 MV Row/Column Exchange
        # D4 ML Vertical Refresh Order    LCD vertical refresh direction control.
        # D3 BGR RGB-BGR Order   Color selector switch control    (0 = RGB color filter panel, 1 = BGR color filter panel)
        # D2 MH Horizontal Refresh ORDER LCD horizontal refreshing direction control.
        # D1-D0 Reserved
        # my = self.mac36h_my
        # mx = self.mac36h_mx
        # mv = self.mac36h_mv
        # ml = self.mac36h_ml
        # brg = self.mac36h_brg
        # mh = self.mac36h_mh
        
        # self.write_data(bytearray([(1<<3)|(0<<6)|(0<<7)]))  # //BGR==1,MY==0,MX==0,MV==0
        # self.write_data(bytearray([(1<<3)|(0<<7)|(1<<6)|(1<<5)]))  # //BGR==1,MY==1,MX==0,MV==1
        # self.write_data(bytearray([(1<<3)|(1<<6)|(0<<7)])) 
        # self.write_data(bytearray([(1<<3)|(1<<5)|(0<<7)]))
        # self.write_data(bytearray([self.reg36]))
        
        self.write_cmd(0x3A)  # 5.2.34. Interface Pixel Format (3Ah)
        # 0x55 16 bits/pixel  TODO dlaczego nie działa?
        # 0x66 18 bits/pixel
        # 0x77 24 bits/pixel
        self.write_data(bytearray([0x66]))
        # self.write_data(bytearray([self.regxx]))
        
        self.write_cmd(0xE0)  # 5.3.33. PGAMCTRL (Positive Gamma Control) (E0h)
        self.write_data(bytearray([0x00, 0x07, 0x10, 0x09, 0x17, 0x0B, 0x41, 0x89, 0x4B, 0x0A, 0x0C, 0x0E, 0x18, 0x1B, 0x0F]))
        
        self.write_cmd(0xE1)  # 5.3.34. NGAMCTRL (Negative Gamma Control) (E1h)
        self.write_data(bytearray([0x00, 0x17, 0x1A, 0x04, 0x0E, 0x06, 0x2F, 0x45, 0x43, 0x02, 0x0A, 0x09, 0x32, 0x36, 0x0F]))
        
        self.write_cmd(0x11)  # 5.2.13. Sleep OUT (11h)
        time.sleep_ms(150)
        self.write_cmd(0x29)  # 5.2.21. Display ON (29h)

    def xxxxinit_display(self):
        # Reset and display off
        self.write_cmd(0x01)  # Software reset
        time.sleep_ms(150)

        self.write_cmd(0x28)  # Display off
        time.sleep_ms(100)

        # Sleep out
        self.write_cmd(0x11)
        time.sleep_ms(150)

        # Column Address Set (CAS)
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, 0x00, 0x01, 0x3F]))  # 0x01, 0x3F (480 columns)

        # Page Address Set (PAS)
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, 0x00, 0x01, 0xFF]))  # 0x01, 0xFF (320 rows)

        # Memory Access Control
        self.write_cmd(0x36)
        self.write_data(bytearray([0x48]))  # Set to normal (portrait) mode

        # Pixel Format
        self.write_cmd(0x3A)
        self.write_data(bytearray([0x55]))  # 16-bit color depth

        # Display on
        self.write_cmd(0x29)
        time.sleep_ms(100)

    def fill_screen(self, color, width=480, height=320, pix_format=0x66):
        self.draw_rectangle(0, 0, width, height, color, pix_format=pix_format)

    def read_display_id_info(self):  # Read Display Identification Information (04h)
        return self.read_data(0x04, 4)

    def draw_rectangle(self, x, y, width, height, color, pix_format=0x66):
        # color 18-bitowy (0xRRGGBB -> RR: 6-bit, GG: 6-bit, BB: 6-bit)
        if pix_format == 0x55:  # 16 bits / pixel
            # high_byte, low_byte
            color_data = bytearray([(color >> 8) & 0xFF, color & 0xFF])
        else:  # 0x66 - 18 bits / pixel
            red = (color >> 16) & 0xFC  # 6-bit Red
            green = (color >> 8) & 0xFC  # 6-bit Green
            blue = color & 0xFC  # 6-bit Blue
            # Składanie kolorów w bajty dla transferu 18-bitowego (3 bajty)
            color_data = bytearray([red, green, blue])

        # Ustawienie zakresu kolumn (x)
        self.write_cmd(0x2A)  # CASET (Column Address Set)
        self.write_data(bytearray([
            # high_byte, low_byte
            (x >> 8) & 0xFF, x & 0xFF, 
            ((x + width - 1) >> 8) & 0xFF, (x + width - 1) & 0xFF
        ]))

        # Ustawienie zakresu wierszy (y)
        self.write_cmd(0x2B)  # PASET (Page Address Set)
        self.write_data(bytearray([
            # high_byte, low_byte
            (y >> 8) & 0xFF, y & 0xFF,
            ((y + height - 1) >> 8) & 0xFF, (y + height - 1) & 0xFF
        ]))

        # Rozpoczęcie zapisu pikseli do pamięci wyświetlacza
        self.write_cmd(0x2C)  # RAMWR (Memory Write)

        # Wypełnienie prostokąta kolorem
        for _ in range(width * height):
            self.write_data(color_data)

    def draw_pixel(self, x, y, color):
        self.write_cmd(0x2A)  # CASET (Column Address Set)
        self.write_data(bytearray([
            # high_byte, low_byte
            (x >> 8) & 0xFF, x & 0xFF, 
            (x >> 8) & 0xFF, x & 0xFF
        ]))

        self.write_cmd(0x2B)  # PASET (Page Address Set)
        self.write_data(bytearray([
            # high_byte, low_byte
            (y >> 8) & 0xFF, y & 0xFF,
            (y >> 8) & 0xFF, y & 0xFF
        ]))

        self.write_cmd(0x2C)  # RAMWR (Memory Write)
        self.write_data(bytearray([(color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF]))

    def draw_framebuf(self, buf, x, y, width, height):
        # color 18-bitowy (0xRRGGBB -> RR: 6-bit, GG: 6-bit, BB: 6-bit)
        # if pix_format == 0x55:  # 16 bits / pixel
            # # high_byte, low_byte
            # color_data = bytearray([(color >> 8) & 0xFF, color & 0xFF])
        # else:  # 0x66 - 16 bits / pixel
            # red = (color >> 16) & 0xFC  # 6-bit Red
            # green = (color >> 8) & 0xFC  # 6-bit Green
            # blue = color & 0xFC  # 6-bit Blue
            # # Składanie kolorów w bajty dla transferu 18-bitowego (3 bajty)
            # color_data = bytearray([red, green, blue])

        self.write_cmd(0x2A)  # CASET (Column Address Set)
        self.write_data(bytearray([
            # high_byte, low_byte
            (x >> 8) & 0xFF, x & 0xFF, 
            ((x + width - 1) >> 8) & 0xFF, (x + width - 1) & 0xFF
        ]))

        # Ustawienie zakresu wierszy (y)
        self.write_cmd(0x2B)  # PASET (Page Address Set)
        self.write_data(bytearray([
            # high_byte, low_byte
            (y >> 8) & 0xFF, y & 0xFF,
            ((y + height - 1) >> 8) & 0xFF, (y + height - 1) & 0xFF
        ]))
        self.write_cmd(0x2C)  # RAMWR (Memory Write)
        self.write_data(buf)

    def mem_access_ctrl(self, my=None, mx=None, mv=None, ml=None, brg=None, mh=None):
        if my is not None:
            self.mac36h_my = my
        else:
            my = self.mac36h_my
        if mx is not None:
            self.mac36h_mx = mx
        else:
            mx = self.mac36h_mx
        if mv is not None:
            self.mac36h_mv = mv
        else:
            mv = self.mac36h_mv
        if ml is not None:
            self.mac36h_ml = ml
        else:
            ml = self.mac36h_ml
        if brg is not None:
            self.mac36h_brg = brg
        else:
            brg = self.mac36h_brg
        if mh is not None:
            self.mac36h_mh = mh
        else:
            mh = self.mac36h_mh
        self.write_cmd(0x36)
        self.write_data(bytearray([(my<<7)|(mx<<6)|(mv<<5)|(ml<<4)|(brg<<3)|(mh<<2)]))
        # todo    
        # self.write_cmd(0x11)  # 5.2.13. Sleep OUT (11h)
        # time.sleep_ms(150)
        # self.write_cmd(0x29)  # 5.2.21. Display ON (29h)

    def text(self, text, x, y, color, bgcolor, scale_v=1, scale_h=1):
        buffs = []
        for char in text:
            buffs.append(self.fb2rgb_char(char, color, bgcolor, scale_v, scale_h))
        r = bytearray()
        for row in range(8*scale_h):
            for c in range(len(text)):
                r += bytes(buffs[c][row*8*scale_v*3:row*8*scale_v*3+(8*scale_v*3)])
        self.draw_framebuf(r, x, y, len(text)*8*scale_v, 8*scale_h)
        return r

    def fb2rgb_char(self, char, color, bgcolor, scale_v, scale_h):
        # chrnbr = len(text)
        # self.mac36h_my = MAC36H_MY
        # self.mac36h_mx = MAC36H_MX
        # self.mac36h_mv = MAC36H_MV
        # self.mac36h_ml = MAC36H_ML
        # self.mac36h_brg = MAC36H_BRG
        # self.mac36h_mh = MAC36H_MH
        h = 8
        buff = bytearray(h)  # 8bit/B
        fb = FrameBuffer(buff, 8, h, MONO_VLSB)
        fb.text(char, 0, 0, 1)
        r = bytearray()
        # for chrno in range(chrnbr):
        for col in range(8):
            for sh in range(scale_h):
                for row in range(h):    
                    for sv in range(scale_v):
                        if self.mac36h_my == 0 and self.mac36h_mx == 0:
                            b = (buff[row] >> (7-col)) & 0x01
                        elif self.mac36h_my == 0 and self.mac36h_mx == 1:
                            b = (buff[(row)] >> col) & 0x01
                        elif self.mac36h_my == 0 and self.mac36h_mx == 0:
                            b = (buff[row] >> (7-col)) & 0x01
                        else:
                            b = (buff[row] >> (7-col)) & 0x01
                        if b == 1:
                            r.append(0x00)
                            r.append(0xFF)
                            r.append(0xFF)
                            #print('#', end='')
                        else:
                            #print('.', end='')
                            r.append(0x00)
                            r.append(0x00)
                            r.append(0x00)
                #print(' ')
        #print('')
        return r

# end.