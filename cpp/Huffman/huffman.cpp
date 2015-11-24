#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <cstdint> 

using namespace std;

struct statElem {
	uint32_t count;
	uint8_t letter;
};

struct queueElem {
	uint32_t count = 0;
	uint8_t letter = 0;
	queueElem * left = NULL;
	queueElem * right = NULL;
};

struct binaryHeap {
	queueElem * queue[257];
	int currentQueueSize;

	binaryHeap(uint32_t * data) {
		currentQueueSize = 0;
		queue[currentQueueSize] = 0;
		for (int i = 0; i < 256; i++) {
			if (data[i]) {
				queueElem * tmp = new queueElem;
				tmp->letter = i;
				tmp->count = data[i];
				queue[++currentQueueSize] = tmp;
				int j = currentQueueSize;
				while ((j > 1) && (queue[j / 2]->count > queue[j]->count)) {
					queueElem * tmp2 = queue[j];
					queue[j] = queue[j / 2];
					queue[j / 2] = tmp2;
					j = j / 2;
				}
			}
		}
		for (int i = currentQueueSize + 1; i < 257; i++) {
			queue[i] = 0;
		}
	}

	queueElem * getMin() {
		queueElem * minElem;
		minElem = queue[1];
		queue[1] = queue[currentQueueSize--];
		int j = 1;
		while (2 * j <= currentQueueSize) {
			int min = 2 * j;
			if (2 * j + 1 <= currentQueueSize) {
				if (queue[2 * j + 1]->count < queue[min]->count) {
					min = 2 * j + 1;
				}
			}
			if (queue[j]->count > queue[min]->count) {
				queueElem * t = queue[j];
				queue[j] = queue[min];
				queue[min] = t;
				j = min;
			}
			else {
				break;
			}
		}
		return minElem;
	}

	void merge2smallestElements() {
		queueElem * a = getMin();
		queueElem * b = getMin();
		queueElem * c = new queueElem;
		c->count = a->count + b->count;
		c->letter = '\0';
		c->left = a;
		c->right = b;
		queue[++currentQueueSize] = c;
		int j = currentQueueSize;
		while ((j > 1) && (queue[j / 2]->count > queue[j]->count)) {
			queueElem * tmp2 = queue[j];
			queue[j] = queue[j / 2];
			queue[j / 2] = tmp2;
			j = j / 2;
		}
	}

	queueElem * buildTree() {
		while (currentQueueSize > 1) {
			merge2smallestElements();
		}
		return queue[1];
	}

	void buildCodesArray(queueElem * currentElement, string * codesArray, string currentCode) {
		if (currentElement->left) {
			buildCodesArray(currentElement->left, codesArray, currentCode + "0");
			buildCodesArray(currentElement->right, codesArray, currentCode + "1");
		}
		else {
			if (currentCode == "") currentCode = "0";					// case of 1 symbol in all text
			codesArray[currentElement->letter] = currentCode;
		}
	}

	string * getCodes(){
		queueElem * root = buildTree();
		if (root) {														// text has at least one symbol
			string * codesArray = new string[256];
			buildCodesArray(root, codesArray, "");
			return codesArray;
		}
		else {
			return NULL;
		}
	}

	~binaryHeap() {
		if (queue[1]) clearTree(queue[1]);
	}

	void clearTree(queueElem * root) {
		if (root->left){
			clearTree(root->left);
			clearTree(root->right);
		}
		delete root;
	}
};

void concatCStrings(int8_t * destintation, uint32_t currentDestinationLength, const char * str) {
	uint32_t t = 0;
	while (str[t] != '\0') {
		destintation[currentDestinationLength++] = str[t++];
	}
	destintation[currentDestinationLength] = '\0';
}

uint8_t binaryStringToUnsignedChar(int8_t * pBegin) {
	uint8_t r = 0, c = 8, t = 1;
	while (c) {
		if (pBegin[--c] == '1'){
			r += t;
		}
		t = t << 1;
	}
	return r;
}

int8_t * charsToBinaryString(uint8_t * inpStr, uint32_t strLength) {
	int8_t * out = new int8_t[strLength * 8 + 1];
	uint32_t outPointer = 0;
	for (uint32_t i = 0; i < strLength; i++) {
		for (uint32_t j = 1 << 7; j > 0; j >>= 1) {
			out[outPointer++] = (inpStr[i] & j) ? '1' : '0';
		}
	}
	out[outPointer] = '\0';
	return out;
}

void encode(const string & inp, const string & outp) {
	ifstream inputStream(inp.c_str(), ios_base::binary);
	ofstream outputStream(outp.c_str(), ios_base::binary);
	if (inputStream && outputStream) {
		inputStream.seekg(0, inputStream.end);					// move the position to the end of the file
		streampos endPosition = inputStream.tellg();			// The current position in the stream.
		uint32_t bufferLength = (size_t)endPosition;
		inputStream.seekg(0, inputStream.beg);					// move the position to the beginning of the file
		char * buffer = new char[bufferLength];
		uint32_t stat[256] = { 0 };
		inputStream.read(buffer, bufferLength);					// read file to buffer
		cout << bufferLength << endl;							// length of input file
		inputStream.close();
		uint8_t * unsignedBuffer = (uint8_t*)buffer;
		for (uint32_t i = 0; i < bufferLength; i++) {
			stat[unsignedBuffer[i]]++;
		}

		vector<statElem> validChars;
		for (int i = 0; i <= 255; i++) {
			if (stat[i]) {
				validChars.push_back({ stat[i], (uint8_t)i });
			}
		}

		binaryHeap h(stat);
		string * codesArray = h.getCodes();
		int codesArrayLengths[256] = { 0 };

		//table: unsigned short number of chars, for every char {char Char, unsigned integer Count}, unsigned integer count of symbols in input text
		uint16_t countOfValidChars = validChars.size();
		uint32_t tableSizeInBytes = sizeof(uint16_t)+countOfValidChars * (sizeof(uint32_t)+sizeof(int8_t)) + sizeof(uint32_t);
		outputStream.write((char *)&countOfValidChars, sizeof(countOfValidChars));							// count of coded charactres in the table
		for (uint32_t i = 0; i < validChars.size(); i++) {
			outputStream.write((char *)&(validChars[i].letter), sizeof(validChars[i].letter));				// char
			outputStream.write((char *)&(validChars[i].count), sizeof(validChars[i].count));				// and its count
		}
		outputStream.write((char *)&bufferLength, sizeof(bufferLength));									// count of chars in text
		cout << tableSizeInBytes << endl;																	// print table size

		uint32_t currentBufferSize = 5000000, currentOutputCodeLength = 0, allOutputCodeLength = 0, almostCurrentBufferSize = currentBufferSize - 10000;
		int8_t * outputCode = (int8_t *)calloc(currentBufferSize, sizeof(int8_t));
		for (uint32_t i = 0; i < bufferLength; i++) {
			concatCStrings(outputCode, currentOutputCodeLength, codesArray[unsignedBuffer[i]].c_str());

			if (!codesArrayLengths[unsignedBuffer[i]])
				codesArrayLengths[unsignedBuffer[i]] = codesArray[unsignedBuffer[i]].length();
			currentOutputCodeLength += codesArrayLengths[unsignedBuffer[i]];
			allOutputCodeLength += codesArrayLengths[unsignedBuffer[i]];

			if ((currentOutputCodeLength > 1000000) && !(currentOutputCodeLength % 8)) {
				int8_t * pBegin = outputCode;
				while (pBegin[0] != '\0') {
					uint8_t tChar = binaryStringToUnsignedChar(pBegin);
					outputStream.write((char *)&tChar, sizeof(tChar));
					pBegin += 8;
				}
				outputCode[0] = '\0';
				currentOutputCodeLength = 0;
			}

			if (currentOutputCodeLength > almostCurrentBufferSize) {
				outputCode = (int8_t*)realloc(outputCode, currentOutputCodeLength * 2);
				currentBufferSize = currentOutputCodeLength * 2;
				almostCurrentBufferSize = currentBufferSize - 10000;
			}
		}

		if (currentOutputCodeLength) {
			while (currentOutputCodeLength % 8) {
				concatCStrings(outputCode, currentOutputCodeLength, "0");
				currentOutputCodeLength++;
				allOutputCodeLength++;
			}
			int8_t * pBegin = outputCode;
			while (pBegin[0] != '\0') {
				uint8_t tChar = binaryStringToUnsignedChar(pBegin);
				outputStream.write((char *)&tChar, sizeof(tChar));
				pBegin += 8;
			}
		}

		cout << (allOutputCodeLength / 8) + tableSizeInBytes << endl;										//print output file length

		outputStream.close();
		delete[] codesArray;
		delete[] buffer;
		free(outputCode);
	}
	else {
		if (!inputStream) {
			if (outputStream) outputStream.close();
			cerr << "No correct input file";
		}
		else {
			inputStream.close();
			cerr << "No correct output file";
		}
	}
}

void decode(const string & inp, const string & outp){
	ifstream inputStream(inp.c_str(), ios_base::binary);
	ofstream outputStream(outp.c_str(), ios_base::binary);
	if (inputStream && outputStream) {
		inputStream.seekg(0, inputStream.end);					// move the position to the end of the file
		streampos endPosition = inputStream.tellg();			// The current position in the stream.
		uint32_t length = (size_t)endPosition;
		inputStream.seekg(0, inputStream.beg);					// move the position to the beginning of the file
		char * buffer = new char[length];
		uint32_t stat[256] = { 0 };
		inputStream.read(buffer, length);						// read file to buffer
		cout << length << endl;									// length of input file
		inputStream.close();
		uint32_t i = 0;
		uint8_t * unsignedBuffer = (uint8_t *)buffer;
		uint32_t tableLength = ((unsignedBuffer[0]) + (unsignedBuffer[1] << 8)) * 5;

		cout << sizeof(uint16_t)+tableLength + sizeof(uint32_t) << endl;		// print table size

		for (i = 2; i < tableLength; i = i + 5) {											// code, 4byte count
			stat[unsignedBuffer[i]] = unsignedBuffer[i + 1] + (unsignedBuffer[i + 2] << 8) + (unsignedBuffer[i + 3] << 16) + (unsignedBuffer[i + 4] << 24);
		}
		uint32_t numberOfChars = unsignedBuffer[i] + (unsignedBuffer[i + 1] << 8) + (unsignedBuffer[i + 2] << 16) + (unsignedBuffer[i + 3] << 24);
		i += 4;
		binaryHeap h(stat);
		queueElem * root = h.buildTree();
		queueElem * tmp = root;

		uint32_t strLength = length - sizeof(uint16_t)-tableLength - sizeof(uint32_t);
		int8_t * str = charsToBinaryString(unsignedBuffer + i, strLength);
		strLength *= 8;
		uint32_t currentOutputLength = 0, j = 0;
		char * outputStr = new char[numberOfChars];

		while (currentOutputLength < numberOfChars) {
			if (j > strLength) {
				cerr << "Corrupted input file" << endl;
				break;
			}
			if (tmp->left || tmp->right) {
				if (str[j] == '1') {
					tmp = tmp->right;
				}
				else {
					tmp = tmp->left;
				}
				j++;
			}
			else {
				outputStr[currentOutputLength] = tmp->letter;
				tmp = root;
				currentOutputLength++;
			}
		}
		if (currentOutputLength == numberOfChars) {				// correct input file
			outputStream.write(outputStr, currentOutputLength);
		}
		cout << currentOutputLength;							//print output file length
		delete[] outputStr;
		delete[] str;
		delete[] buffer;
		outputStream.close();
	}
	else {
		if (!inputStream) {
			if (outputStream) outputStream.close();
			cerr << "No correct input file";
		}
		else {
			inputStream.close();
			cerr << "No correct output file";
		}
	}
}