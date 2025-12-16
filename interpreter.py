import sys
import struct
import csv

MEM_SIZE = 1024

class VM:
    def __init__(self):
        self.memory = [0] * MEM_SIZE
        self.stack = []
        self.log_lines = []

    def log(self, pc, cmd, operand, stack_state):
        # Форматирование лога как на скриншоте
        stack_str = str(stack_state).replace(" ", "") # Убираем лишние пробелы
        op_str = f"{operand}" if operand is not None else ""
        print(f"[{pc:03}] Выполняется: {cmd:<10} | B (операнд): {op_str:<5} | Стек: {stack_str}")

    def run(self, binary_path, dump_path, dump_range):
        with open(binary_path, 'rb') as f:
            code = f.read()
            
        print(f"[INFO] Запуск программы. Всего инструкций: {len(code)//4}")
        print(f"[INFO] Начальное состояние стека: {self.stack}")

        pc = 0
        instr_idx = 0
        
        while pc < len(code):
            if pc + 4 > len(code): break
            
            # Читаем 4 байта
            instruction = struct.unpack("<I", code[pc:pc+4])[0]
            opcode = instruction & 0x3F
            
            # Разбор команд для выполнения и логирования
            if opcode == 50: # LOAD
                val = (instruction >> 6) & 0x1FFFFF
                self.log(instr_idx, "LOAD", val, self.stack)
                self.stack.append(val)
                
            elif opcode == 33: # READ
                self.log(instr_idx, "READ", None, self.stack)
                if self.stack:
                    addr = self.stack.pop()
                    res = self.memory[addr] if 0 <= addr < MEM_SIZE else 0
                    self.stack.append(res)
                    
            elif opcode == 16: # WRITE
                offset = (instruction >> 6) & 0xFFF
                self.log(instr_idx, "WRITE", offset, self.stack)
                if len(self.stack) >= 2:
                    addr_base = self.stack.pop()
                    value = self.stack.pop()
                    target = addr_base + offset
                    if 0 <= target < MEM_SIZE:
                        self.memory[target] = value
                        
            elif opcode == 10: # SAR
                offset = (instruction >> 6) & 0xFFF
                self.log(instr_idx, "SAR", offset, self.stack)
                if self.stack:
                    addr_base = self.stack.pop()
                    shift_addr = addr_base + offset
                    
                    if 0 <= shift_addr < MEM_SIZE and 0 <= addr_base < MEM_SIZE:
                        shift_amt = self.memory[shift_addr]
                        val = self.memory[addr_base]
                        res = val >> shift_amt
                        self.memory[addr_base] = res

            pc += 4
            instr_idx += 1

        print(f"\n--- Выполнение программы завершено на IP-{instr_idx} ---")
        print(f"Финальное состояние стека: {self.stack}")
        
        # Предпросмотр памяти (первые 16 ячеек, как на скрине)
        mem_preview = str(self.memory[:16]).replace(" ", "")
        print(f"Память (первые 16 ячеек): {mem_preview}")

        # Сохранение в CSV
        start, end = map(int, dump_range.split(':'))
        try:
            with open(dump_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Address", "Value"])
                for i in range(start, min(end + 1, MEM_SIZE)):
                    writer.writerow([i, self.memory[i]])
            print(f"\n[INFO] Дамп памяти сохранен в файл: {dump_path}")
        except Exception as e:
            print(f"[ERROR] Не удалось сохранить дамп: {e}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python interpreter.py <binary.bin> <dump.csv> <start:end>")
        return
    vm = VM()
    vm.run(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()