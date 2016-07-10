#include "ros/ros.h"
#include "ros/package.h"
#include "std_msgs/String.h"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <sstream>
#include <fstream>
#include <cmath>
using namespace std;
using namespace cv;

int main(int argc, char** argv) {
	ros::init(argc,argv,"GridMapToRCC8");
	ros::NodeHandle n;
	ros::Publisher pub = n.advertise<std_msgs::String>("sunsegstatus",1000);
	ros::NodeHandle nh("~");
	string path = ros::package::getPath("sun_project");
	ofstream out, csv;
	string fname;
	nh.getParam("map",fname);
	stringstream csv_s, rcc8_s;
	csv_s << path << "/outputs/" << "regions.txt";
	rcc8_s << path << "/outputs/" << "connections.csv";
	string str = path + "/maps/" + fname + ".pgm";


	out.open(csv_s.str().c_str(), ios::out | ios::trunc );
	csv.open(rcc8_s.str().c_str(), ios::out | ios::trunc);
	Mat src = imread(str);
    if (!src.data) return -1;

	Mat mask;
	inRange(src, Scalar(205,205,205), Scalar(205,205,205), mask);
	src.setTo(Scalar(0,0,0), mask);
    // White to black - better results during the use of Distance Transform
    for( int x = 0; x < src.rows; x++ ) {
      for( int y = 0; y < src.cols; y++ ) {
          if ( src.at<Vec3b>(x, y) == Vec3b(255,255,255) ) {
            src.at<Vec3b>(x, y)[0] = 0;
            src.at<Vec3b>(x, y)[1] = 0;
            src.at<Vec3b>(x, y)[2] = 0;
          }
        }
    }
    Mat kernel = (Mat_<float>(3,3) <<
            1,  1, 1,
            1, -8, 1,
            1,  1, 1);
    Mat imgLaplacian;
    Mat sharp = src;									// Copy source image to another temporary one
    filter2D(sharp, imgLaplacian, CV_32F, kernel);
    src.convertTo(sharp, CV_32F);
    Mat imgResult = sharp - imgLaplacian;
    imgResult.convertTo(imgResult, CV_8UC3);			// Convert back to 8bits gray scale
    imgLaplacian.convertTo(imgLaplacian, CV_8UC3);
    src = imgResult;									// Copy back
    Mat bw;
    cvtColor(src, bw, CV_BGR2GRAY);
    threshold(bw, bw, 40, 255, CV_THRESH_BINARY | CV_THRESH_OTSU);
    Mat dist;
    distanceTransform(bw, dist, CV_DIST_L2, 3);			// Perform the distance transform algorithm
    normalize(dist, dist, 0, 1., NORM_MINMAX);			// Normalize between 0 and 1 for better threshold
    threshold(dist, dist, .3, 1., CV_THRESH_BINARY);
    Mat kernel1 = Mat::ones(3, 3, CV_8UC1);
    dilate(dist, dist, kernel1);						// Blur
    Mat dist_8u;
    dist.convertTo(dist_8u, CV_8U);						// CV_8U of the distance image for findContours
	vector<vector<Point> > contours;					// Find total markers
	findContours(dist_8u, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
	Mat markers = Mat::zeros(dist.size(), CV_32SC1);    // Create the marker image for the watershed algorithm
    for (size_t i = 0; i < contours.size(); i++)		// Draw the foreground markers
        drawContours(markers, contours, static_cast<int>(i), Scalar::all(static_cast<int>(i)+1), -1);

    circle(markers, Point(5,5), 3, CV_RGB(255,255,255), -1);	    // Draw the background marker
    watershed(src, markers);							// Perform the watershed algorithm
    Mat mark = Mat::zeros(markers.size(), CV_8UC1);
    markers.convertTo(mark, CV_8UC1);
    bitwise_not(mark, mark);

    vector<Moments> mu(contours.size());				// Save moments of contours
  	vector<Point2f> mc(contours.size());				// Center of mass of contours

	bool adj_mat[contours.size()][contours.size()];
	for(int i = 0; i < contours.size(); i++) {
		for(int j = 0; j < contours.size(); j++) {
			adj_mat[i][j] = false;
		}
	}

  	for (size_t i = 0; i < contours.size(); i++) {
		mu[i] = moments(contours[i], false);
		int mu_x = mu[i].m10/mu[i].m00;
		int mu_y = mu[i].m01/mu[i].m00;
		mc[i] = Point2f(mu_x,mu_y);
		out << "region(r" << i << ",(" << mu_x << "," << mu_y << "))." << endl;
	}

	for(int p=0; p<contours.size();p++) {
		for(int q=p+1; q<contours.size();q++) {
			vector<Vec3b> colors;	// Generate random colors
			int b, g, r;
			for (size_t i = 0; i < contours.size(); i++) {
				if(i==p || i==q) r = g = b = 254;
				else r = g = b = 127;
				colors.push_back(Vec3b((uchar)b, (uchar)g, (uchar)r));
			}

			Mat dst = Mat::zeros(markers.size(), CV_8UC3);		// Create the result image
			for (int i = 0; i < markers.rows; i++) {			// Fill labeled objects with random colors
				for (int j = 0; j < markers.cols; j++) {
				    int index = markers.at<int>(i,j);
					if (index > 0 && index <= static_cast<int>(contours.size()))
				        dst.at<Vec3b>(i,j) = colors[index-1];
				    else
				        dst.at<Vec3b>(i,j) = Vec3b(0,0,0);
				}
			}

			Mat out_img = Mat::zeros(markers.size(), CV_8UC3);		// Create the result image
			for(int i = 0; i < out_img.rows; i++) {
				for(int j = 0; j < out_img.cols; j++) {
					int src_val = (int) src.at<Vec3b>(i,j)[0];
					int dst_val = (int) dst.at<Vec3b>(i,j)[0];
					if(src_val == 254 && dst_val != 127 && src_val != 127) out_img.at<Vec3b>(i,j) = Vec3b(255,255,255);
					if(dst_val == 254) out_img.at<Vec3b>(i,j) = Vec3b(255,255,255);
				}
			}	

			Rect rect;
			floodFill(out_img,mc[p],100,&rect,0,0,8);
			if ((int) out_img.at<Vec3b>(mc[q].y,mc[q].x)[0]==100) {
				out << "connected(r" << p << ",r" << q << ")." << endl;
				adj_mat[p][q] = adj_mat[q][p] = true;
			}
		}
	}

	vector<Vec3b> colors;	// Generate random colors
	int b, g, r;
	for (size_t i = 0; i < contours.size(); i++) {
		b = theRNG().uniform(0, 255);
		g = theRNG().uniform(0, 255);
		r = theRNG().uniform(0, 255);
		colors.push_back(Vec3b((uchar)b, (uchar)g, (uchar)r));
	}

	Mat dst = Mat::zeros(markers.size(), CV_8UC3);		// Create the result image
	for (int i = 0; i < markers.rows; i++) {			// Fill labeled objects with random colors
		for (int j = 0; j < markers.cols; j++) {
		    int index = markers.at<int>(i,j);
			if (index > 0 && index <= static_cast<int>(contours.size()))
		        dst.at<Vec3b>(i,j) = colors[index-1];
		    else
		        dst.at<Vec3b>(i,j) = Vec3b(0,0,0);
		}
	}

	for(int i = 0; i < contours.size(); i++) {
		for(int j = 0; j < contours.size(); j++) {
			cout << adj_mat[i][j] << ",";
			csv << adj_mat[i][j] << ",";
		}
		cout << endl;
		csv << endl;
	}

	for( int i = 0; i< contours.size(); i++ ) {
		stringstream ss;
		ss << i;
		string str = ss.str();
		putText(dst, str, mc[i], FONT_HERSHEY_TRIPLEX, 0.35, Scalar(255,0,0));
    }
	imwrite(path + "/outputs/" + "output.bmp",dst);
	out.close();
	csv.close();

	ros::Rate loop_rate(10);
	while(ros::ok()) {
		std_msgs::String msg;
		stringstream ss;
		ss << "RCC8-Succ";
		msg.data = ss.str();
		pub.publish(msg);
		ros::spinOnce();
		loop_rate.sleep();
	}

    return 0;
}
