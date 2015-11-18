#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

void find_borders() {
	Mat image = imread("portrait.jpg", IMREAD_GRAYSCALE);
	if (image.empty()) {
		return;
	}
	
	// 1st way is gradient(Sobel):
	Mat grad;
	Mat grad_x, grad_y;
	Mat abs_grad_x, abs_grad_y;

	// Gradient X
	Sobel(image, grad_x, CV_16S, 1, 0);
	// Gradient Y
	Sobel(image, grad_y, CV_16S, 0, 1);

	// Convert our partial results back to CV_8U:
	convertScaleAbs(grad_x, abs_grad_x);
	convertScaleAbs(grad_y, abs_grad_y);

	// Try to approximate the gradient by adding both directional gradients
	addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0, grad);
	imwrite("portrait_after_Sobel.jpg", grad);


	// 2nd way is second derivative(Laplacian):
	Mat lapl_abs_dst, lapl_dst;

	Laplacian(image, lapl_dst, CV_16S);
	convertScaleAbs(lapl_dst, lapl_abs_dst);

	imwrite("portrait_after_Laplacian.jpg", lapl_abs_dst);


	//3rd way is morphological operations.
	Mat eroded, difference;
	// 1st step: erode original image
	erode(image, eroded, Mat());
	// 2nd step: find the difference
	absdiff(image, eroded, difference);

	imwrite("portrait_after_morphological_op.jpg", difference);
}

// 4-connectivity connected component labeling for binary image
// 2 pass mplememntation in O(rows * cols * connected_components)
void connected_components(int background) {
	Mat image = imread("connected_components.jpg", IMREAD_GRAYSCALE);
	if (image.empty()) {
		return;
	}

	threshold(image, image, 127.0, 255.0, THRESH_BINARY);
	int next_label = 1;
	Mat labels = Mat::zeros(image.size(), CV_8U);
	vector<set<uchar>> equivalent_groups(255);

	// first pass
	for (int r = 0; r < image.rows; r++) {
		for (int c = 0; c < image.cols; c++) {
			if (image.at<uchar>(r, c) != background) {
				vector<uchar> neighbours_labels = vector<uchar>();
				if ((r - 1 >= 0) && (image.at<uchar>(r - 1, c) != background)) {
					neighbours_labels.push_back(labels.at<uchar>(r - 1, c));
				}
				if ((c - 1 >= 0) && (image.at<uchar>(r, c - 1) != background)) {
					neighbours_labels.push_back(labels.at<uchar>(r, c - 1));
				}
				
				if (neighbours_labels.empty()) {
					equivalent_groups[next_label].insert(next_label);
					labels.at<uchar>(r, c) = next_label++;
				}
				else {
					uchar min_label = neighbours_labels[0];
					for (int i = 1; i < neighbours_labels.size(); i++) {
						min_label = min(neighbours_labels[i], min_label);
					}
					labels.at<uchar>(r, c) = min_label;
					equivalent_groups[min_label].insert(neighbours_labels.begin(), neighbours_labels.end());
				}
			}
		}
	}
	
	// second pass
	for (int r = 0; r < image.rows; r++) {
		for (int c = 0; c < image.cols; c++) {
			if (image.at<uchar>(r, c) != background) {
				uchar group_number = labels.at<uchar>(r, c);
				for (int g = 1; g < group_number; g++) {
					if (equivalent_groups[g].find(group_number) != equivalent_groups[g].end()) {
						group_number = g;
						g = 0;
					}
				}
				labels.at<uchar>(r, c) = group_number;
			}
		}
	}

	equalizeHist(labels, labels);
	namedWindow("Connected components", WINDOW_AUTOSIZE);
	imshow("Connected components", labels);
	imwrite("connected_components_detected.jpg", labels);
	waitKey(0);
}

// Split table structure and text for given image
void find_table() {
	Mat image = imread("table.jpg", IMREAD_GRAYSCALE);
	if (image.empty()) {
		return;
	}

	Mat dst, horizontal, vertical;
	// Transform grayscale image to binary.
	threshold(image, image, 127.0, 255.0, THRESH_BINARY);
	
	// Detect horizontal lines
	Mat horizontalElement = getStructuringElement(MORPH_RECT, Size(7, 1));
	dilate(image, horizontal, horizontalElement, Point(-1,-1), 2);
	morphologyEx(horizontal, horizontal, MORPH_OPEN, Mat(), Point(-1, -1), 5);
	erode(horizontal, horizontal, horizontalElement, Point(-1, -1), 2);

	// Detect vertical lines
	Mat verticalElement = getStructuringElement(MORPH_RECT, Size(1, 7));
	dilate(image, vertical, verticalElement, Point(-1, -1), 5);
	erode(vertical, vertical, verticalElement, Point(-1, -1), 5);

	addWeighted(horizontal, 0.5, vertical, 0.5, 0.0, dst);
	imwrite("table_cleared.jpg", dst);
}

// Detect groupped and alone circles with morphological operations
void groupped_and_alone_circles() {
	Mat image = imread("circles.jpg", IMREAD_GRAYSCALE);
	if (image.empty()) {
		return;
	}
	threshold(image, image, 30.0, 255.0, THRESH_BINARY);
	Mat groupped, alone, on_borders;

	// Find groups of circles
	int erosion_type = MORPH_ELLIPSE, erosion_size = 8;
	Mat element = getStructuringElement(erosion_type,
	                                    Size(2 * erosion_size + 1, 2 * erosion_size + 1),
	                                    Point(erosion_size, erosion_size));
	morphologyEx(image, groupped, MORPH_OPEN, element);
	threshold(groupped, groupped, 30.0, 255.0, THRESH_BINARY);
	imwrite("circles_groupped.jpg", groupped);

	// Find alone circles:
	absdiff(image, groupped, alone);
	// Filter noize a bit
	erosion_size = 3;
	element = getStructuringElement(erosion_type,
		Size(2 * erosion_size + 1, 2 * erosion_size + 1),
		Point(erosion_size, erosion_size));
	morphologyEx(alone, alone, MORPH_OPEN, element);
	imwrite("circles_alone.jpg", groupped);
}

bool cmp_radiuses(const Vec3f &a, const Vec3f &b) {
	return a[2] > b[2];
}

// Find coins and sort them in decreasing order
void find_and_sort_coins() {
	Mat image = imread("coins_1.jpg", IMREAD_COLOR);
	if (image.empty()) {
		return;
	}

	Mat image_grayscale;
	cvtColor(image, image_grayscale, CV_BGR2GRAY);

	Mat grad_x, grad_y, grad;
	Mat abs_grad_x, abs_grad_y;
	// Gradient X
	Sobel(image_grayscale, grad_x, CV_16S, 1, 0);
	// Gradient Y
	Sobel(image_grayscale, grad_y, CV_16S, 0, 1);

	// Convert our partial results back to CV_8U:
	convertScaleAbs(grad_x, abs_grad_x);
	convertScaleAbs(grad_y, abs_grad_y);

	// Try to approximate the gradient by adding both directional gradients
	addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0, grad);
	// Make binary image
	threshold(grad, grad, 40.0, 255.0, THRESH_BINARY);

	// Fill inner space in coins
	Mat element = getStructuringElement(MORPH_ELLIPSE, Size(5,5));
	morphologyEx(grad, grad, MORPH_CLOSE, element, Point(-1, -1), 3);
	erode(grad, grad, element, Point(-1, -1), 10);
	dilate(grad, grad, element, Point(-1, -1), 2);

	// Outline contours:
	Mat eroded, difference;
	// 1st step: erode original image
	erode(grad, eroded, Mat());
	// 2nd step: find the difference
	absdiff(grad, eroded, difference);

	vector<Vec3f> circles;
	// Apply the Hough Transform to find the circles
	HoughCircles(difference, circles, CV_HOUGH_GRADIENT, 1, image_grayscale.cols / 10, 200, 22, 0, 0);

	// Sort circles in decreasing order
	sort(circles.begin(), circles.end(), cmp_radiuses);

	// Draw detected circles 
	RNG rng(100);
	for (size_t i = 0; i < circles.size(); i++) {
		Point center(cvRound(circles[i][0]), cvRound(circles[i][1]));
		int radius = cvRound(circles[i][2]) + 15;
		Scalar color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
		// Draw number in the circle's center
		putText(image, to_string(i + 1), center, FONT_HERSHEY_PLAIN, 2, color, 2);
		// circle outline
		circle(image, center, radius, color, 3, 8, 0);
	}
	
	//Save and show
	imwrite("Coins_1_found_and_sorted.jpg", image);
	namedWindow("Find coins and sort", CV_WINDOW_AUTOSIZE);
	imshow("Find coins and sort", image);
	waitKey(0);
}

void split_coins_and_text() {
	Mat image = imread("coins_2.jpg", IMREAD_COLOR);
	if (image.empty()) {
		return;
	}

	Mat image_grayscale;
	cvtColor(image, image_grayscale, CV_BGR2GRAY);

	// Blur and find coins
	GaussianBlur(image_grayscale, image_grayscale, Size(9, 9), 2, 2);
	vector<Vec3f> circles;
	HoughCircles(image_grayscale, circles, CV_HOUGH_GRADIENT, 1, image_grayscale.cols / 10, 200, 50, 0, 0);
	
	Mat coins = Mat::zeros(image.rows, image.cols, CV_8UC3);
	coins = ~coins;

	for (size_t i = 0; i < circles.size(); i++) {
		Mat mask = Mat::zeros(image.rows, image.cols, CV_8UC1);
		Point center(cvRound(circles[i][0]), cvRound(circles[i][1]));
		int radius = cvRound(circles[i][2]);
		circle(mask, center, radius, Scalar(255, 255, 255), -1, 8, 0); 
		image.copyTo(coins, mask); // copy values of img to coins if mask is > 0.
	}

	Mat text = Mat::zeros(image.rows, image.cols, CV_8UC3);;
	text = ~text;
	Mat mask;
	// Make binary image
	threshold(image_grayscale, mask, 230.0, 255.0, THRESH_BINARY);
	Mat circle_elem = getStructuringElement(MORPH_ELLIPSE, Size(5, 5));
	// Delete small figures(text)
	dilate(mask, mask, Mat(), Point(-1, -1), 8);
	// Fill inner space in coins
	morphologyEx(mask, mask, MORPH_OPEN, circle_elem, Point(-1,-1), 16);
	erode(mask, mask, Mat(), Point(-1, -1), 8);

	image.copyTo(text, mask); // copy values of img to text if mask is > 0.

	imwrite("Coins_2_coins.jpg", coins);
	imwrite("Coins_2_text.jpg", coins);
	namedWindow("Coins", CV_WINDOW_AUTOSIZE);
	imshow("Coins", coins);
	namedWindow("Text", CV_WINDOW_AUTOSIZE);
	imshow("Text", text);
	waitKey(0);
}

// Detect and group coins in very noisy image
void detect_and_group_one() {
	Mat image = imread("coins_noize_1.jpg", IMREAD_COLOR);
	if (image.empty()) {
		return;
	}

	Mat image_blured, image_grayscale;
	medianBlur(image, image_blured, 7);
	cvtColor(image_blured, image_grayscale, CV_BGR2GRAY);

	// Find circles
	vector<Vec3f> circles;
	HoughCircles(image_grayscale, circles, CV_HOUGH_GRADIENT, 1, image_grayscale.cols / 20, 120, 20, 20, 50);
	
	vector<vector<Vec3f>> groups;
	vector<int> groups_radius;
	for (size_t i = 0; i < circles.size(); i++) {
		bool assigned = false;
		int radius = cvRound(circles[i][2]);
		for (size_t cur_group = 0; cur_group < groups.size(); cur_group++) {
			if (abs(radius - groups_radius[cur_group]) < 10) {
				groups[cur_group].push_back(circles[i]);
				assigned = true;
			}
		}
		if (!assigned) {
			vector<Vec3f> vec = vector<Vec3f>();
			vec.push_back(circles[i]);
			groups.push_back(vec);
			groups_radius.push_back(radius);
		}
	}
	
	RNG rng(100);
	for (size_t i = 0; i < groups.size(); i++) {
		vector<Vec3f> curret_group = groups[i];
		Scalar color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
		for (size_t n = 0; n < curret_group.size(); n++) {
			Point center(cvRound(curret_group[n][0]), cvRound(curret_group[n][1]));
			int radius = cvRound(curret_group[n][2]);
			circle(image, center, radius, color, 3, 8, 0);
		}
	}

	imwrite("coins_noize_1_detected.jpg", image);
	namedWindow("coins_noize_1", CV_WINDOW_AUTOSIZE);
	imshow("coins_noize_1", image);
	waitKey(0);
}

void detect_and_group_two() {
	Mat image = imread("coins_noize_2.jpg", IMREAD_COLOR);
	if (image.empty()) {
		return;
	}

	Mat image_blured, image_grayscale;
	int canny_param = 100;

	GaussianBlur(image, image_blured, Size(5, 5), 3, 3);

	cvtColor(image_blured, image_grayscale, CV_BGR2GRAY);
	
	// Find circles
	vector<Vec3f> circles;
	HoughCircles(image_grayscale, circles, CV_HOUGH_GRADIENT, 1, image_grayscale.cols / 20, canny_param * 2, 20, 20, 50);

	vector<vector<Vec3f>> groups;
	vector<int> groups_radius;
	for (size_t i = 0; i < circles.size(); i++) {
		bool assigned = false;
		int radius = cvRound(circles[i][2]);
		for (size_t cur_group = 0; cur_group < groups.size(); cur_group++) {
			if (abs(radius - groups_radius[cur_group]) < 7) {
				groups[cur_group].push_back(circles[i]);
				assigned = true;
			}
		}
		if (!assigned) {
			vector<Vec3f> vec = vector<Vec3f>();
			vec.push_back(circles[i]);
			groups.push_back(vec);
			groups_radius.push_back(radius);
		}
	}

	RNG rng(100);
	for (size_t i = 0; i < groups.size(); i++) {
		vector<Vec3f> curret_group = groups[i];
		Scalar color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
		for (size_t n = 0; n < curret_group.size(); n++) {
			Point center(cvRound(curret_group[n][0]), cvRound(curret_group[n][1]));
			int radius = cvRound(curret_group[n][2]);
			circle(image, center, radius, color, 3, 8, 0);
		}
	}

	imwrite("coins_noize_2_detected.jpg", image);
	namedWindow("coins_noize_2", CV_WINDOW_AUTOSIZE);
	imshow("coins_noize_2", image);
	waitKey(0);
}

void detect_and_group_three() {
	Mat image = imread("coins_noize_3.jpg", IMREAD_COLOR);
	if (image.empty()) {
		return;
	}

	Mat image_blured, image_grayscale;
	int canny_param = 80;
	
	medianBlur(image, image_blured, 7);
	cvtColor(image_blured, image_grayscale, CV_BGR2GRAY);
	
	// Find circles
	vector<Vec3f> circles;
	HoughCircles(image_grayscale, circles, CV_HOUGH_GRADIENT, 1, image_grayscale.cols / 20, canny_param * 2, 15, 20, 50);

	vector<vector<Vec3f>> groups;
	vector<int> groups_radius;
	for (size_t i = 0; i < circles.size(); i++) {
		bool assigned = false;
		int radius = cvRound(circles[i][2]);
		for (size_t cur_group = 0; cur_group < groups.size(); cur_group++) {
			if (abs(radius - groups_radius[cur_group]) < 9) {
				groups[cur_group].push_back(circles[i]);
				assigned = true;
			}
		}
		if (!assigned) {
			vector<Vec3f> vec = vector<Vec3f>();
			vec.push_back(circles[i]);
			groups.push_back(vec);
			groups_radius.push_back(radius);
		}
	}

	RNG rng(100);
	for (size_t i = 0; i < groups.size(); i++) {
		vector<Vec3f> curret_group = groups[i];
		Scalar color = Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255));
		for (size_t n = 0; n < curret_group.size(); n++) {
			Point center(cvRound(curret_group[n][0]), cvRound(curret_group[n][1]));
			int radius = cvRound(curret_group[n][2]);
			circle(image, center, radius, color, 3, 8, 0);
		}
	}

	imwrite("coins_noize_3_detected.jpg", image);
	namedWindow("coins_noize_3", CV_WINDOW_AUTOSIZE);
	imshow("coins_noize_3", image);
	waitKey(0);
}
