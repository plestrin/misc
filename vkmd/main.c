#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>

#include <elf.h>

static int read_pgr_hdr(FILE* kcore, Elf64_Phdr** pgr_hdr_buf_ptr, uint32_t* pgr_hdr_buf_len_ptr){
	Elf64_Ehdr hdr;

	fseek(kcore, 0, SEEK_SET);
	if (fread(&hdr, sizeof hdr, 1, kcore) != 1){
		fprintf(stderr, "[-] in %s, unable to read file header\n", __func__);
		return -1;
	}

	if (hdr.e_ehsize != sizeof(Elf64_Ehdr) || hdr.e_phentsize != sizeof(Elf64_Phdr) || !hdr.e_phnum){
		fprintf(stderr, "[-] in %s, basic checks on file header failed\n", __func__);
		return -1;
	}

	if ((*pgr_hdr_buf_ptr = malloc(sizeof(Elf64_Phdr) * hdr.e_phnum)) == NULL){
		fprintf(stderr, "[-] in %s, unable to allocate memory\n", __func__);
		return -1;
	}

	fseek(kcore, hdr.e_phoff, SEEK_SET);
	if (fread(*pgr_hdr_buf_ptr, sizeof(Elf64_Phdr), hdr.e_phnum, kcore) != hdr.e_phnum){
		fprintf(stderr, "[-] in %s, unable to read program headers\n", __func__);
		return -1;
	}

	*pgr_hdr_buf_len_ptr = hdr.e_phnum;

	return 0;
}

static int dump(FILE* kcore, uint64_t offset, uint64_t size){
	uint8_t chunk[512];
	size_t chunk_size;

	if (fseek(kcore, offset, SEEK_SET)){
		fprintf(stderr, "[-] in %s, unable to seek file offset 0x%lx : %u\n", __func__, offset, errno);
		return -1;
	}

	while (size){
		chunk_size = size;
		if (chunk_size > sizeof chunk){
			chunk_size = sizeof chunk;
		}

		if (fread(chunk, chunk_size, 1, kcore) != 1){
			fprintf(stderr, "[-] in %s, unable to read file\n", __func__);
			return -1;
		}

		if (fwrite(chunk, chunk_size, 1, stdout) != 1){
			fprintf(stderr, "[-] in %s, unable to write to stdout\n", __func__);
			return -1;
		}

		size -= chunk_size;
	}

	return 0;
}

static int dump_vkm(FILE* kcore, Elf64_Phdr* pgr_hdr_buf, uint32_t pgr_hdr_buf_len, uint64_t* addr_ptr, uint64_t* size_ptr){
	uint32_t i;
	uint64_t seg_off;
	uint64_t seg_size;

	for (i = 0; i < pgr_hdr_buf_len; i ++){
		if ((pgr_hdr_buf[i].p_vaddr <= *addr_ptr) && (pgr_hdr_buf[i].p_vaddr + pgr_hdr_buf[i].p_memsz) > *addr_ptr){
			seg_off = *addr_ptr - pgr_hdr_buf[i].p_vaddr;
			seg_size = *size_ptr;
			if (seg_off + seg_size > pgr_hdr_buf[i].p_memsz){
				seg_size = pgr_hdr_buf[i].p_memsz - seg_off;
			}

			if (pgr_hdr_buf[i].p_filesz != pgr_hdr_buf[i].p_memsz){
				fprintf(stderr, "[-] in %s, something is off with program header %u, p_filesz != p_memsz\n", __func__, i);
				return -1;
			}

			if (dump(kcore, pgr_hdr_buf[i].p_offset + seg_off, seg_size)){
				fprintf(stderr, "[-] in %s, call to dump(_, 0x%lx, 0x%lx) failed\n", __func__, pgr_hdr_buf[i].p_offset + seg_off, seg_size);
				return -1;
			}

			*addr_ptr += seg_size;
			*size_ptr -= seg_size;

			return 0;
		}
	}

	fprintf(stderr, "[-] in %s, unable to find program header for address 0x%lx\n", __func__, *addr_ptr);
	return -1;
}

int main(int argc, char** argv){
	uint64_t addr;
	uint64_t size;
	FILE* kcore;
	Elf64_Phdr* pgr_hdr_buf = NULL;
	uint32_t pgr_hdr_buf_len;
	int status = EXIT_SUCCESS;

	if (argc != 3){
		fprintf(stderr, "[-] usage : %s addr_hex, size_hex\n", argv[0]);
		return EXIT_FAILURE;
	}

	addr = strtoull(argv[1], NULL, 16);
	size = strtoull(argv[2], NULL, 16);

	if ((kcore = fopen("/proc/kcore", "rb")) == NULL){
		fprintf(stderr, "[-] in %s, unable to open /proc/kcore\n", __func__);
		return EXIT_FAILURE;
	}

	if (read_pgr_hdr(kcore, &pgr_hdr_buf, &pgr_hdr_buf_len)){
		fprintf(stderr, "[-] in %s, unable to read program headers\n", __func__);
		status = EXIT_FAILURE;
	}
	else {
		while (size){
			if (dump_vkm(kcore, pgr_hdr_buf, pgr_hdr_buf_len, &addr, &size)){
				fprintf(stderr, "[-] in %s, failed to dump kernel virtual memory\n", __func__);
				status = EXIT_FAILURE;
				break;
			}
		}
	}

	fclose(kcore);

	free(pgr_hdr_buf);

	return status;
}
