//
// Created by notoraptor-desktop on 25/09/2023.
//

#ifndef SIMILIRAPTOR_CORE_HPP
#define SIMILIRAPTOR_CORE_HPP

#include <cstdlib>

struct Sequence {
	int* r; // red
	int* g; // green
	int* b; // blue
};

constexpr int SIMPLE_MAX_PIXEL_DISTANCE = 255 * 3;
constexpr int V = SIMPLE_MAX_PIXEL_DISTANCE;
constexpr int K = 0;
constexpr int KV_PLUS_V = K * V + V;

inline double exaggerate(double x) {
	return KV_PLUS_V * x / (K * x + V);
}

inline double pixelDistance(const Sequence* p1, int indexP1, const Sequence* p2, int indexP2) {
	return exaggerate(
			std::abs(p1->r[indexP1] - p2->r[indexP2])
			+ std::abs(p1->g[indexP1] - p2->g[indexP2])
			+ std::abs(p1->b[indexP1] - p2->b[indexP2]));
}

#define PIXEL_DISTANCE(p1, x, y, p2, localX, localY, width) pixelDistance(p1, (x) + (y) * (width), p2, (localX) + (localY) * (width))

template <typename T>
inline T getMin(T t1, T t2, T t3, T t4) {
	T val = t1;
	if (val > t2) val = t2;
	if (val > t3) val = t3;
	if (val > t4) val = t4;
	return val;
}

template <typename T>
inline T getMin(T t1, T t2, T t3, T t4, T t5, T t6) {
	T val = t1;
	if (val > t2) val = t2;
	if (val > t3) val = t3;
	if (val > t4) val = t4;
	if (val > t5) val = t5;
	if (val > t6) val = t6;
	return val;
}

template <typename T>
inline T getMin(T t1, T t2, T t3, T t4, T t5, T t6, T t7, T t8, T t9) {
	T val = t1;
	if (val > t2) val = t2;
	if (val > t3) val = t3;
	if (val > t4) val = t4;
	if (val > t5) val = t5;
	if (val > t6) val = t6;
	if (val > t7) val = t7;
	if (val > t8) val = t8;
	if (val > t9) val = t9;
	return val;
}

inline double inlineCompare(const Sequence* p1, const Sequence* p2, int width, int height, int maximumDistanceScore) {
	// x, y:
	// 0, 0
	double totalDistance = getMin(
			PIXEL_DISTANCE(p1, 0 ,0, p2, 0, 0, width),
			PIXEL_DISTANCE(p1, 0 ,0, p2, 1, 0, width),
			PIXEL_DISTANCE(p1, 0 ,0, p2, 0, 1, width),
			PIXEL_DISTANCE(p1, 0 ,0, p2, 1, 1, width));
	// width - 1, 0
	totalDistance += getMin(
			PIXEL_DISTANCE(p1, width - 1, 0, p2, width - 2, 0, width),
			PIXEL_DISTANCE(p1, width - 1, 0, p2, width - 1, 0, width),
			PIXEL_DISTANCE(p1, width - 1, 0, p2, width - 2, 1, width),
			PIXEL_DISTANCE(p1, width - 1, 0, p2, width - 1, 1, width));
	// 0, height - 1
	totalDistance += getMin(
			PIXEL_DISTANCE(p1, 0, height - 1, p2, 0, height - 1, width),
			PIXEL_DISTANCE(p1, 0, height - 1, p2, 1, height - 1, width),
			PIXEL_DISTANCE(p1, 0, height - 1, p2, 0, height - 2, width),
			PIXEL_DISTANCE(p1, 0, height - 1, p2, 1, height - 2, width));
	// width - 1, height - 1
	totalDistance += getMin(
			PIXEL_DISTANCE(p1, width - 1, height - 1, p2, width - 2, height - 1, width),
			PIXEL_DISTANCE(p1, width - 1, height - 1, p2, width - 1, height - 1, width),
			PIXEL_DISTANCE(p1, width - 1, height - 1, p2, width - 2, height - 2, width),
			PIXEL_DISTANCE(p1, width - 1, height - 1, p2, width - 1, height - 2, width));
	// x, 0
	for (int x = 1; x <= width - 2; ++x) {
		totalDistance += getMin(
				PIXEL_DISTANCE(p1, x, 0, p2, x - 1, 0, width),
				PIXEL_DISTANCE(p1, x, 0, p2, x, 0, width),
				PIXEL_DISTANCE(p1, x, 0, p2, x + 1, 0, width),
				PIXEL_DISTANCE(p1, x, 0, p2, x - 1, 1, width),
				PIXEL_DISTANCE(p1, x, 0, p2, x, 1, width),
				PIXEL_DISTANCE(p1, x, 0, p2, x + 1, 1, width));
	}
	// x, height - 1
	for (int x = 1; x <= width - 2; ++x) {
		totalDistance += getMin(
				PIXEL_DISTANCE(p1, x, height - 1, p2, x - 1, height - 1, width),
				PIXEL_DISTANCE(p1, x, height - 1, p2, x, height - 1, width),
				PIXEL_DISTANCE(p1, x, height - 1, p2, x + 1, height - 1, width),
				PIXEL_DISTANCE(p1, x, height - 1, p2, x - 1, height - 2, width),
				PIXEL_DISTANCE(p1, x, height - 1, p2, x, height - 2, width),
				PIXEL_DISTANCE(p1, x, height - 1, p2, x + 1, height - 2, width));
	}
	for (int y = 1; y <= height - 2; ++y) {
		// 0, y
		totalDistance += getMin(
				PIXEL_DISTANCE(p1, 0, y, p2, 0, y - 1, width),
				PIXEL_DISTANCE(p1, 0, y, p2, 1, y - 1, width),
				PIXEL_DISTANCE(p1, 0, y, p2, 0, y, width),
				PIXEL_DISTANCE(p1, 0, y, p2, 1, y, width),
				PIXEL_DISTANCE(p1, 0, y, p2, 0, y + 1, width),
				PIXEL_DISTANCE(p1, 0, y, p2, 1, y + 1, width));
		// width - 1, y
		totalDistance += getMin(
				PIXEL_DISTANCE(p1, width - 1, y, p2, width - 2, y - 1, width),
				PIXEL_DISTANCE(p1, width - 1, y, p2, width - 1, y - 1, width),
				PIXEL_DISTANCE(p1, width - 1, y, p2, width - 2, y, width),
				PIXEL_DISTANCE(p1, width - 1, y, p2, width - 1, y, width),
				PIXEL_DISTANCE(p1, width - 1, y, p2, width - 2, y + 1, width),
				PIXEL_DISTANCE(p1, width - 1, y, p2, width - 1, y + 1, width));
	}
	// x in [1; width - 2], y in [1; height - 2]
	int remainingSize = (width - 2) * (height - 2);
	for (int index = 0; index < remainingSize; ++index) {
		int x = index % (width - 2) + 1;
		int y = index / (width - 2) + 1;
		totalDistance += getMin(
				PIXEL_DISTANCE(p1, x, y, p2, x - 1, y - 1, width),
				PIXEL_DISTANCE(p1, x, y, p2, x, y - 1, width),
				PIXEL_DISTANCE(p1, x, y, p2, x + 1, y - 1, width),
				PIXEL_DISTANCE(p1, x, y, p2, x - 1, y, width),
				PIXEL_DISTANCE(p1, x, y, p2, x, y, width),
				PIXEL_DISTANCE(p1, x, y, p2, x + 1, y, width),
				PIXEL_DISTANCE(p1, x, y, p2, x - 1, y + 1, width),
				PIXEL_DISTANCE(p1, x, y, p2, x, y + 1, width),
				PIXEL_DISTANCE(p1, x, y, p2, x + 1, y + 1, width));
	}
	return (maximumDistanceScore - totalDistance) / maximumDistanceScore;
}

#endif //SIMILIRAPTOR_CORE_HPP
