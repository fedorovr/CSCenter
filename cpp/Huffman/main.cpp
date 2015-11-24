#include <iostream>
#include <string>

#include "huffman.hpp"

using namespace std;

int main(int argc, char ** argv) {
	if (argc == 6) {
		if ((argv[2] != (string)"-f") && (argv[2] != (string)"--file")) {
			cerr << "Incorrect 2nd parameter: " << argv[2];
			return 2;
		}
		if ((argv[4] != (string)"-o") && (argv[4] != (string)"--output")) {
			cerr << "Incorrect 4th parameter: " << argv[4];
			return 4;
		}
		const string INPUT = argv[3];
		const string OUTPUT = argv[5];
		if (argv[1] == (string) "-c") {
			encode(INPUT, OUTPUT);
		}
		else if (argv[1] == (string) "-u") {
			decode(INPUT, OUTPUT);
		}
		else {
			cerr << "Incorrect 1st parameter: " << argv[1];
			return 1;
		}
	}
	else {
		cerr << "Incorrect count of input parameters: " << argc;
		return 6;
	}
	return 0;
}
