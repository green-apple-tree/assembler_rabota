import struct
import assembler
import interpreter
import os
import sys

class TestCase:
    def __init__(self):
        self.logs = []

    def log(self, msg, status="INFO"):
        # Форматированный вывод
        if status == "PASS":
            print(f"\033[92m[PASS]\033[0m {msg}")
        elif status == "FAIL":
            print(f"\033[91m[FAIL]\033[0m {msg}")
        else:
            print(f"[{status}] {msg}")
        self.logs.append(f"[{status}] {msg}")

    def run(self):
        print("Running Test Suite...")
        try:
            self.test_assembler()
            self.test_interpreter()
            return self.logs
        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}", "FAIL")
            return self.logs

    def test_assembler(self):
        print("\n--- 1. Testing Assembler (Bitwise Check) ---")
        # Данные из PDF (Стр. 43-44, Вариант 10)
        
        # Тест 1: LOAD (Opcode 50). A=50, B=383.
        # Ожидается: 0xF2, 0x5F, 0x00, 0x00
        self.check_asm("LOAD 383", b'\xF2\x5F\x00\x00')

        # Тест 2: READ (Opcode 33). A=33.
        # Ожидается: 0x21, 0x00, 0x00, 0x00
        self.check_asm("READ", b'\x21\x00\x00\x00')

        # Тест 3: WRITE (Opcode 16). A=16, B=13 (Offset).
        # Ожидается: 0x50, 0x03, 0x00, 0x00
        self.check_asm("WRITE 13", b'\x50\x03\x00\x00')

        # Тест 4: SAR (Opcode 10). A=10, B=962 (Offset).
        # Ожидается: 0x8A, 0xF0, 0x00, 0x00
        self.check_asm("SAR 962", b'\x8A\xF0\x00\x00')

    def check_asm(self, line, expected):
        res = bytes(assembler.parse_line(line))
        if res == expected:
            self.log(f"Asm '{line}' -> {res.hex().upper()} : Matches PDF", "PASS")
        else:
            self.log(f"Asm '{line}' -> Expected {expected.hex().upper()}, Got {res.hex().upper()}", "FAIL")

    def test_interpreter(self):
        print("\n--- 2. Testing Interpreter (Logic Check) ---")
        vm = interpreter.VM()
        
        # Тест логики SAR (Сдвиг значения)
        # Задача: сдвинуть число 100 вправо на 2 бита (100 >> 2 = 25).
        # Код: 
        # LOAD 100, LOAD 10, WRITE 0  (Записали 100 в адрес 10)
        # LOAD 2,   LOAD 12, WRITE 0  (Записали 2 в адрес 12. Смещение=2, значит 10+2=12)
        # LOAD 10, SAR 2              (Сдвигаем Mem[10] на величину из Mem[10+2])
        
        ops = [
            "LOAD 100", "LOAD 10", "WRITE 0",
            "LOAD 2",   "LOAD 12", "WRITE 0",
            "LOAD 10", "SAR 2"
        ]
        
        binary = []
        for line in ops:
            binary.extend(assembler.parse_line(line))
            
        with open("test_temp.bin", "wb") as f:
            f.write(bytearray(binary))
            
        # Запуск VM
        vm.run("test_temp.bin", "test_res.json", "0:20")
        
        # Проверка
        val = vm.memory[10]
        if val == 25:
            self.log(f"SAR Logic: 100 >> 2 = 25", "PASS")
        else:
            self.log(f"SAR Logic: Expected 25, got {val}", "FAIL")
            
        # Уборка
        if os.path.exists("test_temp.bin"): os.remove("test_temp.bin")
        if os.path.exists("test_res.json"): os.remove("test_res.json")

if __name__ == "__main__":
    tester = TestCase()
    tester.run()
    # Чтобы консоль не закрывалась мгновенно на Windows
    input("\nPress Enter to exit...")