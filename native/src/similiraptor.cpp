#include "similiraptor.hpp"

double compareSimilarSequences(const Sequence* p1, const Sequence* p2, int width, int height, int maximumDistanceScore) {
	return inlineCompare(p1, p2, width, height, maximumDistanceScore);
}

double countSimilarPixels(const Sequence* p1, const Sequence* p2, int width, int height, int maximumPixelDistance) {
	return inlineCount(p1, p2, width, height, maximumPixelDistance);
}
