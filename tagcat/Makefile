TARGET = tagcat
CC = gcc
CFLAGS = -Wall -pedantic -std=gnu11 -O2 `pkg-config --cflags libnfc`
LIBS = `pkg-config --libs libnfc`

.PHONY: all clean

all: $(TARGET)

clean:
	-rm -f $(TARGET) main.o

main.o: main.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): main.o
	$(CC) main.o $(LIBS) -o $@
