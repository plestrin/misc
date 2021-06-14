CC := gcc
CFLAGS := -Wall -Wextra -O3

all: vkmd

vkmd: main.o
	$(CC) -o $@ $^

%.o: %.c
	$(CC) -c -o $@ $(CFLAGS) $<

clean:
	@ rm -f *.o
	@ rm -f vkmd
