import sys
import struct

# --- Константы команд (Opcode) для Варианта 10 ---
CMD_LOAD = 50   # 0x32
CMD_READ = 33   # 0x21
CMD_WRITE = 16  # 0x10
CMD_SAR = 10    # 0x0A

def pack_command(cmd, args):
    """
    Упаковывает команду в байты согласно битовой спецификации Варианта 10.
    Возвращает: список байтов.
    """
    cmd = cmd.upper()
    if cmd == 'LOAD':
        # Синтаксис: LOAD <val>
        # Биты 0-5: Opcode (50)
        # Биты 6-26: Constant (21 бит)
        val = int(args[0])
        opcode = CMD_LOAD
        packed = (opcode & 0x3F) | ((val & 0x1FFFFF) << 6)
        return list(struct.pack("<I", packed)) # 4 байта, Little Endian
        
    elif cmd == 'READ':
        # Синтаксис: READ
        # Биты 0-5: Opcode (33)
        opcode = CMD_READ
        packed = (opcode & 0x3F)
        return list(struct.pack("<I", packed))
        
    elif cmd == 'WRITE':
        # Синтаксис: WRITE <offset>
        # Биты 0-5: Opcode (16)
        # Биты 6-17: Offset (12 бит)
        offset = int(args[0])
        opcode = CMD_WRITE
        packed = (opcode & 0x3F) | ((offset & 0xFFF) << 6)
        return list(struct.pack("<I", packed))
        
    elif cmd == 'SAR':
        # Синтаксис: SAR <offset>
        # Биты 0-5: Opcode (10)
        # Биты 6-17: Offset (12 бит)
        offset = int(args[0])
        opcode = CMD_SAR
        packed = (opcode & 0x3F) | ((offset & 0xFFF) << 6)
        return list(struct.pack("<I", packed))
        
    return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python assembler.py <input.asm> <output.bin> [--test]")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    is_test_mode = "--test" in sys.argv

    ir_log = []       # Промежуточное представление
    instructions = [] # Бинарный код

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 1. Parsing & Assembly
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            parts = line.split()
            cmd_name = parts[0]
            args = parts[1:]
            
            # Сохраняем IR
            ir_log.append({
                "cmd": cmd_name,
                "args": args
            })

            packed_bytes = pack_command(cmd_name, args)
            if packed_bytes:
                instructions.extend(packed_bytes)
            else:
                print(f"Error: Unknown command '{cmd_name}'")
                return

        # 2. Write Binary
        with open(output_file, 'wb') as f:
            f.write(bytearray(instructions))

        # 3. Test Mode Output (Style from screenshot)
        if is_test_mode:
            # Блок IR
            print("\n--- Промежуточное представление (IR) ---")
            for i, item in enumerate(ir_log):
                args_str = " ".join(item['args'])
                print(f"[{i:02}] {item['cmd']:<10} {args_str}")

            # Блок Hex Dump
            print("\n--- Сгенерированный байт-код (в байтовом формате) ---")
            hex_str = ""
            for i, byte_val in enumerate(instructions):
                hex_str += f"0x{byte_val:02X} "
                if (i + 1) % 12 == 0: # Перенос строки для красоты
                    hex_str += "\n"
            print(hex_str.strip())

            # Блок Detailed View
            print("\n--- Представление по инструкциям (4 байта на команду) ---")
            byte_idx = 0
            for i, item in enumerate(ir_log):
                chunk = instructions[byte_idx : byte_idx+4]
                byte_idx += 4
                bytes_display = " ".join(f"{b:02X}" for b in chunk)
                
                # Формируем строку аргументов для вывода
                arg_val = item['args'][0] if item['args'] else ""
                
                print(f"[{i:02}] {item['cmd']:<10} | Bytes: {bytes_display} | Аргумент: {arg_val}")

            print(f"\n[INFO] Сгенерировано команд: {len(ir_log)}")
            print(f"[INFO] Успешно ассемблировано. Размер: {len(instructions)} байт")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()