#include <opencv2/opencv.hpp>
#include <string>
#include <fstream>

# define M_PI           3.14159265358979323846  /* pi */

using namespace cv;
using namespace std;

double scale_x = 0, scale_y = 0;
Point origin;
const int COUNT_OF_IMAGES = 13;

bool cmp_pointsOX(const Vec3f &a, const Vec3f &b) {
	return a[0] < b[0];
}

// Try to find coefficents of y = kx + b on image
vector<double> line_coefficents(Mat line_plot) {
	const int STEP_X = line_plot.cols / 3;
	Mat line_detect = Mat::zeros(line_plot.size(), CV_8UC1);

	// Draw 2 vertical lines
	line(line_detect, Point(origin.x + STEP_X, 10), Point(origin.x + STEP_X, line_plot.rows - 10), Scalar(255), 5);
	line(line_detect, Point(origin.x - STEP_X, 10), Point(origin.x - STEP_X, line_plot.rows - 10), Scalar(255), 5);

	// Find intersections
	bitwise_and(line_detect, line_plot, line_detect);
	Mat ellipse = getStructuringElement(MORPH_ELLIPSE, Size(9, 9));
	// Input plot may contain some noizy pixels, so get rid of them
	Mat ellipse_small = getStructuringElement(MORPH_ELLIPSE, Size(2, 2));
	erode(line_detect, line_detect, ellipse_small);
	// And outline our intersections point for Hough detector
	dilate(line_detect, line_detect, ellipse);
	
	vector<Vec3f> intersections;
	HoughCircles(line_detect, intersections, CV_HOUGH_GRADIENT, 1, 8, 200, 6, 3, 8);

	if (intersections.size() != 2) {
		cout << "Unable to count line coefficients";
		throw exception("Unable to count line coefficients");
	}

	double p1x = intersections[0][0], p1y = intersections[0][1];
	double p2x = intersections[1][0], p2y = intersections[1][1];

	// Find points coordinates in scale of image
	double x1 = (p1x - origin.x) / scale_x, y1 = (origin.y - p1y) / scale_y;
	double x2 = (p2x - origin.x) / scale_x, y2 = (origin.y - p2y) / scale_y;

	double k = (y1 - y2) / (x1 - x2);
	double b = y1 - k * x1;

	vector<double> answer;
	answer.push_back(k);
	answer.push_back(b);
	return answer;
}

// Try to find coefficents of y = cx^2 + dx + e on image
vector<double> parabola_coefficents(Mat parabola_plot) {
	const int STEP_Y = -1 * parabola_plot.rows / 10;
	Mat parabola_detect = Mat::zeros(parabola_plot.size(), CV_8UC1);

	// Draw 3 horizontal lines
	line(parabola_detect, Point(10, origin.y + STEP_Y), Point(parabola_plot.cols - 10, origin.y + STEP_Y), Scalar(255), 2);
	line(parabola_detect, Point(10, origin.y + 2 * STEP_Y), Point(parabola_plot.cols - 10, origin.y + 2 * STEP_Y), Scalar(255), 2);
	line(parabola_detect, Point(10, origin.y + 3 * STEP_Y), Point(parabola_plot.cols - 10, origin.y + 3 * STEP_Y), Scalar(255), 2);

	// Find intersections
	bitwise_and(parabola_detect, parabola_plot, parabola_detect);
	Mat ellipse = getStructuringElement(MORPH_ELLIPSE, Size(9, 9));
	// Input plot may contain some noizy pixels, so get rid of them
	Mat ellipse_small = getStructuringElement(MORPH_ELLIPSE, Size(2, 2));
	erode(parabola_detect, parabola_detect, ellipse_small);
	// And outline our intersections point for Hough detector
	dilate(parabola_detect, parabola_detect, ellipse);

	vector<Vec3f> intersections;
	HoughCircles(parabola_detect, intersections, CV_HOUGH_GRADIENT, 1, 8, 200, 6, 3, 8);
	
	if (intersections.size() < 3) {
		cout << "Unable to count parabola coefficients";
		throw exception("Unable to count parabola coefficients");
	}

	// Sort intersections with respect to OX from left to right
	sort(intersections.begin(), intersections.end(), cmp_pointsOX);
	int last = intersections.size() - 1;

	double p1x = intersections[0][0], p1y = intersections[0][1];
	double p2x = intersections[last / 2][0], p2y = intersections[last / 2][1];
	double p3x = intersections[last][0], p3y = intersections[last][1];

	// Find points coordinates in scale of image
	double x1 = (p1x - origin.x) / scale_x, y1 = (origin.y - p1y) / scale_y;
	double x2 = (p2x - origin.x) / scale_x, y2 = (origin.y - p2y) / scale_y;
	double x3 = (p3x - origin.x) / scale_x, y3 = (origin.y - p3y) / scale_y;

	// Solve system 3x3
	// Subtract 2nd line from 1st, and 3rd from 2nd
	double dy1 = y1 - y2, dy2 = y2 - y3;
	double dx1sq = x1 * x1 - x2 * x2, dx2sq = x2 * x2 - x3 * x3;
	double dx1 = x1 - x2, dx2 = x2 - x3;

	// Solve 2x2 system with Cramer's rule
	double main_det = dx1sq * dx2 - dx1 * dx2sq;
	double det_c = dy1 * dx2 - dx1 * dy2;
	double det_d = dx1sq * dy2 - dy1 * dx2sq;

	double c = det_c / main_det;
	double d = det_d / main_det;
	double e = y1 - c * x1 * x1 - d * x1;
	
	vector<double> answer;
	answer.push_back(c);
	answer.push_back(d);
	answer.push_back(e);
	return answer;
}

// Try to find coefficents of y = sin(ax + b) on image
vector<double> sin_coefficents(Mat sin_plot) {
	Mat sin_detect = Mat::zeros(sin_plot.size(), CV_8UC1);

	// Draw horizontal line y = 1
	line(sin_detect, Point(10, origin.y - scale_y - 1), Point(sin_plot.cols - 10, origin.y - scale_y - 1), Scalar(255), 2);
	
	// Find intersections
	bitwise_and(sin_detect, sin_plot, sin_detect);
	Mat ellipse = getStructuringElement(MORPH_ELLIPSE, Size(9, 9));
	// Input plot may contain some noizy pixels, so get rid of them
	Mat ellipse_small = getStructuringElement(MORPH_ELLIPSE, Size(2, 2));
	erode(sin_detect, sin_detect, ellipse_small);
	// And outline our intersections point for Hough detector
	dilate(sin_detect, sin_detect, ellipse);

	vector<Vec3f> intersections;
	HoughCircles(sin_detect, intersections, CV_HOUGH_GRADIENT, 1, 14, 200, 5, 3, 8);

	if (intersections.size() < 2) {
		cout << "Unable to count sin coefficients";
		throw exception("Unable to count sin coefficients");
	}

	// Sort intersections with respect to OX from left to right
	sort(intersections.begin(), intersections.end(), cmp_pointsOX);

	double sum_dist = intersections[intersections.size() - 1][0] - intersections[0][0];
	double avg_period = sum_dist / ((double)intersections.size() - 1);
	double avg_period_in_scale = avg_period / scale_x;
	double period_coef = 2 * M_PI / avg_period_in_scale;

	// Create new working image
	sin_detect = Mat::zeros(sin_plot.size(), CV_8UC1);
	// Draw horizontal line y = 0 to find coefficient b
	line(sin_detect, Point(10, origin.y), Point(sin_plot.cols - 10, origin.y), Scalar(255), 2);
	// Find intersections
	bitwise_and(sin_detect, sin_plot, sin_detect);
	// Input plot may contain some noizy pixels, so get rid of them
	erode(sin_detect, sin_detect, ellipse_small);
	// And outline our intersections point for Hough detector
	dilate(sin_detect, sin_detect, ellipse);

	intersections.erase(intersections.begin(), intersections.end());
	HoughCircles(sin_detect, intersections, CV_HOUGH_GRADIENT, 1, 14, 200, 5, 3, 8);

	if (intersections.empty()) {
		cout << "Unable to count sin coefficients";
		throw exception("Unable to count sin coefficients");
	}

	// Sort intersections with respect to OX from left to right
	sort(intersections.begin(), intersections.end(), cmp_pointsOX);

	double shift = intersections[0][0] - origin.x;
	double pre_shift = 0.0;

	int while_counter = 0;
	double half_period = avg_period / 2.0;
	while (shift <= 0.0) {
		pre_shift = shift;
		shift += half_period;
		while_counter++;
		if (while_counter > 100) {
			cout << "Unable to count sin coefficients";
			throw exception("Unable to count sin coefficients");
		}
	}
	pre_shift /= -(period_coef * scale_x);
	
	vector<double> answer;
	answer.push_back(period_coef);
	answer.push_back(pre_shift);
	return answer;
}

void find_origin_and_scale() {
	// count scale and origin and write them to global variables
	// If the task reqiures, this can be done for every input plot
	Mat image = imread("plots/0.png", IMREAD_COLOR);
	if (image.empty()) {
		return;
	}

	Mat image_grayscale = Mat::zeros(image.size(), CV_8UC1);
	cvtColor(image, image_grayscale, CV_BGR2GRAY);

	// Find origin
	vector<Vec3f> circles;
	HoughCircles(image_grayscale, circles, CV_HOUGH_GRADIENT, 1, 10, 160, 15, 0, 10);
	origin.x = cvRound(circles[0][0]);
	origin.y = cvRound(circles[0][1]);

	// Find scale -- erase all that is not a scale segment[(0;-1), (1;-1)]
	cvtColor(image, image_grayscale, CV_BGR2GRAY);
	// Erase nonhorizontal lines
	Mat horizontalElement = getStructuringElement(MORPH_RECT, Size(7, 1));
	morphologyEx(image_grayscale, image_grayscale, MORPH_CLOSE, horizontalElement, Point(-1, -1), 5);
	// make binary image
	threshold(image_grayscale, image_grayscale, 100.0, 255.0, THRESH_BINARY);
	image_grayscale = ~image_grayscale;

	// Count white pixels -- it is scale x, distance to the segment is scale y
	for (int y = 0; y < image_grayscale.rows; y++) {
		for (int x = 0; x < image_grayscale.cols; x++) {
			if (image_grayscale.at<uchar>(y, x) == 255) {
				if (!scale_y) {
					scale_y = abs(origin.y - y);
				}
				scale_x += 1.0;
			}
		}
	}
}

void write_to_file(vector<double> coefficients) {
	static int iteration = 0;
	static string data;
	
	data += to_string(iteration) + ",";
	for (int i = 0; i < coefficients.size() - 1; i++) {
		data += to_string(coefficients[i]) + ",";
	}
	data += to_string(coefficients[coefficients.size() - 1]) + "\n";

	iteration++;
	if (iteration == COUNT_OF_IMAGES) {
		// All work is done, so it's time to write all data to document
		ofstream myfile;
		myfile.open("parameters.txt");
		myfile << data;
		myfile.close();
	}
}

void hw4() {
	find_origin_and_scale();

	// process every image
	for (int i = 0; i < COUNT_OF_IMAGES; i++) {
		string picture_name = "plots/" + to_string(i) + ".png";
		Mat image = imread(picture_name, IMREAD_COLOR);
		if (image.empty()) {
			return;
		}
		
		// Plots are drawn with red, green, blue colors, so split image to BGR channles
		Mat image_grayscale;
		cvtColor(image, image_grayscale, CV_BGR2GRAY);
		image_grayscale = ~image_grayscale;
		vector<Mat> channels;
		split(image, channels);
		
		Mat line_plot, parabola_plot, sin_plot;
		
		for (auto &channel : channels) {
			// For every channel change white background to black and make picture binary
			bitwise_and(channel, image_grayscale, channel);
			medianBlur(channel, channel, 3);
			threshold(channel, channel, 25.0, 255.0, THRESH_BINARY);

			Mat channel_copy;
			channel.copyTo(channel_copy);
			vector<Vec2f> lines;
			
			if (line_plot.empty()) {
				// Try to detect line on every channel
				HoughLines(channel_copy, lines, 1, CV_PI / 180, 205);
				if (lines.size() == 1 || lines.size() == 2) {
					line_plot = channel;
					continue;
				}
			}

			if (parabola_plot.empty()) {
				// Try to detect parabola
				const int STEP_X = scale_x / 2, STEP_Y = scale_y / 2;
				Mat parabola_detect = Mat::zeros(channel.size(), CV_8UC1);
				Mat ellipse = getStructuringElement(MORPH_ELLIPSE, Size(9, 9));
				//Draw line x = 0.5
				line(parabola_detect, Point(STEP_X, origin.y - STEP_Y), Point(channel.cols - STEP_X, origin.y - STEP_Y), Scalar(255), 2);
				bitwise_and(parabola_detect, channel, parabola_detect);
				dilate(parabola_detect, parabola_detect, ellipse);
				Canny(parabola_detect, parabola_detect, 100, 200);

				//Count intersections of plot and line 
				vector<Vec3f> intersections;
				HoughCircles(parabola_detect, intersections, CV_HOUGH_GRADIENT, 1, 8, 200, 6, 3, 8);

				if (intersections.size() == 1 || intersections.size() == 2) {
					parabola_plot = channel;
					continue;
				}
			}

			// If we didnt manage to find a line or a parabola, this channel contains sin
			sin_plot = channel;
		}

		vector<double> coefficients, sin_coef, parabola_coef, line_coef;
		try {
			sin_coef = sin_coefficents(sin_plot);
		}
		catch (exception e) {
			sin_coef.push_back(0.0);
			sin_coef.push_back(0.0);
		}
		coefficients.insert(coefficients.end(), sin_coef.begin(), sin_coef.end());
		
		try {
			parabola_coef = parabola_coefficents(parabola_plot);
		}
		catch (exception e) {
			parabola_coef.push_back(0.0);
			parabola_coef.push_back(0.0);
			parabola_coef.push_back(0.0);
		}
		coefficients.insert(coefficients.end(), parabola_coef.begin(), parabola_coef.end());

		try {
			line_coef = line_coefficents(line_plot);
		}
		catch (exception e) {
			line_plot.push_back(0.0);
			line_plot.push_back(0.0);
		}
		coefficients.insert(coefficients.end(), line_coef.begin(), line_coef.end());
		
		write_to_file(coefficients);
	}
}
