// Standard declarations assumed transitively by the 2023 upstream sources.
#pragma once
#include <algorithm>
#include <array>
#include <cfloat>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
// Keep upstream printf diagnostics out of the binary RGB frame stream.
#define PRINT(...) do { std::fprintf(stderr,__VA_ARGS__); std::fputc('\n',stderr); } while(0)
