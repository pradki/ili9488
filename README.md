### Wprowadzenie

#### Dlaczego ILI9488 i ESP32-S3?
Wybrałem wyświetlacz z kontrolerem ILI9488, ponieważ taki właśnie model posiadam. Zdecydowałem się na ESP32-S3, gdyż ma więcej pamięci RAM niż ESP32, co jest kluczowe przy pracy z wyświetlaczem. Cena obu modeli jest podobna, więc wybór był naturalny.

Próbowałem skorzystać z gotowych bibliotek, ale niestety żadna nie działała poprawnie. Nie twierdzę, że problem leżał po stronie bibliotek — możliwe, że przyczyną był sam wyświetlacz, który prawdopodobnie nie obsługuje kolorów w formacie RGB565 (16-bitowy), co wymaga dodatkowej weryfikacji. Być może problem tkwił również w nieodpowiedniej inicjalizacji wyświetlacza w dostępnych bibliotekach. Ostatecznie, po dokładnym przestudiowaniu dokumentacji, postanowiłem napisać własną bibliotekę.

### Założenia
Moim celem było stworzenie biblioteki:
- **Prostej**, o minimalistycznym kodzie,
- **Wydajnej**, o niskim zużyciu pamięci,
- **Wykorzystującej dostępne narzędzia MicroPythona**.

Jednym z ciekawszych rozwiązań, które wdrożyłem, jest użycie modułu `framebuf` do rysowania tekstów. Dzięki dodatkowym argumentom `scale_v` i `scale_h`, można łatwo skalować czcionki, uzyskując różne rozmiary. To podejście sprawia, że korzystanie z biblioteki jest proste i daje satysfakcjonujące rezultaty.

### Dlaczego nie LVGL?
LVGL, choć jest zaawansowaną biblioteką, obecnie nie działa z moją konfiguracją. Co więcej, wymaga kompilacji, co utrudnia jej zastosowanie w prostszych projektach.

### Wykorzystane narzędzia i sprzęt

#### Wersja MicroPythona
- Użyto wersji **1.23**, ponieważ wersja **1.24** miała problemy z obsługą kart SD.

#### Sprzęt
1. **ESP32-S3** 10PCS-N16R8 – model z SPIRAM, zakupiony na AliExpress:  
   [Link do aukcji](https://pl.aliexpress.com/item/1005007520936918.html)
2. **Wyświetlacz 3.5" z dotykiem** – model zakupiony na AliExpress:  
   [Link do aukcji](https://pl.aliexpress.com/item/1005004995246210.html)

#### Informacje techniczne o połączeniach

Na wyświetlaczu znajduje się zworka J1, którą można zapiąć, jeśli zasilamy wyświetlacz napięciem 3,3V. W moim przypadku wyświetlacz działał poprawnie zarówno ze zworką, jak i bez niej.

| ESP32-S3  | Display 3.5" |
| ------------- | ------------- |
|  8 | T_IRQ |
|  42 | T_DO  |
|  41 | T_DIN |
|  2  | T_CS  |
|  6  | T_CLK |
|  12 | SDO<MISO> |
|  3.3V | LED  |
|  14 | SCK |
|  13 | SOI<MOSI> |
|  16 | DC/RS |
|  17 | RESET |
|  5  | CS  |
| GND | GND |
| 3.3V | VCC |

Wyświetlacz został podłączony do magistrali **HSPI** (id=1), zgodnie z oficjalną dokumentacją MicroPythona:
[Hardware SPI bus](https://docs.micropython.org/en/latest/esp32/quickref.html#software-spi-bus)

| Magistrala SPI | HSPI (id=1) |
| -------------- | ----------- |
| sck            | 14          |
| mosi           | 13          |
| miso           | 12          |

#### Obsługa dotyku
Z powodu ograniczeń sprzętowych ESP32-S3 (brak wyprowadzeń pinów dla VSPI: 18, 19, 23, które są używane przez SPIRAM — wymaga weryfikacji), dotyk nie został podłączony do magistrali VSPI.

### Problemy i rozwiązania
1. **Obsługa kolorów**
   - Próbowano użyć formatu RGB565 (16-bitowego), ale wyświetlacz go nie obsługuje. Aktualnie kolory są przesyłane w formacie 18-bitowym.

2. **Inicjalizacja wyświetlacza**
   - Poprawna inicjalizacja została opracowana na podstawie dokumentacji technicznej ILI9488. To kluczowy element, który pozwolił na poprawne działanie wyświetlacza.

3. **Wydajność**
   - Dzięki zastosowaniu narzędzi MicroPythona, takich jak `framebuf`, udało się zachować niskie zużycie pamięci i zapewnić zadowalającą szybkość działania.

### Przykłady użycia
(To be added)

### Podsumowanie
Biblioteka dla ILI9488 została stworzona z myślą o prostocie i wydajności, korzystając wyłącznie z dostępnych narzędzi MicroPythona. Choć jest minimalistyczna, spełnia swoje zadanie i pozwala na łatwą obsługę wyświetlacza w projektach opartych na ESP32-S3. 
