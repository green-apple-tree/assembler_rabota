#!/bin/bash
# 1. Ассемблирование
python3 assembler.py test_task.asm output.bin --log log.json

# 2. Интерпретация (дамп памяти ячеек 10-30)
python3 interpreter.py output.bin result.json 10:30

# 3. Показать результат
cat result.json