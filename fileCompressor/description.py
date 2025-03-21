"""
[Title/Звание]
Custom File Compressor

[Description/Обрисовка]

Конзолна помощна програма за компресиране и декомпресиране на файлове с помощта на множество алгоритми за компресиране
(RLE, Huffman и LZW). Ще поддържа както текстови, така и двоични файлове,
като предлага евентуално различни нива на компресиране и подробна статистика за процеса на компресиране.
Идеята е на прогрмата да бъден даден файл, тя да го компресира и да върне новия компресиран файл.
Той няма да бъде в четима форма, а двоичен файл.
След това на програмата може да бъде подаден компресиран файл и тя да върне оригиналния файл с оригиналния размер.
Ще работи с различни видове файлове - текстови, снимки и др.
Ще работи с 3 (може и да останат 2) техники/алгоритми за компресиране:
1. Run-Length Encoding (RLE)
2. Huffman Encoding
3. Lempel-Ziv-Welch (LZW)
Техниката за компресиране ще бъде ибрана на база подадения файл и съдържанието му.

[Functionalities/Надарености]
- Поддръжка на множество алгоритми за компресия
- Проследяване на напредъка по време на облаботването на файла
- Статистика и отчитане на процеса на компресиране
- Работа с файлове

[Milestones/Възлови точки]
1. Работа с файлове - извършване на основни операции
2. Създаване на интерфейс за конзолата
3. Имплементация на RLE, Huffman и евентуално LZW
4. Имплементация на проследяването на процеса и статистика
5. Тестване

[Estimate in man-hours/Времеоценка в човекочасове]
да е готов за 15-16.02

[Usage of technologies/Потребление на технологии]
- различни библиотеки в Python - struct,pathlib
"""