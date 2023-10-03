//
// Created by notoraptor-desktop on 25/09/2023.
//

#ifndef SIMILIRAPTOR_CORE_HPP
#define SIMILIRAPTOR_CORE_HPP

#include <cstdlib>
#include <algorithm>

struct Sequence {
	int* r; // red
	int* g; // green
	int* b; // blue
};

constexpr int SIMPLE_MAX_PIXEL_DISTANCE = 255 * 3;
constexpr int V = SIMPLE_MAX_PIXEL_DISTANCE;

inline double exaggerate(int k, double x) {
	return (k * V + V) * x / (k * x + V);
}

inline double pixelDistance(const Sequence* p1, int indexP1, const Sequence* p2, int indexP2, int k) {
	return exaggerate(
		k, std::abs(p1->r[indexP1] - p2->r[indexP2]) + std::abs(p1->g[indexP1] - p2->g[indexP2]) + std::abs(p1->b[indexP1] - p2->b[indexP2])
	);
}

#define PIXEL_DISTANCE_KN(p1, x, y, p2, localX, localY, width) pixelDistance(p1, (x) + (y) * (width), p2, (localX) + (localY) * (width), 4)
#define PIXEL_DISTANCE_K2(p1, x, y, p2, localX, localY, width) pixelDistance(p1, (x) + (y) * (width), p2, (localX) + (localY) * (width), 2)
#define PIXEL_DISTANCE_K0(p1, x, y, p2, localX, localY, width) pixelDistance(p1, (x) + (y) * (width), p2, (localX) + (localY) * (width), 0)

inline double inlineCompare(const Sequence* p1, const Sequence* p2, int width, int height, int maximumDistanceScore) {
	int r = 1;
	double totalDistance = 0;
	for (int x = 0; x < width; ++x) {
		for (int y = 0; y < height; ++y) {
			double minDistance = SIMPLE_MAX_PIXEL_DISTANCE;
			for (int i = std::max(0, x - r); i < std::min(x + r + 1, width); ++i) {
				for (int j = std::max(0, y - r); j < std::min(y + r + 1, height); ++j) {
					minDistance = std::min(minDistance, PIXEL_DISTANCE_KN(p1, x, y, p2, i, j, width));
				}
			}
			totalDistance += minDistance;
		}
	}
	return (maximumDistanceScore - totalDistance) / maximumDistanceScore;
}

inline double inlineCount(const Sequence* p1, const Sequence* p2, int width, int height, int maximumPixelDistance) {
	int r = 2;
	double total = 0;
	for (int x = 0; x < width; ++x) {
		for (int y = 0; y < height; ++y) {
			double minDistance = SIMPLE_MAX_PIXEL_DISTANCE;
			for (int i = std::max(0, x - r); i < std::min(x + r + 1, width); ++i) {
				for (int j = std::max(0, y - r); j < std::min(y + r + 1, height); ++j) {
					minDistance = std::min(minDistance, PIXEL_DISTANCE_K0(p1, x, y, p2, i, j, width));
				}
			}
			total += minDistance <= maximumPixelDistance;
		}
	}
	return total;
}

#endif //SIMILIRAPTOR_CORE_HPP
