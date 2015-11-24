This is program for Huffman encoding and decoding.

Parameters of command line:
-c means encode
-u means decode
-f or --file means input file name
-o or --output means output file name

Example of usage:
(encoding)
$ ./huffman -c -f myfile.txt -o result.bin
(decoding)
$ huffman -u -f result.bin -o myfile_new.txt

Output of the program in the command line:
1st line contains size of input file
2nd line contains size of output file
3rd line contains size of supplementary data in the encoded file

This program was written by Roman Fedorov in October 2014