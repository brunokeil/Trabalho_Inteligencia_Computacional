CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -pedantic
SRC      := $(wildcard src/*.cpp)
OBJ      := $(SRC:src/%.cpp=build/%.o)
BIN      := alocacao

all: $(BIN)

$(BIN): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^

build/%.o: src/%.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -c -o $@ $<

build:
	mkdir -p build

clean:
	rm -rf build $(BIN)

.PHONY: all clean run-all

run-all: $(BIN)
	python3 scripts/preparar_instancias.py
	python3 scripts/executar_todas.py --instancias-dir instances/preparadas -k 1 --runs 30 --out resultados/final_vnd

report:
	cd docs && pdflatex -interaction=nonstopmode -halt-on-error relatorio.tex
	cd docs && pdflatex -interaction=nonstopmode -halt-on-error relatorio.tex
.PHONY: report

CORE := $(filter-out src/main.cpp,$(SRC))
build/test_parser: tests/parser.cpp src/instancia.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -Isrc tests/parser.cpp src/instancia.cpp -o $@
build/test_core: tests/core.cpp $(CORE) $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -Isrc tests/core.cpp $(CORE) -o $@
test: all build/test_parser build/test_core
	./build/test_parser
	./build/test_core
	python3 -m unittest discover -s tests -p 'test_*.py' -v
.PHONY: test

SANFLAGS := -std=c++17 -O1 -g -Wall -Wextra -fsanitize=address,undefined -fno-omit-frame-pointer
build/test_core_san: tests/core.cpp $(CORE) $(wildcard src/*.hpp) | build
	$(CXX) $(SANFLAGS) -Isrc tests/core.cpp $(CORE) -o $@
build/alocacao_san: $(SRC) $(wildcard src/*.hpp) | build
	$(CXX) $(SANFLAGS) $(SRC) -o $@
test-sanitize: build/test_core_san build/alocacao_san
	./build/test_core_san
	DCC136_TEST_BIN="$(CURDIR)/build/alocacao_san" python3 -m unittest discover -s tests -p 'test_*.py' -v
.PHONY: test-sanitize
