#ifndef SIMILIRAPTOR_HPP
#define SIMILIRAPTOR_HPP

#include "core.hpp"

extern "C" {
	double compareSimilarSequences(const Sequence* p1, const Sequence* p2, int width, int height, int maximumDistanceScore);
	double countSimilarPixels(const Sequence* p1, const Sequence* p2, int width, int height, int maximumDistanceScore);
};

#endif
